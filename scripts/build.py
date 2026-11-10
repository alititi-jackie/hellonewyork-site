"""Build the Pages artifact from the homepage and structured guide sources."""
import html
import json
import re
import shutil
from datetime import date
from itertools import zip_longest
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape as xml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
SITE = "https://hellonewyork.org"
HUB = "/topics/"
PAGE_SIZE = 12
CATEGORIES = {
    "dmv": "DMV", "paperwork": "生活办事", "community": "华人生活",
    "visit": "旅游购物", "phone": "手机号码", "tools": "实用工具",
}
PHOTO_CREDITS = json.loads((ROOT / "content/photo-credits.json").read_text(encoding="utf-8"))
IMAGES = {
    "dmv": "纽约街头的黄色出租车",
    "hero": "纽约曼哈顿天际线与布鲁克林大桥",
    "newcomer": "纽约地铁站日常生活场景",
    "housing": "纽约街区住宅与临街商铺",
    "jobs": "纽约华埠街景",
    "services": "纽约社区街道与商铺",
    "attractions": "夜色中的布鲁克林大桥与曼哈顿天际线",
    "shopping": "纽约第五大道购物街道与行人",
    "navigation": "纽约地铁站出入口与线路标识",
    "tools": "从高处俯瞰纽约曼哈顿建筑",
    **{name: photo["alt"] for name, photo in PHOTO_CREDITS.items()},
}

def e(value):
    return html.escape(str(value))

def link(label, href, **attrs):
    extra = "".join(f' {key.replace("_", "-")}="{e(value)}"' for key, value in attrs.items())
    return f'<a href="{e(href)}"{extra}>{e(label)}</a>'

def article_path(article):
    return f'{HUB}{article["slug"]}/'

def category_path(category):
    return f"{HUB}category/{category}/" if category else HUB

def page_path(base, number):
    return f"{base}page/{number}/" if number > 1 else base

def json_script(data, mime="application/ld+json", attrs=""):
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return f'<script type="{mime}"{attrs}>{payload}</script>'

def breadcrumb(items):
    visible = [link(label, path) for label, path in items[:-1]]
    visible.append(f'<span aria-current="page">{e(items[-1][0])}</span>')
    return f'<nav class="article-crumb" aria-label="面包屑">{" <span aria-hidden=\"true\">›</span> ".join(visible)}</nav>'

def site_header(homepage=False):
    home_href = "#top" if homepage else "/"
    anchor_prefix = "" if homepage else "/"
    sections = [
        ("start", "初到纽约"),
        ("life", "生活指南"),
        ("explore", "城市探索"),
        ("resources", "实用资源"),
    ]
    guides_link = (link("实用指南", f"{anchor_prefix}#guides") if homepage
                   else link("实用指南", f"{anchor_prefix}#guides", aria_current="page"))
    nav = guides_link + "".join(link(label, f"{anchor_prefix}#{section}") for section, label in sections)
    return f"""<header class="topbar"><div class="wrap nav">
<a class="brand" href="{home_href}" aria-label="HelloNewYork.org 首页"><span class="brandwords"><b>HelloNewYork<span class="org-suffix">.org</span></b><small>你好，纽约 · 免费公益生活指南</small></span></a>
<nav aria-label="主导航">{nav}</nav>
<span class="nav-actions"><a class="nav-cta" href="https://go.openaa.com/" target="_blank" rel="noopener">Go.OpenAA</a><button class="share-btn" type="button" aria-label="分享这个页面"><svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 15V5"/><path d="M8.5 8L12 4.5L15.5 8"/><path d="M5 13v6a1.5 1.5 0 0 0 1.5 1.5h11A1.5 1.5 0 0 0 19 19v-6"/></svg></button></span>
</div></header><nav class="mobile-nav" aria-label="手机栏目导航">{nav}</nav>"""

def home_guide_categories():
    covers = {
        "dmv": "dmv-bronx-office",
        "paperwork": "brooklyn-central-library",
        "community": "brooklyn-brownstones",
        "visit": "flushing-main-street",
        "phone": "mobile-phone-sim",
        "tools": "nyc-muni-meter",
    }
    cards = []
    credits = []
    for category, title in CATEGORIES.items():
        image = covers[category]
        photo = PHOTO_CREDITS[image]
        cards.append(
            f'<a class="photo-card" href="{category_path(category)}" aria-label="{e(title)}">'
            f'<img src="/assets/{image}.webp" alt="{e(photo["alt"])}" loading="lazy">'
            f'<div><h3>{e(title)}</h3></div></a>'
        )
        original = link(photo["credit"], photo["source"])
        license_link = link(photo["license"], photo["license_url"])
        credits.append(f'<li>{e(title)} · {original} · {license_link}</li>')
    return f"""<section id="guides" class="section wrap home-guides" aria-labelledby="home-guides-heading">
<div class="section-head"><h2 id="home-guides-heading">纽约实用指南</h2>
{link("查看全部指南 →", HUB, **{"class": "home-guides-all"})}</div>
<div class="cards">{''.join(cards)}</div>
<details class="home-guides-credits"><summary>图片来源</summary><ul>{''.join(credits)}</ul>
<p>图片已缩放并转换为 WebP。</p></details>
</section>"""

