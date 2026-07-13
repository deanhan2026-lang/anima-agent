"""
gh_push_clean.py - 用全新Tree替换anima-agent仓库内容，清除旧骨架文件
"""
import base64, json, os, subprocess, urllib.request, urllib.error

REPO = "deanhan2026-lang/anima-agent"
TOKEN = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
agent_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Content-Type": "application/json",
}

def api(method, path, data=None):
    url = f"https://api.github.com/{path}"
    raw = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, raw, HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read().decode()
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[HTTP {e.code}] {body[:300]}")
        raise

# 1. Collect files - ONLY our new ANIMA AGENT files
EXCLUDE_PREFIXES = ('.git', '__pycache__', '.egg-info', 'scripts/gh_push')
EXCLUDE_SUFFIXES = ('.pyc', '.pyo')
INCLUDE_PATHS = {'.gitignore', 'LICENSE', 'README.md', 'install.ps1', 'install.sh', 'pyproject.toml'}

files = []
for root_dir, subdirs, fnames in os.walk(agent_root):
    # Prune __pycache__ dirs
    subdirs[:] = [d for d in subdirs if d != '__pycache__' and d != '.pytest_cache' and d != '__pycache__']
    for fname in fnames:
        fpath = os.path.join(root_dir, fname)
        rel = os.path.relpath(fpath, agent_root).replace('\\', '/')
        if any(rel.startswith(p) for p in EXCLUDE_PREFIXES):
            continue
        if any(rel.endswith(s) for s in EXCLUDE_SUFFIXES):
            continue
        with open(fpath, 'rb') as f:
            content = f.read()
        if len(content) == 0:
            continue
        files.append((rel, content))

print(f"[FILES] {len(files)} to upload")
for rel, _ in sorted(files):
    print(f"  {rel}")

# 2. Create blobs
tree_items = []
for i, (rel, content) in enumerate(files):
    b64 = base64.b64encode(content).decode()
    result = json.loads(api("POST", f"repos/{REPO}/git/blobs", {"content": b64, "encoding": "base64"}))
    tree_items.append({"path": rel, "mode": "100644", "type": "blob", "sha": result["sha"]})
    if (i+1) % 10 == 0:
        print(f"  blobs: {i+1}/{len(files)}")
print(f"[BLOBS] {len(tree_items)} created")

# 3. Create tree (NO base_tree to avoid merging old files)
result = json.loads(api("POST", f"repos/{REPO}/git/trees", {"tree": tree_items}))
tree_sha = result["sha"]
print(f"[TREE] {tree_sha}")

# 4. Create commit (orphan - no parents = clean slate)
commit = json.loads(api("POST", f"repos/{REPO}/git/commits", {
    "message": "v1.0.0: ANIMA AGENT — AI Identity Sovereign Runtime\n\nClean replacement. Only ANIMA AGENT v1.0 files.",
    "tree": tree_sha,
    "parents": [],
}))
commit_sha = commit["sha"]
print(f"[COMMIT] {commit_sha}")

# 5. Force update master
api("PATCH", f"repos/{REPO}/git/refs/heads/master", {"sha": commit_sha, "force": True})
print("[PUSH] master forced to new commit (clean tree)")

# 6. Tag
try:
    tag = json.loads(api("POST", f"repos/{REPO}/git/tags", {
        "tag": "v1.0.0",
        "message": "ANIMA AGENT v1.0.0",
        "object": commit_sha,
        "type": "commit",
    }))
    # Delete old tag if exists
    try:
        api("DELETE", f"repos/{REPO}/git/refs/tags/v1.0.0")
    except:
        pass
    api("POST", f"repos/{REPO}/git/refs", {"ref": "refs/tags/v1.0.0", "sha": tag["sha"]})
    print("[TAG] v1.0.0 recreated")
except Exception as e:
    print(f"[TAG SKIP] {e}")

print("[DONE]")
