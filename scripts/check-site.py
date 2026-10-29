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
        self.section_urls = {}
        self.current_section = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'section' and attrs.get('id'):
            self.current_section = attrs['id']
            self.section_urls[self.current_section] = []
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for field in ('href', 'src', 'data-filename'):
            if attrs.get(field):
                self.urls.append(attrs[field])
                if self.current_section:
                    self.section_urls[self.current_section].append(attrs[field])

    def handle_endtag(self, tag):
        if tag == 'section':
            self.current_section = None

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
featured_urls = [url for url in home.section_urls.get('publications', [])
                 if re.fullmatch(r'/publication/[^/]+/', url)]
expected_urls = [f'/publication/{slug}/' for slug in manifest.get('featured_publications', [])]
if expected_urls and featured_urls != expected_urls:
    errors.append('Homepage featured selection or order changed')
if '/publication/' not in home.section_urls.get('publications', []):
    errors.append('Featured publications must link to the full archive')
for title in manifest.get('work_in_progress', []):
    if title not in ' '.join(home.text):
        errors.append(f'Work-in-progress title missing: {title}')
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
