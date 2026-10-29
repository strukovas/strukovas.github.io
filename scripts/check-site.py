#!/usr/bin/env python3
"""Check the generated Hugo output before it can be published (stdlib only)."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote, urlsplit

REPO = Path(__file__).resolve().parents[1]
OUTPUT = Path(sys.argv[1] if len(sys.argv) > 1 else REPO / 'build').resolve()
manifest = json.loads((REPO / 'site/content-manifest.json').read_text())
errors = []


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []
        self.ids = set()
        self.text = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for field in ('href', 'src', 'data-filename'):
            if attrs.get(field):
                self.urls.append(attrs[field])

    def handle_data(self, value):
        self.text.append(value)


for file in OUTPUT.rglob('*.html'):
    content = file.read_text()
    page = Page()
    page.feed(content)
    if re.search(r'https?://(?:dx\.)?doi\.org/https?://', content):
        errors.append(f'{file.relative_to(OUTPUT)}: duplicated DOI prefix')
    if 'strukovas.gitub.io' in content:
        errors.append(f'{file.relative_to(OUTPUT)}: misspelled production URL')
    for url in page.urls:
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        path = unquote(parsed.path)
        target = OUTPUT / path.lstrip('/') if path.startswith('/') else file.parent / path
        if not target.exists():
            errors.append(f'{file.relative_to(OUTPUT)}: missing local resource {url}')

home = Page()
home.feed((OUTPUT / 'index.html').read_text())
for section in manifest['homepage_sections']:
    if section not in home.ids:
        errors.append(f'Homepage section missing: {section}')
for slug, title in manifest['publications'].items():
    page = OUTPUT / 'publication' / slug / 'index.html'
    if not page.is_file() or title not in page.read_text():
        errors.append(f'Publication missing: {slug}')
    if not (page.parent / 'cite.bib').is_file():
        errors.append(f'Citation missing: {slug}')
for path in ('publication/example', 'talk/example-talk', 'post/getting-started', 'project/example', 'slides/example'):
    if (OUTPUT / path).exists():
        errors.append(f'Starter example published: {path}')
for expected in manifest.get('homepage_text', []):
    if expected not in ' '.join(home.text):
        errors.append(f'Homepage content missing: {expected[:80]}')
search = json.loads((OUTPUT / 'index.json').read_text())
by_url = {item['relpermalink']: item for item in search}
for slug, authors in manifest.get('publication_authors', {}).items():
    record = by_url.get(f'/publication/{slug}/', {})
    if record.get('authors') != authors:
        errors.append(f'Author names or order changed: {slug}')
    page = Page()
    page.feed((OUTPUT / 'publication' / slug / 'index.html').read_text())
    for author in authors:
        if author not in ' '.join(page.text):
            errors.append(f'Author name missing from detail page: {slug}: {author}')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'Validated {len(manifest["publications"])} publications, citations, homepage content, DOI links and local resources.')
