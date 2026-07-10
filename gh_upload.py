#!/usr/bin/env python3
"""Upload anima-agent files to GitHub via REST API (git push 网络阻断开路方案)"""
import json, os, sys, urllib.request, base64, subprocess, time

REPO = "deanhan2026-lang/anima-agent"
BRANCH = "master"  # GitHub 默认分支
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
        "message": "feat: v0.1.0 Pre-alpha release — 文档完善 + 真实安装体验\n\n"
                   "📝 文档更新:\n"
                   "- README: 新增「真实安装体验」「Windows 用户提示」「npm 镜像配置」「MIT 合规声明」\n"
                   "- CONTRIBUTING.md: 贡献指南 + MIT 合规要求 + 代码风格\n"
                   "- CHANGELOG.md: v0.1.0 版本日志，标注 Pre-alpha/Developer Preview\n"
                   "- docs/ISSUES_REAL_INSTALL.md: 华为笔记本实测 10 个安装问题\n"
                   "- scripts/install.ps1: P0 修复 (npm 镜像/配置写入/PowerShell 转义)\n\n"
                   "🔧 脚本修复:\n"
                   "- install.ps1: 自动切换 npm 镜像 + Node.js v22+ 检测\n"
                   "- install_lingskills.ps1: 三件套一键安装 (新增)\n\n"
                   "基于 OpenClaw (MIT) 分发，国产模型开箱即用。", 
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
