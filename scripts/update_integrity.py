#!/usr/bin/env python3
"""Recalculate CSP and SRI when the approved script changes; then run security_check.py."""
import base64
import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
digest = 'sha256-' + base64.b64encode(hashlib.sha256((root / 'public/assets/site.js').read_bytes()).digest()).decode()
hashes = [digest]
for page in (root / 'public').glob('*.html'):
    content = page.read_text()
    for data in re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.S):
        json.loads(data)  # Structured data must remain valid JSON, never executable code.
        hashes.append('sha256-' + base64.b64encode(hashlib.sha256(data.encode()).digest()).decode())
    page.write_text(re.sub(r'integrity="sha256-[^"]+"', 'integrity="' + digest + '"', content))
path = root / 'vercel.json'
config = json.loads(path.read_text())
for group in config['headers']:
    for header in group['headers']:
        if header['key'] == 'Content-Security-Policy':
            approved = ' '.join("'" + value + "'" for value in dict.fromkeys(hashes))
            header['value'] = re.sub(r"script-src [^;]+", 'script-src ' + approved + " 'strict-dynamic'", header['value'])
path.write_text(json.dumps(config, indent=2) + '\n')
print('Updated approved script integrity and CSP hash.')
