from datetime import timedelta
import os

from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import Article, Category, Project, ServiceGroup, ServiceLink


class Command(BaseCommand):
    help = 'Create starter articles and projects; safe to run more than once.'

    def handle(self, *args, **options):
        categories = {
            name: Category.objects.get_or_create(name=name, defaults={'slug': slug})[0]
            for name, slug in [('开发', 'development'), ('工具', 'tools'), ('生活', 'life')]
        }
        now = timezone.now()
        articles = [
            ('docker-django-vue', '用 Docker 部署 Django + Vue 的完整记录', '开发', '从本地开发到公网部署，把前后端、数据库和反向代理放进一套清晰的发布流程。', '把项目真正放到服务器上之后，才发现部署本身也是产品的一部分。环境一致、更新简单、出问题时能快速回退，这些事情比多加一个功能更让人安心。\n\n## 先把服务边界理清楚\n\n前端负责展示，Django 提供 API，数据库只允许应用内部访问。反向代理统一处理 HTTPS 和请求转发，日志也集中从容器输出。\n\n## 发布前留好退路\n\n上线前备份数据库，镜像保留上一个可用版本。改动越小、回滚越容易，维护博客就越轻松。'),
            ('siyuan-to-blog', '思源笔记自动同步到博客的三种思路', '工具', '整理从手动导出、Git 同步到 API 发布的几种方式，找到适合自己的写作节奏。', '笔记是写作的起点，博客是整理之后的出口。同步流程越顺手，越容易保持稳定更新。\n\n## 先从 Markdown 开始\n\n如果文章主要是文字和图片，导出 Markdown 后提交到 Git 是最简单可靠的方式。等内容多了，再考虑自动发布和元数据转换。'),
            ('year-notes', '我的 2024 年终总结', '生活', '一些关于工作、学习和日常生活的记录，也给新的一年留几个小目标。', '这一年做了不少计划，也有一些事情是在路上才慢慢想明白的。回头看，留下来的不只是结果，还有重新开始的勇气。\n\n## 把注意力放回日常\n\n少一点宏大的目标，多一点能持续的小习惯。阅读、运动、写作，做得不多，但希望一直做下去。'),
            ('vim-setup', 'Vim 配置从入门到放弃再到真香', '开发', '从一份很长的配置文件开始，最后留下的反而只有几个真正高频的快捷键。', '折腾编辑器很容易变成另一种拖延。后来我把配置删到只剩日常需要的部分，反而开始享受 Vim 的轻快。\n\n## 先记住移动和搜索\n\n熟悉基本移动、搜索和文本对象，比装很多插件更有用。等遇到重复的操作，再给它一个快捷键。'),
            ('starting-again', '为什么我又开始写博客了', '生活', '给自己的想法留一个可以回来的地方，也把走过的路慢慢写下来。', '很多想法当时觉得记得住，过几个月就只剩下模糊的印象。于是想重新开始写博客，把学到的东西和生活里的片段留在这里。\n\n不追求更新频率，只希望每次写完都比开始时更清楚一点。'),
        ]
        for index, (slug, title, category, excerpt, content) in enumerate(articles):
            Article.objects.get_or_create(slug=slug, defaults={
                'title': title, 'category': categories[category], 'excerpt': excerpt,
                'content': content, 'published': True, 'published_at': now - timedelta(days=index * 5),
            })
        Project.objects.get_or_create(title='个人博客', defaults={
            'description': '一个安静写作、认真记录的地方。',
            'technologies': ['Vue', 'Django', 'PostgreSQL'], 'featured': True, 'sort_order': 1,
        })
        Project.objects.get_or_create(title='家庭数据中心', defaults={
            'description': '用一台小主机整理文件与日常服务。',
            'technologies': ['Linux', 'Docker', 'NAS'], 'featured': True, 'sort_order': 2,
        })
        group, _ = ServiceGroup.objects.get_or_create(name='家庭服务', defaults={'sort_order': 1})
        ServiceLink.objects.get_or_create(group=group, name='NAS', defaults={
            'description': '家庭文件与照片存储',
            'url': os.getenv('NAS_URL', ''),
            'icon': '⌂',
            'sort_order': 1,
            'enabled': True,
        })
        self.stdout.write(self.style.SUCCESS('示例文章、项目和 NAS 入口已准备好。未配置 NAS_URL 时，请到 Django 后台填写实际地址。'))
