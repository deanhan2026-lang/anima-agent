#!/usr/bin/env python3
"""Upload anima-agent files to GitHub via REST API (git push 网络阻断开路方案)"""
import json, os, sys, urllib.request, base64, subprocess, time

REPO = "deanhan2026-lang/anima-agent"
BRANCH = "main"  # GitHub 默认分支
ROOT = r"C:\Users\Administrator\.qclaw\workspace-agent-d9479bde\projects\anima-agent"

def get_token():
    r = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    return r.stdout.strip()

def gh_api(method, path, data=None):
    token = get_token()
    url = f"https://api.github.com{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"API Error {e.code}: {err[:500]}")
        raise

# Collect files
def collect_files():
    files = {}
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # skip .git
        if ".git" in dirpath.split(os.sep):
            continue
        for f in filenames:
            abspath = os.path.join(dirpath, f)
            relpath = os.path.relpath(abspath, ROOT).replace("\\", "/")
            files[relpath] = abspath
    return files

def upload_files():
    files = collect_files()
    print(f"Files to upload: {len(files)}")
    for k in sorted(files.keys()):
        print(f"  {k}")

    # Step 1: Get current HEAD ref
    try:
        main_ref = gh_api("GET", f"/repos/{REPO}/git/ref/heads/{BRANCH}")
        head_sha = main_ref["object"]["sha"]
        print(f"\nHEAD: {head_sha[:8]}")
    except:
        # No commits yet — create initial empty commit
        print("No commits yet, creating initial blob...")
        empty_blob = gh_api("POST", f"/repos/{REPO}/git/blobs", {
            "content": base64.b64encode(b"# Anima Agent\n").decode(),
            "encoding": "base64",
        })
        empty_tree = gh_api("POST", f"/repos/{REPO}/git/trees", {
            "tree": [{"path": ".gitkeep", "mode": "100644", "type": "blob", "sha": empty_blob["sha"]}],
        })
        init_commit = gh_api("POST", f"/repos/{REPO}/git/commits", {
            "message": "init",
            "tree": empty_tree["sha"],
        })
        gh_api("POST", f"/repos/{REPO}/git/refs", {
            "ref": f"refs/heads/{BRANCH}",
            "sha": init_commit["sha"],
        })
        head_sha = init_commit["sha"]
        print(f"  Created {head_sha[:8]}")

    # Step 2: Get old tree
    old_commit = gh_api("GET", f"/repos/{REPO}/git/commits/{head_sha}")
    old_tree_sha = old_commit["tree"]["sha"]

    # Step 3: Create blobs for all files
    print("\nCreating blobs...")
    tree_entries = []
    for relpath, abspath in files.items():
        with open(abspath, "rb") as fh:
            content = fh.read()
        blob = gh_api("POST", f"/repos/{REPO}/git/blobs", {
            "content": base64.b64encode(content).decode(),
            "encoding": "base64",
        })
        tree_entries.append({
            "path": relpath,
            "mode": "100644",
            "type": "blob",
            "sha": blob["sha"],
        })
        print(f"  {relpath} → {blob['sha'][:8]}")

    # Step 4: Create new tree (base on old tree to handle deletes)
    print("\nCreating tree...")
    new_tree = gh_api("POST", f"/repos/{REPO}/git/trees", {
        "base_tree": old_tree_sha,
        "tree": tree_entries,
    })

    # Step 5: Create commit
    print("\nCreating commit...")
    new_commit = gh_api("POST", f"/repos/{REPO}/git/commits", {
        "message": "feat: Anima Agent v0.1.0 — 灵元智能体底座首次提交\n\n"
                   "🧬 核心提交:\n"
                   "- 三件套出厂预装技能 (MeshIdentity/MemGuard/Polaris SKILL.md)\n"
                   "- 自动激活脚本 (anima_init.py)\n"
                   "- 集成规范 + 模型路由层 + 战略文档\n"
                   "- README + AGENTS.md + LICENSE (MIT)\n\n"
                   "基于 OpenClaw MIT 许可深度定制，中文优先，国产模型开箱即用。\n"
                   "激活即入网 — 每个用户启动后自动获得 DID 并加入灵元分布式身份网络。",
        "tree": new_tree["sha"],
        "parents": [head_sha],
    })

    # Step 6: Update ref
    print("\nUpdating ref...")
    gh_api("PATCH", f"/repos/{REPO}/git/refs/heads/{BRANCH}", {
        "sha": new_commit["sha"],
        "force": False,
    })

    print(f"\n✅ Uploaded! {new_commit['sha']}")
    print(f"   https://github.com/{REPO}/commit/{new_commit['sha']}")
    return new_commit["sha"]

if __name__ == "__main__":
    upload_files()
