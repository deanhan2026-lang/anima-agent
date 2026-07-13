# -*- coding: utf-8 -*-
"""Push anima-agent v1.1.0 to GitHub via REST API."""
import os, sys, json, base64, urllib.request, urllib.error, subprocess

sys.stdout.reconfigure(encoding='utf-8')

REPO = 'deanhan2026-lang/anima-agent'
API = 'https://api.github.com'
ROOT = r'C:\Users\Administrator\.qclaw\workspace-agent-d9479bde\anima-agent'

# Get token
token = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True).stdout.strip()
headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
}

def api(method, path, data=None):
    url = f'{API}/repos/{REPO}{path}'
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f'API error {e.code}: {e.reason}')
        print(e.read().decode())
        raise

# Get latest commit SHA from main
ref = api('GET', '/git/ref/heads/main')
base_sha = ref['object']['sha']
print(f'Base commit: {base_sha[:7]}')

# Collect all files
files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    # Skip .git and __pycache__
    dirnames[:] = [d for d in dirnames if d not in ('.git', '__pycache__', 'node_modules')]
    for fn in filenames:
        if fn.endswith(('.pyc', '.bak', '.pre_fix.bak')):
            continue
        fpath = os.path.join(dirpath, fn)
        rel = os.path.relpath(fpath, ROOT).replace('\\', '/')
        with open(fpath, 'rb') as f:
            content = f.read()
        files.append((rel, content))

print(f'Files: {len(files)}')

# Create blobs
blobs = {}
for rel, content in files:
    result = api('POST', '/git/blobs', {
        'content': base64.b64encode(content).decode(),
        'encoding': 'base64',
    })
    blobs[rel] = result['sha']
    print(f'  blob {result["sha"][:7]} {rel}')

# Get base tree
base_tree = api('GET', f'/git/commits/{base_sha}')['tree']['sha']

# Create new tree
tree_items = []
for rel, sha in blobs.items():
    tree_items.append({
        'path': rel,
        'mode': '100644',
        'type': 'blob',
        'sha': sha,
    })

new_tree = api('POST', '/git/trees', {
    'base_tree': base_tree,
    'tree': tree_items,
})
print(f'\nNew tree: {new_tree["sha"][:7]}')

# Create commit
new_commit = api('POST', '/git/commits', {
    'message': 'v1.1.0: 灵元令协议v1.0 + stellar_did + AnimaLink注册表 + Dashboard + 品牌资源\n\n新增:\n- docs/anima_token_protocol_v1.0.md: 灵元令实操规格\n- docs/STELLAR_MASTER_ROADMAP.md: 四阶段施工图\n- docs/anima_link_architecture.md: 跨平台架构\n- src/anima_agent/identity/: stellar_did.py + anima_link.py\n- src/anima_agent/dashboard/: templates/ + static/\n- scripts/ + start_public.ps1',
    'tree': new_tree['sha'],
    'parents': [base_sha],
})
print(f'New commit: {new_commit["sha"][:7]}')

# Update ref
api('PATCH', '/git/refs/heads/main', {
    'sha': new_commit['sha'],
    'force': True,
})
print(f'\n✅ Pushed {len(files)} files to {REPO} main')

# Tag v1.1.0
try:
    api('POST', '/git/refs', {
        'ref': 'refs/tags/v1.1.0',
        'sha': new_commit['sha'],
    })
    print('✅ Tag v1.1.0 created')
except urllib.error.HTTPError:
    # Tag may exist, try force update
    api('PATCH', '/git/refs/tags/v1.1.0', {
        'sha': new_commit['sha'],
        'force': True,
    })
    print('✅ Tag v1.1.0 updated')