def shell(title, description, path, body, image="attractions", crumbs=(), article=None, script=""):
    full_title = f"{title}｜HelloNewYork.org"
    url = SITE + path
    img = f"{SITE}/assets/{image}.webp"
    schema = []
    if crumbs:
        schema.append({"@context": "https://schema.org", "@type": "BreadcrumbList",
                       "itemListElement": [{"@type": "ListItem", "position": i, "name": label, "item": SITE + href}
                                           for i, (label, href) in enumerate(crumbs, 1)]})
    if article:
        schema.append({"@context": "https://schema.org", "@type": "Article", "headline": title,
                       "description": description, "image": img, "url": url, "mainEntityOfPage": url,
                       "inLanguage": "zh-CN", "articleSection": CATEGORIES[article["category"]],
                       "datePublished": article["published"], "dateModified": article["updated"],
                       "author": {"@type": "Organization", "name": "HelloNewYork.org", "url": SITE},
                       "publisher": {"@type": "Organization", "name": "HelloNewYork.org", "url": SITE}})
    return f"""<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full_title)}</title><meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(url)}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/icon-192.png">
<link rel="stylesheet" href="/styles.css?v=20261115"><link rel="stylesheet" href="/article.css?v=20261114">
<meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:locale" content="zh_CN">
<meta property="og:title" content="{e(full_title)}"><meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(url)}"><meta property="og:image" content="{e(img)}">
<meta property="og:image:alt" content="{e(IMAGES[image])}"><meta name="twitter:card" content="summary_large_image">
{''.join(json_script(item) for item in schema)}
</head><body class="article-main">
<a class="skip" href="#main">跳到正文</a>
{site_header()}
{body}
<footer><div class="wrap foot"><div><a class="foot-logo" href="/">HelloNewYork<span class="org-suffix">.org</span></a><p>你好，纽约 · 免费公益生活指南 · 无需注册。</p></div>
<div class="footer-right"><a href="/topics/">纽约实用指南</a><a href="https://openaa.com/" target="_blank" rel="noopener">OpenAA.com ↗</a><span>© <span id="year">2026</span> HelloNewYork.org</span></div></div>
<div class="wrap disclaimer">本站是独立的免费公益生活信息导航项目。办事要求、价格和开放时间以相关机构或服务方公布的信息为准。</div></footer>
<script src="/script.js?v=20261115" defer></script>{script}
</body></html>
"""

def card(href, title, image, label, priority=False):
    loading = 'fetchpriority="high"' if priority else 'loading="lazy"'
    return (f'<a class="article-photo-card" href="{e(href)}"><img src="/assets/{image}.webp" '
            f'alt="{e(IMAGES[image])}" {loading}><span class="article-photo-copy">'
            f'<small>{e(label)}</small><strong>{e(title)}</strong></span></a>')

def article_card(article):
    return card(article_path(article), article["title"], article["image"], CATEGORIES[article["category"]])

