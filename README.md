# Hello New York｜你好，纽约

纽约生活与新移民指南静态入口站，内容以精选常青主题、可靠外部资料及 OpenAA 现有深度资源为主。

## 架构

- `index.html`：语义化首页、栏目、链接及结构化数据
- `styles.css`：响应式视觉系统
- `script.js`：轻量脚本
- `assets/*.webp`：经压缩的本地纽约摄影图片，不再依赖运行时第三方图片请求
- `og-image.jpg`：固定社交分享封面
- `robots.txt` / `sitemap.xml`：基础索引配置
- `.github/workflows/static.yml`：GitHub Pages 自动发布

## 内容原则

1. 不复制政府、旅游机构或第三方文章和图片。
2. 涉及证件、法律、费用与资格时，明确引导用户至官方实时说明。
3. 不复制 OpenAA 的动态招聘、房屋、服务数据库，采用跳转与精选指南方式降低维护成本。
4. 新增指南前先检查目标链接、信息有效性及是否与现有 OpenAA 内容重复。

## 发布前检查

- GitHub Pages 已使用 `hellonewyork.org` 主域；每次发布后仍应检查 DNS/HTTPS。
- 确认 canonical、Open Graph URL、sitemap 域名与实际主域一致。
- 检查 OpenAA 下游页面链接是否仍有效。

## 摄影图片来源

以下原图来自 Unsplash，使用前已确认图片链接及其免费使用页面。保留来源记录便于后续核对授权、替换或署名：

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
