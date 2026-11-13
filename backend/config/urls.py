from django.contrib import admin
from django.urls import include, path

from blog.views import siyuan_media


urlpatterns = [
    path('admin/', admin.site.urls),
    path('media/siyuan/<str:source_id>/<path:filename>', siyuan_media, name='siyuan-media'),
    path('api/', include('blog.urls')),
]
