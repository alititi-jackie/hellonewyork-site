# Hello New York｜你好，纽约

纽约生活与新移民指南静态入口站，内容以精选常青主题、可靠外部资料及 OpenAA 现有深度资源为主。

## 架构

- `index.html`：语义化首页、栏目、链接及结构化数据
- `styles.css`：响应式视觉系统
- `script.js`：轻量脚本
- `assets/*.webp`：经压缩的本地纽约摄影图片，不再依赖运行时第三方图片请求
- `og-image.jpg`：固定社交分享封面
- `content/*.json`：六个分类的文章
- `scripts/build.py`：生成文章、分类、分页、搜索索引与 Sitemap
- `article.css` / `topics.js`：文章和入口样式、渐进增强搜索
- `.github/workflows/static.yml`：PR 构建检查与主分支 GitHub Pages 自动发布

## 内容原则

1. 不复制政府、旅游机构或第三方文章和图片。
2. 涉及证件、法律、费用与资格时，明确引导用户至官方实时说明。
3. 不复制 OpenAA 的动态招聘、房屋、服务数据库，采用跳转与精选指南方式降低维护成本。
4. 新增指南前先检查目标链接、信息有效性及是否与现有 OpenAA 内容重复。

## 本地预览与维护

需要 Python 3.12，无第三方构建依赖。

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8000 --directory dist
```

在本地浏览 `http://localhost:8000/topics/`。新增文章时在相应分类文件内加一条记录，填写唯一的 slug、摘要、关键词、封面图片、段落、常见问题、来源与日期。保留旧文章首次公开日期；新文章延后上线时，在发布前更新其首次公开日期。图片请用自有或有清晰授权的真实照片，并记录来源。运行构建后会自动生成目录、搜索索引、分页和 Sitemap。

## 发布前检查

- GitHub Pages 已使用 `hellonewyork.org` 主域；每次发布后仍应检查 DNS/HTTPS。
- 确认 canonical、Open Graph URL、sitemap 域名与实际主域一致。
- 检查 OpenAA 下游页面链接是否仍有效。

## 摄影图片来源

新增 Wikimedia Commons 封面的作者、原始文件和许可记录在 [photo-credits.json](content/photo-credits.json) 中，并显示在对应文章页。以下是早期采用的 Unsplash 素材来源。

| 网站图片 | 原图页面 / 来源 |
| --- | --- |
| 首页大图与分享图 | https://unsplash.com/photos/manhattan-skyline-and-brooklyn-bridge-SVVTZtTGyaU |
| DMV 交通卡片 | https://unsplash.com/photos/yellow-taxi-cab-on-road-near-high-rise-buildings-during-daytime-4pHR99IBXQ8 |
| 新移民指南 | https://images.unsplash.com/photo-1749253045920-755da5e8910b |
| 工具箱 | https://images.unsplash.com/photo-1483658026612-2ea7827cfc81 |
| 租房与住房 | https://images.unsplash.com/photo-1702683233563-9c773a34e470 |
| 工作与招聘 | https://unsplash.com/photos/a-group-of-people-sitting-at-tables-on-a-street-V1gN5rJlfGA |
| 本地服务 | https://images.unsplash.com/photo-1508163356824-03f81a9d4e9b |
| 网站导航 | https://images.unsplash.com/photo-1729803404404-5346a94096f8 |
| 城市景点 | https://images.unsplash.com/photo-1599854171059-d91f0fee45cd |
| 品牌购物 | https://unsplash.com/photos/people-walking-on-sidewalk-during-daytime-HkRUuJUUAMA |
