from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField('名称', max_length=40, unique=True)
    slug = models.SlugField('标识', max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = '分类'
        verbose_name_plural = '分类'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True) or f'category-{self.pk or "new"}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField('标题', max_length=180)
    slug = models.SlugField('URL 标识', max_length=200, unique=True, blank=True)
    excerpt = models.CharField('摘要', max_length=300, blank=True)
    content = models.TextField('正文')
    source_id = models.CharField('思源文档 ID', max_length=80, unique=True, null=True, blank=True, editable=False)
    source_path = models.CharField('思源文档路径', max_length=500, blank=True, editable=False)
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    published = models.BooleanField('公开发布', default=False)
    published_at = models.DateTimeField('发布时间', default=timezone.now)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['-published_at', '-id']
        verbose_name = '文章'
        verbose_name_plural = '文章'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) or f'article-{timezone.now():%Y%m%d%H%M%S}'
        super().save(*args, **kwargs)


class SiyuanSource(models.Model):
    name = models.CharField('来源名称', max_length=80, default='思源笔记')
    base_url = models.URLField('思源 API 地址', help_text='例如 http://192.168.1.20:6806，不要填 /api/...')
    notebook_id = models.CharField('笔记本 ID', max_length=80)
    folder_path = models.CharField('文件夹路径', max_length=500, help_text='思源中的路径，例如 /博客；填 / 表示整个笔记本')
    enabled = models.BooleanField('启用同步', default=True)
    last_synced_at = models.DateTimeField('上次同步时间', null=True, blank=True, editable=False)
    last_sync_summary = models.CharField('上次同步结果', max_length=240, blank=True, editable=False)

    class Meta:
        verbose_name = '思源同步来源'
        verbose_name_plural = '思源同步来源'

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField('名称', max_length=120)
    description = models.CharField('简介', max_length=400)
    url = models.URLField('项目链接', blank=True)
    technologies = models.JSONField('技术标签', default=list, blank=True)
    featured = models.BooleanField('首页展示', default=True)
    sort_order = models.PositiveIntegerField('排序', default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = '项目'
        verbose_name_plural = '项目'

    def __str__(self):
        return self.title


class ServiceGroup(models.Model):
    name = models.CharField('分组名称', max_length=80)
    sort_order = models.PositiveIntegerField('排序', default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = '私人服务分组'
        verbose_name_plural = '私人服务分组'

    def __str__(self):
        return self.name


class ServiceLink(models.Model):
    group = models.ForeignKey(ServiceGroup, verbose_name='所属分组', on_delete=models.CASCADE, related_name='items')
    name = models.CharField('名称', max_length=80)
    description = models.CharField('说明', max_length=160, blank=True)
    url = models.URLField('服务地址', blank=True)
    icon = models.CharField('图标字符', max_length=8, blank=True)
    sort_order = models.PositiveIntegerField('排序', default=0)
    enabled = models.BooleanField('显示', default=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = '私人服务链接'
        verbose_name_plural = '私人服务链接'

    def __str__(self):
        return self.name
