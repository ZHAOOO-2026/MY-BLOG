from django.urls import path

from .views import ArticleDetailView, ArticleListView, PortalLinksView, ProjectListView, current_user, csrf_token, sign_in, sign_out


urlpatterns = [
    path('auth/csrf/', csrf_token, name='csrf-token'),
    path('auth/me/', current_user, name='current-user'),
    path('auth/login/', sign_in, name='login'),
    path('auth/logout/', sign_out, name='logout'),
    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article-detail'),
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('portal/links/', PortalLinksView.as_view(), name='portal-links'),
]
