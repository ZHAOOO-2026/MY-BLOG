# 个人博客 + 私人服务门户

Vue 3 + Vite 前端，Django REST Framework 后端，PostgreSQL 数据库。博客首页、文章、项目和关于页公开访问；服务门户需要管理员账号登录。网页不提供注册入口。

## 本地开发

需要 Node.js 22+ 和 Python 3.12+。

```powershell
# 终端 1：启动后端
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

```powershell
# 终端 2：启动前端
npm install
npm run dev
```

打开 Vite 显示的地址（通常是 `http://localhost:5173`）。开发时 `/api` 会代理到 Django 的 `127.0.0.1:8000`。

## 内容后台

访问 `http://localhost:8000/admin/`，用 `createsuperuser` 创建的管理员登录。

- 在“文章”中新建或编辑文章，正文支持 Markdown。勾选“公开发布”才会出现在博客。
- 文章列表可以直接切换“公开发布”勾选框；取消勾选后，公开列表和文章详情 API 都不再返回该文章。
- 在“思源同步来源”中新建来源，填写思源 API 地址、笔记本 ID 和文件夹路径（例如 `/博客`）。先在服务器 `.env` 设置 `SIYUAN_API_TOKEN` 并重启 API，再在来源列表勾选来源，通过“同步选中的思源文件夹到文章草稿”操作导入。新文章默认隐藏；重复同步会更新正文和标题，但保留你在后台设置的公开状态。
- 思源 API 必须能从博客服务器访问。不要为了同步把思源 API 直接暴露到公网；建议使用同一内网/VPN/安全隧道。Markdown 图片附件会复制到博客媒体目录，只有文章公开后对应图片才可访问。
- 在“私人服务分组”中管理鲁班猫、NAS 等入口；示例初始化数据会创建一张 NAS 卡片。首次运行时地址为空，到后台填写实际地址后即可点击打开。
- 在“项目”中维护公开项目；“首页展示”可控制首页精选。

## Docker Compose

在项目根目录创建 `.env`：

```powershell
Copy-Item .env.example .env
```

修改 `.env` 中的 `DJANGO_SECRET_KEY`、`DB_PASSWORD`、域名和 CSRF 来源。生产环境要先为域名配置 HTTPS，再设置 `DJANGO_SECURE_COOKIES=1`。

```powershell
docker compose up -d --build
docker compose exec api python manage.py createsuperuser
```

容器入口默认绑定 `127.0.0.1:18081`，PostgreSQL 数据持久化在 `./data/postgres`。部署到公网服务器 `/opt/personal-blog` 时，站点容器不会占用服务器现有的 80/443 端口；让服务器已有的 Nginx/Caddy 为域名终止 HTTPS，并反向代理到 `127.0.0.1:18081`。

常用运维命令：

```sh
docker compose ps
docker compose logs -f api
docker compose restart api
docker compose down       # 保留 ./data/postgres
```

数据库备份示例：

```sh
docker compose exec -T db pg_dump -U "$DB_USER" "$DB_NAME" > backup.sql
```

把备份复制到 NAS 或异地存储；不要只把唯一备份留在同一台服务器上。

## 接口

- `GET /api/articles/`：公开已发布文章列表
- `GET /api/articles/{slug}/`：公开已发布文章详情
- `GET /api/projects/`：公开项目
- `GET /api/auth/csrf/`、`GET /api/auth/me/`、`POST /api/auth/login/`、`POST /api/auth/logout/`
- `GET /api/portal/links/`：管理员登录后返回私人服务链接

服务链接 API 受 Django session 认证保护，登录和注销使用 CSRF。服务门户保护的是入口清单；NAS、路由器和设备管理服务本身也应限制在家庭网络或 VPN 内访问。