def render_article(article, articles, resources):
    title = article["title"]
    path = article_path(article)
    category = article["category"]
    image = article["image"]
    crumbs = [("首页", "/"), ("纽约实用指南", HUB), (CATEGORIES[category], category_path(category)), (title, path)]
    recommendation = article.get("recommendation")
    recommendation_text = ""
    if recommendation:
        recommendation_text = (
            f'<p>{e(recommendation["before"])}'
            f'{link(*resources[recommendation["resource"]])}'
            f'{e(recommendation["after"])}</p>'
        )
    sections = "".join(
        f'<section><h2>{e(heading)}</h2>'
        + "".join(f"<p>{e(p)}</p>" for p in paragraphs)
        + (recommendation_text if recommendation and heading == recommendation["section"] else "")
        + "</section>"
        for heading, *paragraphs in article["sections"]
    )
    faq = "".join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in article["faq"])
    sources = "".join(f"<li>{link(label, url)}</li>" for label, url in article["sources"])
    resource = ""
    if article.get("resource"):
        label, url = article["resource"]
        resource = card(url, label, image, "相关资源 ↗", priority=True)
    credit = ""
    if photo := PHOTO_CREDITS.get(image):
        original = link(photo["credit"], photo["source"])
        license_link = link(photo["license"], photo["license_url"])
        credit = f'<p class="article-meta article-credit">封面图 {original} · {license_link} · 已缩放并转换为 WebP</p>'
    by_slug = {a["slug"]: a for a in articles}
    direct = [by_slug[slug] for slug in article.get("related", [])]
    related = []
    used = {category}
    for candidate in [*direct, *articles]:
        if len(related) == 4:
            break
        if candidate["category"] not in used:
            used.add(candidate["category"])
            related.append(candidate)
    next_steps = "".join(f"<li>{link(a['title'], article_path(a))}</li>" for a in direct)
    next_steps = f"<section><h2>接下来可以看</h2><ul>{next_steps}</ul></section>" if next_steps else ""
    body = f"""<main class="wrap article-body" id="main"><article>
<header class="article-head">{breadcrumb(crumbs)}<h1>{e(title)}</h1><p class="article-intro">{e(article['summary'])}</p>
<p class="article-meta">最近核查 <time datetime="{article['updated']}">{article['updated']}</time></p></header>
{resource}{credit}
<div class="article-prose">{sections}
<section class="article-faq"><h2>常见问题</h2>{faq}</section>{next_steps}
<section><h2>参考资料与办理入口</h2><ul>{sources}</ul></section></div>
</article><section class="article-related"><h2>你可能还需要</h2>
<div class="article-related-grid">{''.join(map(article_card, related))}</div></section></main>"""
    return shell(title, article["summary"], path, body, image, crumbs, article)

def render_hub(articles, category, number):
    selected = [a for a in articles if not category or a["category"] == category]
    base = category_path(category)
    path = page_path(base, number)
    title = "纽约实用指南" + (f" · {CATEGORIES[category]}" if category else "")
    description = ("从证件办理到日常生活，找到真正用得上的纽约信息。" if not category else
                   f"浏览 HelloNewYork.org 的{CATEGORIES[category]}指南。{'、'.join(a['title'] for a in selected[:2])}。")
    if number > 1:
        title += f" · 第 {number} 页"
        description += f" 第 {number} 页。"
    navigation = "".join(link(label, category_path(key), **({"aria_current": "page"} if key == category else {}))
                         for key, label in {"": "全部", **CATEGORIES}.items())
    cards = "".join(map(article_card, selected[(number - 1) * PAGE_SIZE:number * PAGE_SIZE]))
    total = (len(selected) + PAGE_SIZE - 1) // PAGE_SIZE
    pages = "".join(link(i, page_path(base, i), aria_label=f"第 {i} 页",
                         **({"aria_current": "page"} if i == number else {})) for i in range(1, total + 1))
    crumbs = [("首页", "/"), ("纽约实用指南", HUB)]
    if category:
        crumbs.append((CATEGORIES[category], base))
    if number > 1:
        crumbs.append((f"第 {number} 页", path))
    body = f"""<main class="wrap article-body" id="main"><header class="article-head">
{breadcrumb(crumbs)}<h1>{e(title)}</h1><p class="article-intro">从证件办理到日常生活，找到真正用得上的纽约信息。</p></header>
<div class="hub-search" hidden><label for="guide-search">搜索指南</label><input id="guide-search" type="search" placeholder="例如 IDNYC、租房或地铁"></div>
<nav class="hub-tabs" aria-label="指南分类">{navigation}</nav>
<p id="hub-status" class="sr-only" role="status"></p><p id="hub-empty" hidden>没有找到符合条件的指南。试试其他关键词，或切换到「全部」。</p>
<div class="hub-grid" id="hub-grid">{cards}</div>
<nav class="hub-pages" id="hub-pages" aria-label="指南分页"{'' if total > 1 else ' hidden'}>{pages}</nav>
</main>"""
    return shell(title, description, path, body, crumbs=crumbs, script='<script src="/topics.js" defer></script>')

def write(path, data):
    target = OUT / path.lstrip("/")
    if path.endswith("/"):
        target /= "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(data, encoding="utf-8")

