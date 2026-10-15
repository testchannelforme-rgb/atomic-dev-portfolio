#!/usr/bin/env python3
"""Check the static pages' search metadata and sitemap without dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import sys
import xml.etree.ElementTree as ET

PUBLIC = Path(__file__).resolve().parents[1] / 'public'
ORIGIN = 'https://atomic-dev-portfolio.vercel.app'
errors = []


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.canonicals = []
        self.title = ''
        self.in_title = False
        self.lang = ''
        self.h1 = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.lang = attrs.get('lang', '')
        if tag == 'h1':
            self.h1 += 1
        if tag == 'title':
            self.in_title = True
        if tag == 'meta':
            key = attrs.get('name', attrs.get('property', ''))
            self.meta.setdefault(key, []).append(attrs.get('content', ''))
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href', ''))
        if tag == 'img' and 'alt' not in attrs:
            errors.append('Image is missing alternative text')

    def handle_data(self, data):
        if self.in_title:
            self.title += data

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False


titles, descriptions, urls = [], [], []
for path in sorted(PUBLIC.glob('*.html')):
    page = Page()
    page.feed(path.read_text())
    if page.lang != 'en' or page.h1 != 1:
        errors.append(f'{path.name}: expected English and exactly one H1')
    if path.name == '404.html':
        if 'noindex' not in page.meta.get('robots', [''])[0]:
            errors.append('404 must remain excluded from indexing')
        continue
    canonical = ORIGIN + ('/' if path.name == 'index.html' else '/' + path.stem)
    if page.canonicals != [canonical]:
        errors.append(f'{path.name}: canonical mismatch')
    required = ['description', 'viewport', 'og:title', 'og:description', 'og:type', 'og:url',
                'og:image', 'og:image:alt', 'twitter:card', 'twitter:title',
                'twitter:description', 'twitter:image', 'twitter:image:alt']
    for key in required:
        values = page.meta.get(key, [])
        if len(values) != 1 or not values[0]:
            errors.append(f'{path.name}: missing or duplicate {key}')
    if page.meta.get('og:url') != [canonical]:
        errors.append(f'{path.name}: social URL mismatch')
    if any('noindex' in value for value in page.meta.get('robots', [])):
        errors.append(f'{path.name}: public page is noindex')
    for key in ['og:image', 'twitter:image']:
        for value in page.meta.get(key, []):
            url = urlsplit(value)
            if url.scheme != 'https' or ORIGIN != url.scheme + '://' + url.netloc or not (PUBLIC / url.path.lstrip('/')).is_file():
                errors.append(f'{path.name}: invalid social image')
    titles.append(page.title)
    descriptions.extend(page.meta.get('description', []))
    urls.append(canonical)
if len(set(titles)) != len(titles) or len(set(descriptions)) != len(descriptions):
    errors.append('Indexable pages need distinct titles and descriptions')
sitemap = ET.parse(PUBLIC / 'sitemap.xml')
listed = [node.text for node in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
if set(listed) != set(urls) or len(listed) != len(set(listed)):
    errors.append('Sitemap must include each indexable canonical exactly once')
if 'Sitemap: ' + ORIGIN + '/sitemap.xml' not in (PUBLIC / 'robots.txt').read_text():
    errors.append('robots.txt sitemap reference is missing')
if errors:
    print('\n'.join('FAIL: ' + message for message in errors))
    sys.exit(1)
print(f'PASS: {len(urls)} indexable pages; unique metadata, H1, language, social images, canonicals and complete sitemap.')
