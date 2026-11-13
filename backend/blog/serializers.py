from rest_framework import serializers

from .models import Article, Project, ServiceGroup, ServiceLink


class ArticleListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    read_time = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['slug', 'title', 'excerpt', 'category', 'published_at', 'read_time']

    def get_read_time(self, obj):
        words = len(obj.content)
        return f'{max(1, (words + 399) // 400)} 分钟'

    def get_category(self, obj):
        return obj.category.name if obj.category_id else '未分类'


class ArticleDetailSerializer(ArticleListSerializer):
    class Meta(ArticleListSerializer.Meta):
        fields = ArticleListSerializer.Meta.fields + ['content']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'url', 'technologies', 'featured']


class ServiceLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLink
        fields = ['name', 'description', 'url', 'icon']


class ServiceGroupSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = ServiceGroup
        fields = ['name', 'items']

    def get_items(self, obj):
        return ServiceLinkSerializer(obj.items.filter(enabled=True), many=True).data
