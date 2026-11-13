<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MarkdownIt from 'markdown-it'

const route = useRoute()
const router = useRouter()
const isDark = ref(document.documentElement.classList.contains('dark'))
const selectedTag = ref('全部')
const isAuthenticated = ref(false)
const portalLoading = ref(false)
const loginLoading = ref(false)
const loginError = ref('')
const loginForm = ref({ username: '', password: '' })
const portalUser = ref('')
const serviceGroups = ref([])
const projects = ref([])
const activeArticle = ref(null)
const markdownRenderer = new MarkdownIt({ html: false, linkify: true, breaks: false })

const articles = ref([
  {
    slug: 'docker-django-vue',
    date: '2025-01-15',
    title: '用 Docker 部署 Django + Vue 的完整记录',
    category: '开发',
    readTime: '8 分钟',
    excerpt: '从本地开发到公网部署，把前后端、数据库和反向代理放进一套清晰的发布流程。',
    content: [
      { type: 'p', text: '把项目真正放到服务器上之后，才发现部署本身也是产品的一部分。环境一致、更新简单、出问题时能快速回退，这些事情比多加一个功能更让人安心。' },
      { type: 'h2', text: '先把服务边界理清楚' },
      { type: 'p', text: '前端负责展示，Django 提供 API，数据库只允许应用内部访问。反向代理统一处理 HTTPS 和请求转发，日志也集中从容器输出。' },
      { type: 'code', text: 'docker compose up -d --build' },
      { type: 'p', text: '个人项目不用一开始就做复杂的集群。把配置、数据卷和备份规划好，一台服务器也能运行得很稳。' },
      { type: 'h2', text: '发布前留好退路' },
      { type: 'p', text: '上线前备份数据库，镜像保留上一个可用版本。改动越小、回滚越容易，维护博客就越轻松。' },
    ],
  },
  {
    slug: 'siyuan-to-blog',
    date: '2025-01-10',
    title: '思源笔记自动同步到博客的三种思路',
    category: '工具',
    readTime: '6 分钟',
    excerpt: '整理从手动导出、Git 同步到 API 发布的几种方式，找到适合自己的写作节奏。',
    content: [
      { type: 'p', text: '笔记是写作的起点，博客是整理之后的出口。同步流程越顺手，越容易保持稳定更新。' },
      { type: 'h2', text: '先从 Markdown 开始' },
      { type: 'p', text: '如果文章主要是文字和图片，导出 Markdown 后提交到 Git 是最简单可靠的方式。等内容多了，再考虑自动发布和元数据转换。' },
      { type: 'p', text: '工具的价值是减少重复劳动，而不是让流程变得更复杂。' },
    ],
  },
  {
    slug: 'year-notes',
    date: '2024-12-31',
    title: '我的 2024 年终总结',
    category: '生活',
    readTime: '5 分钟',
    excerpt: '一些关于工作、学习和日常生活的记录，也给新的一年留几个小目标。',
    content: [
      { type: 'p', text: '这一年做了不少计划，也有一些事情是在路上才慢慢想明白的。回头看，留下来的不只是结果，还有重新开始的勇气。' },
      { type: 'h2', text: '把注意力放回日常' },
      { type: 'p', text: '少一点宏大的目标，多一点能持续的小习惯。阅读、运动、写作，做得不多，但希望一直做下去。' },
    ],
  },
  {
    slug: 'vim-setup',
    date: '2024-12-20',
    title: 'Vim 配置从入门到放弃再到真香',
    category: '开发',
    readTime: '7 分钟',
    excerpt: '从一份很长的配置文件开始，最后留下的反而只有几个真正高频的快捷键。',
    content: [
      { type: 'p', text: '折腾编辑器很容易变成另一种拖延。后来我把配置删到只剩日常需要的部分，反而开始享受 Vim 的轻快。' },
      { type: 'h2', text: '先记住移动和搜索' },
      { type: 'p', text: '熟悉基本移动、搜索和文本对象，比装很多插件更有用。等遇到重复的操作，再给它一个快捷键。' },
    ],
  },
  {
    slug: 'starting-again',
    date: '2024-12-15',
    title: '为什么我又开始写博客了',
    category: '生活',
    readTime: '3 分钟',
    excerpt: '给自己的想法留一个可以回来的地方，也把走过的路慢慢写下来。',
    content: [
      { type: 'p', text: '很多想法当时觉得记得住，过几个月就只剩下模糊的印象。于是想重新开始写博客，把学到的东西和生活里的片段留在这里。' },
      { type: 'p', text: '不追求更新频率，只希望每次写完都比开始时更清楚一点。' },
    ],
  },
])

