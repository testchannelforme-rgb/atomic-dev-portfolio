#!/usr/bin/env python3
"""Dependency-free guard for this static site's deploy surface and Git history.

This is a targeted source audit, not a complete credential detector or pentest.
It prints only finding locations/types, never candidate credential values.
"""
import base64
import hashlib
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.anchors = []
        self.resources = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        check(not any(key.startswith('on') for key in attrs), f'Inline event handler on {tag}')
        check('style' not in attrs, f'Inline style on {tag}')
        check(tag not in ('form', 'iframe', 'object', 'embed', 'base'), f'Unexpected active element: {tag}')
        if tag == 'script':
            check('src' in attrs, 'Inline script is prohibited')
            self.scripts.append(attrs)
        if tag == 'a':
            href = attrs.get('href', '')
            self.anchors.append(href)
            check(href.startswith(('#', '/', 'https://', 'mailto:')), 'Unsafe anchor URL scheme')
            if attrs.get('target') == '_blank':
                check({'noopener', 'noreferrer'} <= set(attrs.get('rel', '').split()), 'External tab missing rel protection')
        if tag == 'script' or tag == 'img':
            self.resources.append(attrs.get('src', ''))
        if tag == 'link' and attrs.get('rel') in ('stylesheet', 'preload', 'icon'):
            self.resources.append(attrs.get('href', ''))


config = json.loads((ROOT / 'vercel.json').read_text())
check(config.get('outputDirectory') == 'public', 'Deployment must publish only public/')
check(config.get('buildCommand') is None, 'Unexpected build command')
check(not config.get('rewrites'), 'Unexpected rewrites may hide 404 responses')
headers = {h['key'].lower(): h['value'] for item in config['headers'] if item['source'] == '/(.*)' for h in item['headers']}
csp = headers.get('content-security-policy', '')
digest = 'sha256-' + base64.b64encode(hashlib.sha256((PUBLIC / 'assets/site.js').read_bytes()).digest()).decode()
for directive in ("default-src 'none'", "script-src '" + digest + "' 'strict-dynamic'", "script-src-attr 'none'", "style-src 'self'", "style-src-attr 'none'", "connect-src 'none'", "base-uri 'none'", "object-src 'none'", "frame-ancestors 'none'", "form-action 'none'", "require-trusted-types-for 'script'", "trusted-types 'none'"):
    check(directive in csp.split('; '), f'Missing CSP directive: {directive.split()[0]}')
check('unsafe-inline' not in csp and 'unsafe-eval' not in csp, 'Unsafe CSP allowance')
check(headers.get('x-content-type-options') == 'nosniff', 'Missing MIME protection')
check(headers.get('x-frame-options') == 'DENY', 'Missing frame protection')
check(headers.get('referrer-policy') == 'no-referrer', 'Unexpected referrer policy')
check('max-age=31536000' in headers.get('strict-transport-security', ''), 'Missing HSTS')
check('camera=()' in headers.get('permissions-policy', ''), 'Missing permissions restrictions')
check(headers.get('access-control-allow-origin') == 'https://atomic-dev-portfolio.vercel.app', 'CORS must use the fixed canonical origin, never a wildcard')
check('access-control-allow-credentials' not in headers, 'Credentialed cross-origin requests are not used')

allowed_extensions = {'.html', '.css', '.js', '.svg', '.png', '.jpg', '.ttf', '.txt', '.xml'}
banned_name = 'mono' + 'posto'
for path in PUBLIC.rglob('*'):
    if path.is_file():
        check(path.suffix in allowed_extensions, f'Unexpected public file type: {path.relative_to(PUBLIC)}')
        check(not any(part.startswith('.') for part in path.relative_to(PUBLIC).parts), 'Dotfile in deployment')
        check(not re.search(r'(?i)(\.env|\.map$|\.sql$|\.bak$|\.pem$|\.key$|package(?:-lock)?\.json)', path.name), 'Sensitive filename in deployment')
        if path.suffix in {'.html', '.css', '.js', '.svg', '.txt', '.xml'}:
            check(banned_name not in path.read_text().lower(), f'Prohibited branding in {path.relative_to(PUBLIC)}')