def validate(articles, resources):
    for key in ("slug", "title", "summary", "image"):
        values = [a[key] for a in articles]
        if len(values) != len(set(values)):
            raise ValueError(f"Duplicate {key}")
    slugs = {a["slug"] for a in articles}
    for a in articles:
        slug = a["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in {"category", "page"}:
            raise ValueError(f"Invalid slug: {slug}")
        if a["category"] not in CATEGORIES or a["image"] not in IMAGES or not (ROOT / f'assets/{a["image"]}.webp').is_file():
            raise ValueError(f"Invalid category or image: {slug}")
        if date.fromisoformat(a["updated"]) < date.fromisoformat(a["published"]):
            raise ValueError(f"Invalid publication dates: {slug}")
        if len(a["sections"]) < 3 or not 3 <= len(a["faq"]) <= 5 or not a["sources"] or not a["keywords"]:
            raise ValueError(f"Incomplete article: {slug}")
        if not set(a.get("related", [])) <= slugs - {slug}:
            raise ValueError(f"Invalid related links: {slug}")
        references = [*a["sources"]]
        if a.get("resource"):
            references.append(a["resource"])
        if recommendation := a.get("recommendation"):
            section_count = sum(heading == recommendation["section"] for heading, *_ in a["sections"])
            if section_count != 1 or recommendation["resource"] not in resources:
                raise ValueError(f"Invalid recommendation: {slug}")
            label, url = resources[recommendation["resource"]]
            if urlsplit(url).path in ("", "/") or any(url == other for _, other in references):
                raise ValueError(f"Recommendation must use a unique detail URL: {slug}")
            references.append((label, url))
        for _, url in references:
            parsed = urlsplit(url)
            if parsed.scheme != "https" or not parsed.netloc:
                raise ValueError(f"Invalid reference URL: {url}")

def build():
    groups = {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in sorted((ROOT / "content").glob("*.json"))
              if path.stem in CATEGORIES}
    grouped = [[{**article, "category": category} for article in groups.get(category, [])]
               for category in CATEGORIES]
    articles = [article for row in zip_longest(*grouped) for article in row if article is not None]
    resources = json.loads((ROOT / "content/recommendation-resources.json").read_text(encoding="utf-8"))
    validate(articles, resources)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    homepage = (ROOT / "index.html").read_text(encoding="utf-8")
    for marker, content in (
        ("<!-- SITE_HEADER -->", site_header(homepage=True)),
        ("<!-- HOME_GUIDE_CATEGORIES -->", home_guide_categories()),
    ):
        if homepage.count(marker) != 1:
            raise ValueError(f"Homepage must have exactly one marker: {marker}")
        homepage = homepage.replace(marker, content)
    write("/", homepage)
    for name in ("styles.css", "article.css", "topics.js", "script.js", "site.webmanifest",
                 "favicon.svg", "favicon.ico", "favicon-32.png", "icon-192.png", "icon-512.png", "og-image.jpg", "robots.txt"):
        shutil.copyfile(ROOT / name, OUT / name)
    urls = {"/": None}
    for category in ("", *CATEGORIES):
        count = sum(not category or a["category"] == category for a in articles)
        for number in range(1, (count + PAGE_SIZE - 1) // PAGE_SIZE + 1):
            path = page_path(category_path(category), number)
            write(path, render_hub(articles, category, number))
            urls[path] = None
    for a in articles:
        path = article_path(a)
        write(path, render_article(a, articles, resources))
        urls[path] = a["updated"]
    write("/topics/index.json", json.dumps({
        "pageSize": PAGE_SIZE, "categories": CATEGORIES,
        "articles": [{**{key: a[key] for key in ("title", "summary", "category", "image", "keywords")},
                      "path": article_path(a), "alt": IMAGES[a["image"]]} for a in articles],
    }, ensure_ascii=False))
    redirects = json.loads((ROOT / "content/redirects.json").read_text(encoding="utf-8"))
    if any(source in urls or target not in urls for source, target in redirects.items()):
        raise ValueError("Invalid redirect mapping")
    # GitHub Pages serves these static redirect documents.
    for source, target in redirects.items():
        write(source, f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
                      f'<meta http-equiv="refresh" content="0;url={e(target)}"><link rel="canonical" href="{SITE}{e(target)}">'
                      f'<title>指南已迁移｜HelloNewYork.org</title></head><body><main><h1>这篇指南已迁移</h1>'
                      f'{link("打开新版指南", target)}</main></body></html>')
    sitemap = "\n".join(f"<url><loc>{xml(SITE + path)}</loc>{f'<lastmod>{updated}</lastmod>' if updated else ''}</url>"
                        for path, updated in urls.items())
    write("/sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + sitemap + "\n</urlset>\n")
    print(f"Built {len(articles)} articles and {len(urls)} canonical pages.")

if __name__ == "__main__":
    build()