const tags = ['全部', '开发', '工具', '生活']
const visibleArticles = computed(() => selectedTag.value === '全部'
  ? articles.value
  : articles.value.filter((article) => article.category === selectedTag.value))
const currentSlug = computed(() => route.params.slug)
const currentArticle = computed(() => activeArticle.value || articles.value.find((article) => article.slug === currentSlug.value))
const contentBlocks = computed(() => {
  const source = currentArticle.value?.content || ''
  if (Array.isArray(source)) return source
  const blocks = []
  const lines = source.split(/\r?\n/)
  let paragraph = []
  let code = []
  let inCode = false
  const flushParagraph = () => {
    if (paragraph.length) blocks.push({ type: 'p', text: paragraph.join(' ') })
    paragraph = []
  }
  for (const line of lines) {
    if (line.trim().startsWith('```')) {
      if (!inCode) { flushParagraph(); inCode = true } else { blocks.push({ type: 'code', text: code.join('\n') }); code = []; inCode = false }
    } else if (inCode) code.push(line)
    else if (!line.trim()) flushParagraph()
    else if (line.startsWith('## ')) { flushParagraph(); blocks.push({ type: 'h2', text: line.slice(3) }) }
    else paragraph.push(line.trim())
  }
  if (inCode) blocks.push({ type: 'code', text: code.join('\n') })
  flushParagraph()
  return blocks
})
const renderedMarkdown = computed(() => {
  const content = currentArticle.value?.content
  return typeof content === 'string' ? markdownRenderer.render(content) : ''
})
const articleDate = (article) => article.published_at || article.date
const articleReadTime = (article) => article.read_time || article.readTime
const activityCells = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const year = today.getFullYear()
  const yearStart = new Date(year, 0, 1)
  const gridStart = new Date(year, 0, 1 - ((yearStart.getDay() + 6) % 7))
  const counts = new Map()
  for (const article of articles.value) {
    const value = articleDate(article)
    const key = typeof value === 'string' ? value.slice(0, 10) : ''
    if (key.startsWith(`${year}-`)) counts.set(key, (counts.get(key) || 0) + 1)
  }
  const cells = []
  for (let date = new Date(gridStart), index = 0; date <= today; date.setDate(date.getDate() + 1), index += 1) {
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    const count = counts.get(key) || 0
    cells.push({ date: key, week: Math.floor(index / 7), day: (date.getDay() + 6) % 7, count, level: count ? Math.min(count, 4) : 0 })
  }
  return cells
})
const activityWeekCount = computed(() => activityCells.value.at(-1)?.week + 1 || 1)
const activityMonthLabels = computed(() => {
  const today = new Date()
  const yearStart = new Date(today.getFullYear(), 0, 1)
  const gridStart = new Date(today.getFullYear(), 0, 1 - ((yearStart.getDay() + 6) % 7))
  const labels = []
  for (let monthStart = new Date(today.getFullYear(), 0, 1); monthStart <= today; monthStart.setMonth(monthStart.getMonth() + 1)) {
    labels.push({
      label: `${monthStart.getMonth() + 1}月`,
      week: Math.max(0, Math.floor((monthStart - gridStart) / (7 * 24 * 60 * 60 * 1000))),
    })
  }
  return labels
})
const activityTotal = computed(() => activityCells.value.reduce((total, cell) => total + cell.count, 0))
const activityDays = computed(() => activityCells.value.filter((cell) => cell.count > 0).length)
const page = computed(() => {
  if (route.path === '/') return 'home'
  if (route.path === '/blog') return 'blog'
  if (route.path.startsWith('/blog/')) return 'article'
  if (route.path === '/projects') return 'projects'
  if (route.path === '/about') return 'about'
  if (route.path === '/portal' || route.path.startsWith('/portal/')) return 'portal'
  return 'not-found'
})

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  try { localStorage.setItem('theme', isDark.value ? 'dark' : 'light') } catch (_) {}
}

