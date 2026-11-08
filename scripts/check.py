"""Validate generated navigation, metadata and the absence of duplicate legacy pages."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree

from build import OUT, ROOT, SITE

class Page(HTMLParser):
    def __init__(self, file):
        super().__init__(convert_charrefs=True)
        self.refs = []
        self.ids = set()
        self.h1s = []
        self.title = ""
        self.field = ""
        self.description = ""
        self.canonical = ""
        self.noindex = False
        self.schemas = []
        self.schema = ""
        self.og = {}
        self.feed(file.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate id: {attrs['id']}"
            self.ids.add(attrs["id"])
        if tag == "h1":
            self.h1s.append("")
            self.field = "h1"
        if tag == "title":
            self.field = "title"
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.field = "schema"
            self.schema = ""
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs["href"]
        if tag == "meta":
            if attrs.get("name") == "description":
                self.description = attrs["content"]
            if attrs.get("name") == "robots":
                self.noindex = "noindex" in attrs["content"]
            if attrs.get("property", "").startswith("og:"):
                self.og[attrs["property"]] = attrs["content"]
        if tag == "img":
            assert attrs.get("alt"), f"Missing image alt: {attrs}"
        self.refs.extend(value for key, value in attributes if key in {"href", "src"} and value)

    def handle_endtag(self, tag):
        if tag == self.field:
            self.field = ""
        if tag == "script" and self.field == "schema":
            self.schemas.append(json.loads(self.schema))
            self.field = ""

    def handle_data(self, data):
        if self.field == "title":
            self.title += data
        elif self.field == "h1":
            self.h1s[-1] += data
        elif self.field == "schema":
            self.schema += data

def page_path(file):
    return "/" + file.relative_to(OUT).as_posix().removesuffix("index.html")

def main():
    pages = {page_path(file): Page(file) for file in OUT.rglob("index.html")}
    redirects = json.loads((ROOT / "content/redirects.json").read_text(encoding="utf-8"))
    indexed = {path: page for path, page in pages.items() if not page.noindex}
    assert set(pages) - set(indexed) == redirects.keys()
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    tree = ElementTree.parse(OUT / "sitemap.xml")
    sitemap = [loc.text for loc in tree.findall("s:url/s:loc", namespace)]
    assert len(sitemap) == len(indexed) and set(sitemap) == {SITE + path for path in indexed}
    articles = json.loads((OUT / "topics/index.json").read_text(encoding="utf-8"))["articles"]
    article_paths = {article["path"] for article in articles}
    for attr in ("title", "description", "h1s"):
        values = [str(getattr(page, attr)).strip() for page in indexed.values()]
        assert all(values) and len(values) == len(set(values)), f"Missing or duplicate {attr}"
    for path, page in pages.items():
        canonical = SITE + redirects.get(path, path)
        assert len(page.h1s) == 1 and page.h1s[0].strip(), path
        assert page.canonical == canonical, (path, page.canonical)
        if path in indexed:
            assert page.og.get("og:url") == canonical, path
            if path in article_paths:
                schema = {schema["@type"]: schema for schema in page.schemas}
                assert schema["Article"]["url"] == canonical
                assert schema["Article"]["headline"] == page.h1s[0]
                assert schema["BreadcrumbList"]["itemListElement"][-1]["item"] == canonical
        for ref in filter(None, [*page.refs, page.og.get("og:image")]):
            url = urlsplit(urljoin(SITE + path, ref))
            if url.netloc != urlsplit(SITE).netloc:
                continue
            target = unquote(url.path)
            assert target not in redirects, f"Link to redirected page: {path} → {ref}"
            if target in pages:
                assert not url.fragment or unquote(url.fragment) in pages[target].ids, (path, ref)
            else:
                assert (OUT / target.lstrip("/")).is_file(), (path, ref)
    print(f"Validated {len(indexed)} canonical pages, {len(articles)} articles and {len(redirects)} fallback mappings.")

if __name__ == "__main__":
    main()
