(async () => {
  const search = document.querySelector('#guide-search');
  const tabs = document.querySelector('.hub-tabs');
  const grid = document.querySelector('#hub-grid');
  const pages = document.querySelector('#hub-pages');
  const empty = document.querySelector('#hub-empty');
  const status = document.querySelector('#hub-status');
  const heading = document.querySelector('.article-head h1');
  const breadcrumb = document.querySelector('.article-crumb');

  let index;
  try {
    const response = await fetch('/topics/index.json');
    if (!response.ok) return;
    index = await response.json();
  } catch {
    return;
  }

  const base = category => category ? `/topics/category/${category}/` : '/topics/';
  const pathFor = (category, page) => base(category) + (page > 1 ? `page/${page}/` : '');
  const read = () => {
    const url = new URL(location.href);
    const [, category = '', page = '1'] = url.pathname.match(
      /^\/topics\/(?:category\/([^/]+)\/)?(?:page\/(\d+)\/)?$/
    ) || [];
    return { category, page: Number(page), query: url.searchParams.get('q') || '' };
  };
  const urlFor = (category, page, query) =>
    pathFor(category, page) + (query ? '?' + new URLSearchParams({ q: query }) : '');

  function element(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value) node.textContent = value;
    return node;
  }

  function card(article) {
    const anchor = element('a', 'article-photo-card');
    anchor.href = article.path;
    const image = element('img');
    image.src = `/assets/${article.image}.webp`;
    image.alt = article.alt;
    image.loading = 'lazy';
    const copy = element('span', 'article-photo-copy');
    copy.append(element('small', '', index.categories[article.category]), element('strong', '', article.title));
    anchor.append(image, copy);
    return anchor;
  }

  function renderBreadcrumb(category, page) {
    const items = [['首页', '/'], ['纽约实用指南', base('')]];
    if (category) items.push([index.categories[category], base(category)]);
    if (page > 1) items.push([`第 ${page} 页`, pathFor(category, page)]);
    breadcrumb.replaceChildren();
    items.forEach(([label, href], i) => {
      if (i > 0) {
        const separator = element('span', '', '›');
        separator.setAttribute('aria-hidden', 'true');
        breadcrumb.append(separator);
      }
      if (i === items.length - 1) {
        const current = element('span', '', label);
        current.setAttribute('aria-current', 'page');
        breadcrumb.append(current);
      } else {
        const anchor = element('a', '', label);
        anchor.href = href;
        breadcrumb.append(anchor);
      }
    });
  }

  function render() {
    const { category, page, query } = read();
    const words = query.trim().normalize('NFKC').toLocaleLowerCase().split(/\s+/u).filter(Boolean);
    const matches = index.articles.filter(article => {
      if (category && article.category !== category) return false;
      const haystack = [article.title, article.summary, index.categories[article.category], ...article.keywords]
        .join(' ').normalize('NFKC').toLocaleLowerCase();
      return words.every(word => haystack.includes(word));
    });
    const count = Math.ceil(matches.length / index.pageSize);
    const current = Math.max(1, Math.min(page, count));
    heading.textContent = '纽约实用指南' + (category ? ` · ${index.categories[category]}` : '') +
      (current > 1 ? ` · 第 ${current} 页` : '');
    document.title = heading.textContent + '｜HelloNewYork.org';
    renderBreadcrumb(category, current);
    for (const anchor of tabs.querySelectorAll('a')) {
      if (anchor.pathname === base(category)) anchor.setAttribute('aria-current', 'page');
      else anchor.removeAttribute('aria-current');
    }
    const offset = (current - 1) * index.pageSize;
    grid.replaceChildren(...matches.slice(offset, offset + index.pageSize).map(card));
    empty.hidden = matches.length !== 0;
    status.textContent = `找到 ${matches.length} 篇指南` + (count > 1 ? `，第 ${current} 页，共 ${count} 页` : '');
    const links = Array.from({ length: count }, (_, i) => {
      const number = i + 1;
      const anchor = element('a', '', String(number));
      anchor.href = urlFor(category, number, query);
      anchor.setAttribute('aria-label', `第 ${number} 页`);
      if (number === current) anchor.setAttribute('aria-current', 'page');
      return anchor;
    });
    pages.replaceChildren(...links);
    pages.hidden = count < 2;
  }

  search.parentElement.hidden = false;
  search.value = read().query;
  search.addEventListener('input', () => {
    history.replaceState(null, '', urlFor(read().category, 1, search.value.trim()));
    render();
  });
  tabs.addEventListener('click', event => {
    const anchor = event.target.closest('a');
    if (!anchor || event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const query = search.value.trim();
    history.pushState(null, '', anchor.pathname + (query ? '?' + new URLSearchParams({ q: query }) : ''));
    render();
  });
  pages.addEventListener('click', event => {
    const anchor = event.target.closest('a');
    if (!anchor || event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    history.pushState(null, '', anchor.href);
    render();
    pages.querySelector('[aria-current="page"]')?.focus();
  });
  addEventListener('popstate', () => {
    search.value = read().query;
    render();
  });
  render();
})();