function onKeydown(event) {
  if (event.key === 'Escape' && page.value === 'article') router.push('/blog')
}

function getCsrfToken() {
  return document.cookie.split('; ').find((row) => row.startsWith('csrftoken='))?.split('=')[1] || ''
}

async function loadPortal() {
  if (!route.path.startsWith('/portal')) return
  portalLoading.value = true
  try {
    const response = await fetch('/api/auth/me/', { credentials: 'include' })
    if (!response.ok) {
      isAuthenticated.value = false
      return
    }
    const user = await response.json()
    isAuthenticated.value = true
    portalUser.value = user.username || user.name || '已登录用户'
    const linksResponse = await fetch('/api/portal/links/', { credentials: 'include' })
    if (linksResponse.ok) {
      const result = await linksResponse.json()
      serviceGroups.value = Array.isArray(result) ? result : (result.groups || [])
    }
  } catch {
    isAuthenticated.value = false
  } finally {
    portalLoading.value = false
  }
}

async function signIn() {
  loginError.value = ''
  loginLoading.value = true
  try {
    const response = await fetch('/api/auth/login/', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
      body: JSON.stringify(loginForm.value),
    })
    if (!response.ok) {
      const result = await response.json().catch(() => ({}))
      throw new Error(result.detail || '账号或密码不正确，请重试。')
    }
    loginForm.value.password = ''
    await loadPortal()
  } catch (error) {
    loginError.value = error.message || '登录服务暂不可用，请稍后再试。'
  } finally {
    loginLoading.value = false
  }
}

async function signOut() {
  try {
    await fetch('/api/auth/logout/', {
      method: 'POST',
      credentials: 'include',
      headers: { 'X-CSRFToken': getCsrfToken() },
    })
  } finally {
    isAuthenticated.value = false
    serviceGroups.value = []
    portalUser.value = ''
    router.push('/portal')
  }
}

function backToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function formatShortDate(value) {
  if (!value) return ''
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value.slice(5).replace('-', '.')
  return new Intl.DateTimeFormat('zh-CN', { month: '2-digit', day: '2-digit' }).format(new Date(value)).replace('/', '.')
}

function formatDate(value) {
  if (!value) return ''
  return new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(value)).replaceAll('/', '-')
}

async function loadArticles() {
  try {
    const response = await fetch('/api/articles/')
    if (response.ok) articles.value = await response.json()
  } catch { /* Keep starter content visible while the API is unavailable. */ }
}

async function loadProjects() {
  try {
    const response = await fetch('/api/projects/')
    if (response.ok) projects.value = await response.json()
  } catch { projects.value = [] }
}

async function loadArticle(path) {
  activeArticle.value = null
  const slug = path.split('/').filter(Boolean).at(-1)
  if (!slug) return
  try {
    const response = await fetch(`/api/articles/${encodeURIComponent(slug)}/`)
    if (response.ok) activeArticle.value = await response.json()
  } catch { /* Fall back to a local starter article if available. */ }
}

watch(() => route.fullPath, () => { selectedTag.value = '全部' })
watch(() => route.path, (path) => {
  if (path.startsWith('/blog/')) loadArticle(path)
  else activeArticle.value = null
}, { immediate: true })
onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  loadArticles()
  loadProjects()
})
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
watch(() => route.path, loadPortal, { immediate: true })
</script>

