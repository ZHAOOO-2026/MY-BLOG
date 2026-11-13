import json
import re
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from .models import Article, Category


class SiyuanAPIError(Exception):
    pass


class SiyuanClient:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.token = token

    def post(self, endpoint, payload):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        request = Request(
            f'{self.base_url}/api/{endpoint}',
            data=body,
            headers={
                'Authorization': f'Token {self.token}',
                'Content-Type': 'application/json',
            },
            method='POST',
        )
        try:
            with urlopen(request, timeout=20) as response:
                result = json.loads(response.read().decode('utf-8'))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise SiyuanAPIError(f'思源接口请求失败：{exc}') from exc
        if result.get('code') != 0:
            raise SiyuanAPIError(result.get('msg') or f'思源接口 {endpoint} 返回错误')
        return result.get('data')

    def get_asset(self, asset_path):
        body = json.dumps({'path': f'/data/{asset_path}'}).encode('utf-8')
        request = Request(
            f'{self.base_url}/api/file/getFile',
            data=body,
            headers={
                'Authorization': f'Token {self.token}',
                'Content-Type': 'application/json',
            },
            method='POST',
        )
        try:
            with urlopen(request, timeout=20) as response:
                content = response.read()
                if 'application/json' in response.headers.get('Content-Type', ''):
                    detail = json.loads(content.decode('utf-8'))
                    raise SiyuanAPIError(detail.get('msg') or f'思源附件读取失败：{asset_path}')
                return content
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise SiyuanAPIError(f'思源附件请求失败：{exc}') from exc


def _tree_ids(nodes):
    for node in nodes or []:
        if not isinstance(node, dict) or not node.get('id'):
            continue
        yield node['id']
        yield from _tree_ids(node.get('children'))


def _excerpt(markdown):
    text = re.sub(r'```.*?```', ' ', markdown, flags=re.S)
    text = re.sub(r'!?(\[[^\]]*\])\([^)]*\)', r'\1', text)
    text = re.sub(r'[#>*_`~|\[\]()]+', ' ', text)
    return ' '.join(text.split())[:300]


_ASSET_LINK = re.compile(r'(?P<lead>!?\[[^\]]*\]\()(?P<path>(?:\.\./)*assets/[^)\s]+)(?P<tail>\))')


def _copy_assets(client, markdown, document_id):
    media_dir = Path(settings.MEDIA_ROOT) / 'siyuan' / document_id
    media_prefix = f'/media/siyuan/{quote(document_id)}/'
    failures = 0

    def replace(match):
        nonlocal failures
        asset_path = match.group('path')
        relative_path = asset_path.split('assets/', 1)[1]
        parts = PurePosixPath(relative_path).parts
        if not parts or any(part in {'', '.', '..'} for part in parts):
            failures += 1
            return match.group(0)
        safe_path = '/'.join(parts)
        destination = media_dir.joinpath(*parts)
        try:
            if not destination.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(client.get_asset(f'assets/{safe_path}'))
        except (OSError, SiyuanAPIError):
            failures += 1
            return match.group(0)
        return f"{match.group('lead')}{media_prefix}{quote(safe_path, safe='/')}{match.group('tail')}"

    return _ASSET_LINK.sub(replace, markdown), failures


def sync_source(source):
    token = getattr(settings, 'SIYUAN_API_TOKEN', '')
    if not token:
        raise SiyuanAPIError('服务器尚未配置 SIYUAN_API_TOKEN。请将思源 API Token 配置到服务器 .env。')
    client = SiyuanClient(source.base_url, token)

    # Resolve the configured human-readable folder path, then walk the
    # document tree and export each document as Markdown.
    folder_path = source.folder_path.strip() or '/'
    if folder_path == '/':
        storage_path = '/'
    else:
        folder_ids = client.post('filetree/getIDsByHPath', {
            'notebook': source.notebook_id,
            'path': folder_path,
        })
        if not folder_ids:
            raise SiyuanAPIError('没有找到这个笔记本路径，请检查笔记本 ID 和文件夹路径。')
        folder_storage = client.post('filetree/getPathByID', {'id': folder_ids[0]})
        storage_path = folder_storage['path']
    tree = client.post('filetree/listDocTree', {
        'notebook': source.notebook_id,
        'path': storage_path,
        'sortMode': 0,
        'flashcard': False,
        'showHidden': False,
        'maxListCount': 10000,
    })
    document_ids = list(_tree_ids(tree))

    category, _ = Category.objects.get_or_create(name='思源笔记')
    created = updated = asset_failures = 0
    for document_id in document_ids:
        exported = client.post('export/exportMdContent', {'id': document_id})
        markdown, failed_assets = _copy_assets(client, exported.get('content', '').strip(), document_id)
        asset_failures += failed_assets
        path = exported.get('hPath', source.folder_path)
        title = path.rstrip('/').split('/')[-1] or '未命名文档'
        if not markdown:
            continue

        with transaction.atomic():
            article = Article.objects.filter(source_id=document_id).first()
            if article:
                article.title = title[:180]
                article.content = markdown
                article.excerpt = _excerpt(markdown)
                article.source_path = path
                # Keep the visibility state and any category chosen in admin.
                article.save(update_fields=['title', 'content', 'excerpt', 'source_path', 'updated_at'])
                updated += 1
                continue

            base_slug = slugify(title, allow_unicode=True)[:160] or 'siyuan-note'
            slug = f'{base_slug}-sy-{document_id[-12:]}'
            Article.objects.create(
                title=title[:180],
                slug=slug,
                excerpt=_excerpt(markdown),
                content=markdown,
                category=category,
                published=False,
                source_id=document_id,
                source_path=path,
            )
            created += 1

    source.last_synced_at = timezone.now()
    source.last_sync_summary = f'完成：新增 {created} 篇，更新 {updated} 篇，附件失败 {asset_failures} 个'
    source.save(update_fields=['last_synced_at', 'last_sync_summary'])
    return created, updated
