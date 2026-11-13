import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, unique=True, verbose_name='名称')),
                ('slug', models.SlugField(blank=True, max_length=60, unique=True, verbose_name='标识')),
            ],
            options={'verbose_name': '分类', 'verbose_name_plural': '分类', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='名称')),
                ('description', models.CharField(max_length=400, verbose_name='简介')),
                ('url', models.URLField(blank=True, verbose_name='项目链接')),
                ('technologies', models.JSONField(blank=True, default=list, verbose_name='技术标签')),
                ('featured', models.BooleanField(default=True, verbose_name='首页展示')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='排序')),
            ],
            options={'verbose_name': '项目', 'verbose_name_plural': '项目', 'ordering': ['sort_order', 'id']},
        ),
        migrations.CreateModel(
            name='ServiceGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='分组名称')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='排序')),
            ],
            options={'verbose_name': '私人服务分组', 'verbose_name_plural': '私人服务分组', 'ordering': ['sort_order', 'id']},
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=180, verbose_name='标题')),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True, verbose_name='URL 标识')),
                ('excerpt', models.CharField(blank=True, max_length=300, verbose_name='摘要')),
                ('content', models.TextField(verbose_name='正文')),
                ('published', models.BooleanField(default=False, verbose_name='公开发布')),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='发布时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to='blog.category', verbose_name='分类')),
            ],
            options={'verbose_name': '文章', 'verbose_name_plural': '文章', 'ordering': ['-published_at', '-id']},
        ),
        migrations.CreateModel(
            name='ServiceLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='名称')),
                ('description', models.CharField(blank=True, max_length=160, verbose_name='说明')),
                ('url', models.URLField(blank=True, verbose_name='服务地址')),
                ('icon', models.CharField(blank=True, max_length=8, verbose_name='图标字符')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='排序')),
                ('enabled', models.BooleanField(default=True, verbose_name='显示')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='blog.servicegroup', verbose_name='所属分组')),
            ],
            options={'verbose_name': '私人服务链接', 'verbose_name_plural': '私人服务链接', 'ordering': ['sort_order', 'id']},
        ),
    ]