<template>
  <div class="site-shell">
    <nav class="nav-wrap" aria-label="主导航">
      <RouterLink class="brand" to="/">XXX<span class="brand-dot">.</span></RouterLink>
      <div class="nav-links">
        <RouterLink to="/blog" :class="{ active: page === 'blog' || page === 'article' }">博客</RouterLink>
        <RouterLink to="/projects" :class="{ active: page === 'projects' }">项目</RouterLink>
        <RouterLink to="/about" :class="{ active: page === 'about' }">关于</RouterLink>
        <RouterLink class="portal-nav" to="/portal" :class="{ active: page === 'portal' }">个人空间</RouterLink>
        <button class="theme-toggle" type="button" :aria-label="isDark ? '切换到浅色模式' : '切换到深色模式'" @click="toggleTheme">
          <span aria-hidden="true">{{ isDark ? '☀' : '☾' }}</span>
        </button>
      </div>
    </nav>

    <main>
      <template v-if="page === 'home'">
        <div class="home-layout">
        <header class="hero">
          <div class="eyebrow"><span class="status-dot"></span> 独立记录 · 持续更新</div>
          <h1>你好，我是 <span>XXX</span></h1>
          <p class="hero-copy">后端开发者。这里记录技术、工具和生活，<br class="desktop-break" />也记录一些还在路上的想法。</p>
          <div class="social-links">
            <a href="https://github.com" target="_blank" rel="noreferrer">GitHub <span>↗</span></a>
            <a href="mailto:hello@example.com">邮箱 <span>↗</span></a>
            <a href="/feed.xml">RSS <span>↗</span></a>
          </div>
        </header>

        <div class="home-main">

        <section class="section-block">
          <div class="section-heading">
            <div><p class="kicker">RECENT WRITING</p><h2>最近文章</h2></div>
            <RouterLink class="text-link" to="/blog">全部文章 <span>→</span></RouterLink>
          </div>
          <ul class="article-list home-list">
            <li v-for="article in articles.slice(0, 5)" :key="article.slug" class="article-row">
              <time :datetime="articleDate(article)">{{ formatShortDate(articleDate(article)) }}</time>
              <RouterLink :to="`/blog/${article.slug}`">{{ article.title }}</RouterLink>
              <span class="row-arrow">↗</span>
            </li>
          </ul>
        </section>

          </div>

        <section class="activity-panel" aria-labelledby="activity-title">
          <div class="activity-heading">
            <div><p class="kicker">WRITING ACTIVITY</p><h2 id="activity-title">写作日历</h2></div>
            <p class="activity-summary"><strong>{{ new Date().getFullYear() }}</strong> · {{ activityTotal }} 篇文章 · {{ activityDays }} 个记录日</p>
          </div>
          <div class="activity-scroll">
            <div class="activity-calendar" :style="{ '--week-count': activityWeekCount }">
              <div class="activity-months" aria-hidden="true"><span v-for="month in activityMonthLabels" :key="month.label" :style="{ left: `calc(${month.week} * 13px)` }">{{ month.label }}</span></div>
              <div class="activity-layout">
                <div class="activity-weekdays" aria-hidden="true"><span>一</span><span></span><span>三</span><span></span><span>五</span><span></span><span></span></div>
                <div class="activity-grid" role="img" :aria-label="`${new Date().getFullYear()} 年写作日历：${activityTotal} 篇文章，分布在 ${activityDays} 天`">
                  <span v-for="cell in activityCells" :key="cell.date" class="activity-cell" :class="`level-${cell.level}`" :style="{ gridColumn: cell.week + 1, gridRow: cell.day + 1 }" :title="`${cell.date} · ${cell.count} 篇文章`"></span>
                </div>
              </div>
            </div>
          </div>
          <div class="activity-legend"><span>少</span><i class="level-0"></i><i class="level-1"></i><i class="level-2"></i><i class="level-3"></i><i class="level-4"></i><span>多</span></div>
        </section>

        <section class="section-block project-preview">
          <div class="section-heading">
            <div><p class="kicker">SELECTED WORK</p><h2>最近在做</h2></div>
            <RouterLink class="text-link" to="/projects">更多项目 <span>→</span></RouterLink>
          </div>
          <div class="mini-projects">
            <a v-for="(project, index) in projects.filter((item) => item.featured).slice(0, 2)" :key="project.id" class="mini-project" :href="project.url || undefined" :target="project.url ? '_blank' : undefined" :rel="project.url ? 'noreferrer' : undefined">
              <span class="project-index">{{ String(index + 1).padStart(2, '0') }}</span><div><h3>{{ project.title }}</h3><p>{{ project.description }}</p></div><span class="project-mark">↗</span>
            </a>
          </div>
        </section>
        </div>
      </template>

      <template v-else-if="page === 'blog'">
        <header class="page-header">
          <p class="kicker">NOTES & THOUGHTS</p><h1>博客<span class="brand-dot">.</span></h1>
          <p>关于开发、工具和生活的记录。写下来，慢慢想清楚。</p>
        </header>
        <div class="filter-row" aria-label="文章分类">
          <button v-for="tag in tags" :key="tag" :class="{ selected: selectedTag === tag }" @click="selectedTag = tag">{{ tag }}</button>
          <span class="filter-count">{{ visibleArticles.length }} 篇</span>
        </div>
        <ul class="article-list archive-list">
          <li v-for="article in visibleArticles" :key="article.slug" class="archive-item">
            <time :datetime="articleDate(article)">{{ formatDate(articleDate(article)) }}</time>
            <div class="archive-content"><RouterLink :to="`/blog/${article.slug}`">{{ article.title }}</RouterLink><p>{{ article.excerpt }}</p></div>
            <span class="category-pill">{{ article.category }}</span>
          </li>
        </ul>
      </template>

      <article v-else-if="page === 'article' && currentArticle" class="post-view">
        <RouterLink class="back-link" to="/blog">← 返回文章列表</RouterLink>
        <header class="post-header">
          <div class="post-meta"><time :datetime="articleDate(currentArticle)">{{ formatDate(articleDate(currentArticle)) }}</time><span>·</span><span>{{ currentArticle.category }}</span><span>·</span><span>{{ articleReadTime(currentArticle) }}阅读</span></div>
          <h1>{{ currentArticle.title }}</h1>
          <p>{{ currentArticle.excerpt }}</p>
        </header>
        <div v-if="Array.isArray(currentArticle.content)" class="post-body">
          <template v-for="(block, index) in contentBlocks" :key="index">
            <h2 v-if="block.type === 'h2'">{{ block.text }}</h2>
            <p v-else-if="block.type === 'p'">{{ block.text }}</p>
            <pre v-else-if="block.type === 'code'"><code>{{ block.text }}</code></pre>
          </template>
        </div>
        <div v-else class="post-body markdown-body" v-html="renderedMarkdown"></div>
        <div class="post-end"><span>—</span><p>感谢阅读，欢迎交流。</p><RouterLink to="/blog">继续阅读 →</RouterLink></div>
      </article>
      <div v-else-if="page === 'article'" class="empty-state"><p class="kicker">404 · ARTICLE NOT FOUND</p><h1>这篇文章暂时找不到。</h1><RouterLink class="text-link" to="/blog">回到文章列表 →</RouterLink></div>

      <template v-else-if="page === 'projects'">
        <header class="page-header"><p class="kicker">THINGS I’VE BUILT</p><h1>项目<span class="brand-dot">.</span></h1><p>一些正在做、曾经做过，或一直想做的小东西。</p></header>
        <div class="project-grid">
          <a v-for="(project, index) in projects" :key="project.id" class="project-card" :href="project.url || undefined" :target="project.url ? '_blank' : undefined" :rel="project.url ? 'noreferrer' : undefined">
            <div class="card-top"><span>{{ String(index + 1).padStart(2, '0') }} / PROJECT</span><span class="project-mark">↗</span></div><h2>{{ project.title }}</h2><p>{{ project.description }}</p><div class="tech-list"><span v-for="technology in project.technologies" :key="technology">{{ technology }}</span></div>
          </a>
        </div>
      </template>

      <template v-else-if="page === 'about'">
        <header class="page-header"><p class="kicker">A LITTLE ABOUT ME</p><h1>关于<span class="brand-dot">.</span></h1><p>你好，很高兴你来到这里。</p></header>
        <div class="about-content">
          <p>我是 XXX，一名后端开发者，平时喜欢研究软件、折腾工具，也喜欢把复杂的事情整理清楚。</p>
          <p>这个博客是我的个人空间。我会在这里记录开发中的经验、值得分享的工具，以及一些生活里的小发现。</p>
          <div class="about-note"><span class="note-icon">✳</span><div><strong>目前关注</strong><p>Python · Django · Vue · 自托管 · 写作</p></div></div>
          <p>如果你也对这些话题感兴趣，欢迎通过 <a href="mailto:hello@example.com">邮件</a> 或 GitHub 联系我。</p>
        </div>
      </template>
      <template v-else-if="page === 'portal'">
        <header class="page-header portal-header"><p class="kicker">MY SPACE · SIGN-IN REQUIRED</p><h1>个人空间<span class="brand-dot">.</span></h1><p>登录后集中访问家里的 NAS、鲁班猫和其他自托管服务。</p></header>
        <div v-if="portalLoading" class="portal-state"><span class="loading-spinner"></span><p>正在确认登录状态…</p></div>
        <section v-else-if="!isAuthenticated" class="login-card">
          <div class="login-icon">▦</div>
          <h2>登录个人空间</h2>
          <p class="login-intro">登录后查看已配置的设备和自托管服务。</p>
          <form class="login-form" @submit.prevent="signIn">
            <label for="username">账号</label>
            <input id="username" v-model.trim="loginForm.username" name="username" autocomplete="username" required placeholder="用户名或邮箱" />
            <label for="password">密码</label>
            <input id="password" v-model="loginForm.password" name="password" type="password" autocomplete="current-password" required placeholder="请输入密码" />
            <p v-if="loginError" class="login-error" role="alert">{{ loginError }}</p>
            <button class="login-submit" type="submit" :disabled="loginLoading">{{ loginLoading ? '正在登录…' : '登录并继续' }} <span>→</span></button>
          </form>
          <p class="login-footnote">博客文章仍可直接公开浏览，无需登录。</p>
        </section>
        <section v-else class="portal-content">
          <div class="portal-welcome"><div><p class="kicker">WELCOME BACK</p><h2>你好，{{ portalUser }}</h2><p>你的设备与自托管服务都在这里。</p></div><button class="logout-button" type="button" @click="signOut">退出登录</button></div>
          <div v-if="!serviceGroups.length" class="portal-empty"><span>✳</span><p>还没有添加设备或服务</p><small>在 Django 后台添加鲁班猫、NAS 等链接后，它们会显示在这里。</small></div>
          <section v-for="group in serviceGroups" :key="group.name" class="service-group">
            <div class="service-heading"><h3>{{ group.name }}</h3><span>{{ (group.items || []).length.toString().padStart(2, '0') }}</span></div>
            <div class="service-grid">
              <a v-for="service in group.items || []" :key="service.name" class="service-card" :href="service.url || undefined" :target="service.url ? '_blank' : undefined" :rel="service.url ? 'noreferrer' : undefined" :aria-disabled="!service.url">
                <span class="service-icon">{{ service.icon || '↗' }}</span><span class="service-copy"><strong>{{ service.name }}</strong><small>{{ service.url ? (service.description || '打开服务') : '请在后台填写服务地址' }}</small></span><span class="service-arrow">{{ service.url ? '↗' : '···' }}</span>
              </a>
            </div>
          </section>
          <aside class="portal-note"><span>ⓘ</span><p>这些入口由服务器登录保护。NAS、路由器和设备管理页本身也应限制在家庭网络或 VPN 内访问。</p></aside>
        </section>
      </template>
      <div v-else class="empty-state"><p class="kicker">404 · PAGE NOT FOUND</p><h1>这里还没有内容。</h1><RouterLink class="text-link" to="/">回到首页 →</RouterLink></div>
    </main>

    <footer class="site-footer">
      <span>© {{ new Date().getFullYear() }} XXX</span>
      <span class="footer-center">用一点耐心，认真做点东西。</span>
      <a href="#top" @click.prevent="backToTop">回到顶部 ↑</a>
    </footer>
  </div>
</template>
