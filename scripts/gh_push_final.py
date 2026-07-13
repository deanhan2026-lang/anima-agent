"""
gh_push_final.py - 用GitHub API上传ANIMA AGENT v1.0到 deanhan2026-lang/anima-agent
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
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[HTTP {e.code}] {body[:200]}")
        raise

# 1. Collect all files
files = []
for root_dir, subdirs, fnames in os.walk(agent_root):
    for fname in fnames:
        fpath = os.path.join(root_dir, fname)
        rel = os.path.relpath(fpath, agent_root).replace('\\', '/')
        if rel.startswith('.git') or rel.startswith('__pycache__') or rel.startswith('scripts') or rel.endswith(('.pyc', '.pyo', '.egg-info')):
            continue
        # skip __pycache__ dirs
        if '__pycache__' in rel or '.egg-info' in rel:
            continue
        with open(fpath, 'rb') as f:
            content = f.read()
        files.append((rel, content))

print(f"[FILES] {len(files)} to upload")

# 2. Create blobs + build tree
tree = []
for i, (rel, content) in enumerate(files):
    b64 = base64.b64encode(content).decode()
    blob = api("POST", f"repos/{REPO}/git/blobs", {"content": b64, "encoding": "base64"})
    tree.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
    if (i+1) % 10 == 0:
        print(f"  blobs: {i+1}/{len(files)}")
print(f"[BLOBS] {len(tree)} created")

# 3. Get parent tree from existing repo
try:
    ref = api("GET", f"repos/{REPO}/git/ref/heads/master")
    parent_sha = ref["object"]["sha"]
    parent_commit = api("GET", f"repos/{REPO}/git/commits/{parent_sha}")
    base_tree_sha = parent_commit["tree"]["sha"]
    print(f"[PARENT] master at {parent_sha[:12]}, tree {base_tree_sha[:12]}")
except:
    parent_sha = None
    base_tree_sha = None
    print("[PARENT] No master branch, creating fresh")

# 4. Create new tree
tree_params = {"tree": tree}
if base_tree_sha:
    tree_params["base_tree"] = base_tree_sha
result = api("POST", f"repos/{REPO}/git/trees", tree_params)
tree_sha = result["sha"]
print(f"[TREE] {tree_sha}")

# 5. Create commit
parents = [parent_sha] if parent_sha else []
commit = api("POST", f"repos/{REPO}/git/commits", {
    "message": "v1.0.0: ANIMA AGENT — AI Identity Sovereign Runtime",
    "tree": tree_sha,
    "parents": parents,
})
commit_sha = commit["sha"]
print(f"[COMMIT] {commit_sha}")

# 6. Update/create ref
try:
    api("PATCH", f"repos/{REPO}/git/refs/heads/master", {"sha": commit_sha, "force": True})
    print("[PUSH] master branch updated")
except:
    api("POST", f"repos/{REPO}/git/refs", {"ref": "refs/heads/master", "sha": commit_sha})
    print("[PUSH] master branch created")

# 7. Create tag
try:
    tag = api("POST", f"repos/{REPO}/git/tags", {
        "tag": "v1.0.0",
        "message": "ANIMA AGENT v1.0.0",
        "object": commit_sha,
        "type": "commit",
    })
    api("POST", f"repos/{REPO}/git/refs", {"ref": "refs/tags/v1.0.0", "sha": tag["sha"]})
    print("[TAG] v1.0.0 created")
except Exception as e:
    print(f"[TAG SKIP] {e}")

print("[DONE] ANIMA AGENT v1.0.0 pushed!")
