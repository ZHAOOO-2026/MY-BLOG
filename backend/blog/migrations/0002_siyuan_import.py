from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('blog', '0001_initial')]

    operations = [
        migrations.AddField(
            model_name='article',
            name='source_id',
            field=models.CharField(blank=True, editable=False, max_length=80, null=True, unique=True, verbose_name='思源文档 ID'),
        ),
        migrations.AddField(
            model_name='article',
            name='source_path',
            field=models.CharField(blank=True, editable=False, max_length=500, verbose_name='思源文档路径'),
        ),
        migrations.CreateModel(
            name='SiyuanSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='思源笔记', max_length=80, verbose_name='来源名称')),
                ('base_url', models.URLField(help_text='例如 http://192.168.1.20:6806，不要填 /api/... ', verbose_name='思源 API 地址')),
                ('notebook_id', models.CharField(max_length=80, verbose_name='笔记本 ID')),
                ('folder_path', models.CharField(help_text='思源中的路径，例如 /博客；填 / 表示整个笔记本', max_length=500, verbose_name='文件夹路径')),
                ('enabled', models.BooleanField(default=True, verbose_name='启用同步')),
                ('last_synced_at', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='上次同步时间')),
                ('last_sync_summary', models.CharField(blank=True, editable=False, max_length=240, verbose_name='上次同步结果')),
            ],
            options={
                'verbose_name': '思源同步来源',
                'verbose_name_plural': '思源同步来源',
            },
        ),
    ]
