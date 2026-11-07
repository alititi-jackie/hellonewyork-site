# Hello New York｜你好，纽约

纽约生活与新移民指南静态入口站，内容以精选常青主题、可靠外部资料及 OpenAA 现有深度资源为主。

## 架构

- `index.html`：语义化首页、栏目、链接及结构化数据
- `styles.css`：响应式视觉系统
- `script.js`：轻量脚本
- `robots.txt` / `sitemap.xml`：基础索引配置
- `.github/workflows/static.yml`：GitHub Pages 自动发布

## 内容原则

1. 不复制政府、旅游机构或第三方文章和图片。
2. 涉及证件、法律、费用与资格时，明确引导用户至官方实时说明。
3. 不复制 OpenAA 的动态招聘、房屋、服务数据库，采用跳转与精选指南方式降低维护成本。
4. 新增指南前先检查目标链接、信息有效性及是否与现有 OpenAA 内容重复。

## 发布前检查

- 将 GitHub Pages 自定义域绑定到 `hellonewyork.org`，并设置 DNS/HTTPS。
- 确认 canonical、Open Graph URL、sitemap 域名与实际主域一致。
- 检查 OpenAA 下游页面链接是否仍有效。
- 若域名尚未绑定，不要把临时 GitHub Pages 地址作为长期 canonical。
