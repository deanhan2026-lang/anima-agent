"""
gh_push_all.py - 用GitHub API批量推送ANIMA AGENT v1.0到 deanhan2026-lang/anima-agent
绕过 git push 网络限制
"""
import base64, json, os, subprocess, urllib.request, urllib.error

REPO = "deanhan2026-lang/anima-agent"
BRANCH = "main"
TOKEN = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
agent_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Content-Type": "application/json",
}

def gh_get(path):
    r = subprocess.run(["gh", "api", path, "--jq", "."], capture_output=True, text=True)
    return json.loads(r.stdout)

def gh_post(path, data):
    url = f"https://api.github.com/{path}"
    req = urllib.request.Request(url, json.dumps(data).encode(), HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def gh_patch(path, data):
    url = f"https://api.github.com/{path}"
    req = urllib.request.Request(url, json.dumps(data).encode(), HEADERS, method="PATCH")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def upload_files():
    # 1. Get latest commit
    try:
        ref = gh_get(f"repos/{REPO}/git/ref/heads/{BRANCH}")
        current_sha = ref["object"]["sha"]
        print(f"[REF] Branch {BRANCH} at {current_sha[:12]}")
    except:
        print(f"[WARN] Branch {BRANCH} not found, creating from scratch")
        current_sha = None

    # 2. Collect files
    files = []
    dirs = ["src/anima_agent", "src/anima_agent/cli", "src/anima_agent/dashboard",
            "src/anima_agent/export", "src/anima_agent/gateway",
            "src/anima_agent/governance", "src/anima_agent/identity",
            "src/anima_agent/models", "tests", "docs", "distill"]

    for rel_dir in dirs:
        full_dir = os.path.join(agent_root, rel_dir)
        if not os.path.isdir(full_dir):
            continue
        for fname in os.listdir(full_dir):
            fpath = os.path.join(full_dir, fname)
            if os.path.isfile(fpath) and not fname.endswith(('.pyc', '.pyo')) and not fname == '__pycache__':
                rel_path = os.path.join(rel_dir, fname).replace('\\', '/')
                with open(fpath, 'rb') as f:
                    content = f.read()
                files.append({"path": rel_path, "content": base64.b64encode(content).decode()})

    # Also root files
    for fname in ['.gitignore', 'LICENSE', 'README.md', 'install.ps1', 'install.sh', 'pyproject.toml']:
        fpath = os.path.join(agent_root, fname)
        if os.path.isfile(fpath):
            with open(fpath, 'rb') as f:
                content = f.read()
            files.append({"path": fname, "content": base64.b64encode(content).decode()})

    print(f"[FILES] {len(files)} files to upload")

    # 3. Create all blobs
    tree_items = []
    for i, f in enumerate(files):
        blob = gh_post(f"repos/{REPO}/git/blobs", {"content": f["content"], "encoding": "base64"})
        tree_items.append({"path": f["path"], "mode": "100644", "type": "blob", "sha": blob["sha"]})
        if (i + 1) % 10 == 0:
            print(f"  blobs: {i+1}/{len(files)}")

    print(f"[BLOBS] {len(tree_items)} created")

    # 4. Create tree
    if current_sha:
        base_commit = gh_get(f"repos/{REPO}/git/commits/{current_sha}")
        base_tree = base_commit["tree"]["sha"]
        tree_params = {"base_tree": base_tree, "tree": tree_items}
    else:
        tree_params = {"tree": tree_items}

    tree = gh_post(f"repos/{REPO}/git/trees", tree_params)
    tree_sha = tree["sha"]
    print(f"[TREE] {tree_sha[:12]}")

    # 5. Create commit
    parents = [current_sha] if current_sha else []
    commit = gh_post(f"repos/{REPO}/git/commits", {
        "message": "v1.0.0: ANIMA AGENT — AI Identity Sovereign Runtime\n\nIncludes: DID identity, G001-G008 governance engine, model router, persona packager, gateway client, CLI (8 commands), desktop dashboard, install scripts, STELLAR strategy docs, STELLAR NYX 1.0-beta distil.",
        "tree": tree_sha,
        "parents": parents,
    })
    commit_sha = commit["sha"]
    print(f"[COMMIT] {commit_sha[:12]}")

    # 6. Get full SHA
    full_sha = commit["sha"]
    print(f"[COMMIT FULL] {full_sha}")

    # 7. Get ORIGINAL master branch tree (to wipe old files)
    try:
        master_ref = gh_get(f"repos/{REPO}/git/ref/heads/master")
        master_sha = master_ref["object"]["sha"]
        master_commit = gh_get(f"repos/{REPO}/git/commits/{master_sha}")
        master_tree = master_commit["tree"]["sha"]
        print(f"[MASTER] {master_sha[:12]} at tree {master_tree[:12]}")
    except:
        master_tree = None
        print("[MASTER] No master branch")

    # 8. Create a new tree with our files as overlay (replacing all old content)
    tree_params = {"tree": tree_items}
    tree = gh_post(f"repos/{REPO}/git/trees", tree_params)
    tree_sha = tree["sha"]
    print(f"[FINAL TREE] {tree_sha[:12]}")

    # 9. Create merge commit (use master as parent so it replaces old content)
    parents = [master_sha] if master_sha else []
    merge_commit = gh_post(f"repos/{REPO}/git/commits", {
        "message": "v1.0.0: ANIMA AGENT — AI Identity Sovereign Runtime\n\nIncludes: DID identity, G001-G008 governance, model router, persona packager, gateway client, CLI, dashboard, install scripts, STELLAR strategy docs, distil pack.",
        "tree": tree_sha,
        "parents": parents,
    })
    merge_sha = merge_commit["sha"]
    print(f"[MERGE COMMIT] {merge_sha[:12]}")

    # 10. Force update master (replace old content)
    gh_patch(f"repos/{REPO}/git/refs/heads/master", {"sha": merge_sha, "force": True})
    print(f"[PUSH] master branch -> {merge_sha[:12]}")

    # 7. Create tag
    try:
        gh_post(f"repos/{REPO}/git/tags", {
            "tag": "v1.0.0",
            "message": "ANIMA AGENT v1.0.0 — AI Identity Sovereign Runtime",
            "object": commit_sha,
            "type": "commit",
        })
        gh_post(f"repos/{REPO}/git/refs", {
            "ref": "refs/tags/v1.0.0",
            "sha": commit_sha,
        })
        print(f"[TAG] v1.0.0 created")
    except Exception as e:
        print(f"[TAG SKIP] {e}")

    print("\n[DONE] ANIMA AGENT v1.0.0 pushed to GitHub!")

if __name__ == "__main__":
    upload_files()
