from django.contrib import admin

from .models import Article, Category, Project, ServiceGroup, ServiceLink, SiyuanSource
from .siyuan import SiyuanAPIError, sync_source


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'published', 'published_at', 'updated_at']
    list_filter = ['published', 'category']
    search_fields = ['title', 'excerpt', 'content']
    date_hierarchy = 'published_at'
    list_editable = ['published']
    fieldsets = [
        (None, {'fields': ('title', 'slug', 'excerpt', 'content')}),
        ('发布设置', {'fields': ('category', 'published', 'published_at')}),
    ]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'featured', 'sort_order']
    list_editable = ['featured', 'sort_order']


class ServiceLinkInline(admin.TabularInline):
    model = ServiceLink
    extra = 0


@admin.register(ServiceGroup)
class ServiceGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order']
    list_editable = ['sort_order']
    inlines = [ServiceLinkInline]


@admin.register(ServiceLink)
class ServiceLinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'group', 'url', 'enabled', 'sort_order']
    list_filter = ['group', 'enabled']
    list_editable = ['enabled', 'sort_order']


@admin.register(SiyuanSource)
class SiyuanSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_url', 'notebook_id', 'folder_path', 'enabled', 'last_synced_at', 'last_sync_summary']
    list_filter = ['enabled']
    search_fields = ['name', 'notebook_id', 'folder_path']
    list_editable = ['enabled']
    readonly_fields = ['last_synced_at', 'last_sync_summary']
    actions = ['sync_selected_sources']
    fields = ['name', 'base_url', 'notebook_id', 'folder_path', 'enabled', 'last_synced_at', 'last_sync_summary']

    @admin.action(description='同步选中的思源文件夹到文章草稿')
    def sync_selected_sources(self, request, queryset):
        total_created = total_updated = 0
        for source in queryset:
            if not source.enabled:
                self.message_user(request, f'已跳过未启用的来源：{source.name}', level='WARNING')
                continue
            try:
                created, updated = sync_source(source)
                total_created += created
                total_updated += updated
            except SiyuanAPIError as exc:
                self.message_user(request, f'{source.name} 同步失败：{exc}', level='ERROR')
        if total_created or total_updated:
            self.message_user(request, f'同步完成：新增 {total_created} 篇，更新 {total_updated} 篇。新文章默认隐藏，已有文章的公开状态保持不变。')


admin.site.site_header = '个人博客管理'
admin.site.site_title = '个人博客管理'
admin.site.index_title = '内容和私人服务'