for path in PUBLIC.glob('*.html'):
    parser = SiteParser()
    parser.feed(path.read_text())
    check(len(parser.ids) == len(set(parser.ids)), f'Duplicate id in {path.name}')
    for href in parser.anchors:
        if href.startswith('#'):
            check(href[1:] in parser.ids, f'Broken in-page anchor in {path.name}: {href}')
        elif href.startswith('/'):
            target = PUBLIC / urlparse(href).path.lstrip('/')
            check(target.exists() or target.with_suffix('.html').exists(), f'Broken local link in {path.name}')
    for source in parser.resources:
        check(source.startswith('/'), f'Resource must be self-hosted in {path.name}')
        check((PUBLIC / source.lstrip('/')).is_file(), f'Missing asset in {path.name}: {source}')
    for script in parser.scripts:
        check(script.get('integrity') == digest, f'Script SRI mismatch in {path.name}')

js = (PUBLIC / 'assets/site.js').read_text()
for pattern in (r'\binnerHTML\b', r'\bouterHTML\b', r'\binsertAdjacentHTML\b', r'\bdocument\.write\b', r'\beval\s*\(', r'\bnew\s+Function\b', r'\blocalStorage\b', r'\bdocument\.cookie\b', r'\bfetch\s*\(', r'\bconsole\.', r'\bdebugger\b'):
    check(not re.search(pattern, js), f'Unexpected runtime capability: {pattern}')

# Regex rules intentionally contain no real credentials or secret examples.
patterns = {
    'private key': r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
    'AWS access key': r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'GitHub token': r'\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b',
    'Google API key': r'\bAIza[A-Za-z0-9_-]{35}\b',
    'Stripe live key': r'\b(?:sk|rk)_live_[A-Za-z0-9]{20,}\b',
    'AI provider key': r'\bsk-(?:proj-|ant-api\d+-)?[A-Za-z0-9_-]{32,}\b',
    'Slack token': r'\bxox[baprs]-[A-Za-z0-9-]{20,}\b',
    'JWT': r'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b',
    'credential in URL': r'(?i)(?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql|redis|https?)://[^\s/:<>\'"]+:[^\s/@<>\'"]+@',
    'secret assignment': r'(?i)(?:api[_-]?key|client[_-]?secret|password|access[_-]?token|auth[_-]?token)\s*[:=]\s*[\'"][A-Za-z0-9_/.+=-]{20,}[\'"]',
}


def scan(label, data):
    text = data.decode('utf-8', errors='ignore')
    for name, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            line = text.count('\n', 0, match.start()) + 1
            errors.append(f'Secret candidate ({name}) in {label}, line {line}; value redacted')


for path in [*PUBLIC.rglob('*'), ROOT / 'vercel.json']:
    if path.is_file() and path.suffix not in {'.png', '.jpg', '.ttf'}:
        scan(str(path.relative_to(ROOT)), path.read_bytes())

commits = subprocess.check_output(['git', 'rev-list', '--all'], cwd=ROOT, text=True).splitlines()
objects = subprocess.check_output(['git', 'rev-list', '--objects', '--all'], cwd=ROOT, text=True).splitlines()
scanned = 0
for entry in objects:
    parts = entry.split(' ', 1)
    sha = parts[0]
    kind = subprocess.check_output(['git', 'cat-file', '-t', sha], cwd=ROOT, text=True).strip()
    if kind in ('blob', 'commit'):
        data = subprocess.check_output(['git', 'cat-file', '-p', sha], cwd=ROOT)
        if kind == 'blob':
            scanned += 1
        scan('Git object ' + sha[:12] + (' ' + parts[1] if len(parts) > 1 else ''), data)
        if len(parts) > 1:
            check(not re.search(r'(^|/)(\.env(?:\..*)?|[^/]+\.(?:pem|key|sql))$', parts[1]), 'Sensitive file tracked in history; inspect without exposing values')

if errors:
    for error in errors:
        print('FAIL:', error)
    sys.exit(1)
print(f'PASS: deployment boundary, CSP/SRI, public assets, links and DOM sinks; {len(commits)} reachable commits and {scanned} unique historical blobs scanned with {len(patterns)} secret rule families.')
print('Scope: reachable refs only; regex scans cannot prove absence of secrets, and do not cover account security or private/unreachable history.')
