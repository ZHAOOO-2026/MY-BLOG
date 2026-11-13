import json
from pathlib import Path

from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.cache import cache
from django.http import FileResponse, Http404, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.views.decorators.http import require_GET, require_POST
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article, Project, ServiceGroup
from .serializers import ArticleDetailSerializer, ArticleListSerializer, ProjectSerializer, ServiceGroupSerializer


@require_GET
def siyuan_media(request, source_id, filename):
    article = Article.objects.filter(source_id=source_id, published=True).first()
    if not article:
        raise Http404
    root = (Path(settings.MEDIA_ROOT) / 'siyuan' / source_id).resolve()
    candidate = (root / filename).resolve()
    if not candidate.is_relative_to(root) or not candidate.is_file():
        raise Http404
    response = FileResponse(candidate.open('rb'))
    response['Cache-Control'] = 'private, no-store'
    return response


@require_GET
@ensure_csrf_cookie
def csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})


@require_GET
@ensure_csrf_cookie
def current_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required.'}, status=401)
    return JsonResponse({'username': request.user.get_username(), 'name': request.user.get_full_name() or request.user.get_username()})


@require_POST
@csrf_protect
def sign_in(request):
    # DRF's anonymous login views do not enforce CSRF by default, so this endpoint
    # uses Django's csrf_protect explicitly and also applies a small IP throttle.
    throttle_key = f'blog-login:{request.META.get("REMOTE_ADDR", "unknown")}'
    attempts = cache.get(throttle_key, 0)
    if attempts >= 10:
        return JsonResponse({'detail': '登录尝试过多，请 15 分钟后再试。'}, status=429)
    try:
        data = json.loads(request.body or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'detail': '请求内容格式错误。'}, status=400)
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', ''))
    user = authenticate(request, username=username, password=password)
    if user is None or not user.is_active or not user.is_staff:
        cache.set(throttle_key, attempts + 1, timeout=900)
        return JsonResponse({'detail': '账号或密码不正确。'}, status=400)
    cache.delete(throttle_key)
    login(request, user)
    request.session.cycle_key()
    return JsonResponse({'username': user.get_username(), 'name': user.get_full_name() or user.get_username()})


@require_POST
@csrf_protect
def sign_out(request):
    logout(request)
    return JsonResponse({'ok': True})


class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        from django.utils import timezone
        return Article.objects.filter(published=True, published_at__lte=timezone.now()).select_related('category')


class ArticleDetailView(generics.RetrieveAPIView):
    serializer_class = ArticleDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        from django.utils import timezone
        return Article.objects.filter(published=True, published_at__lte=timezone.now()).select_related('category')


class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Project.objects.all()


class PortalLinksView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        groups = ServiceGroup.objects.filter(items__enabled=True).distinct().prefetch_related('items')
        return Response({'groups': ServiceGroupSerializer(groups, many=True).data})
