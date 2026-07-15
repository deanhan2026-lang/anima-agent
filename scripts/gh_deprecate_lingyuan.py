"""
gh_deprecate_lingyuan.py - 更新lingyuan-os README为重定向公告，然后归档
"""
import base64, json, subprocess, urllib.request, urllib.error

REPO = "deanhan2026-lang/lingyuan-os"
TOKEN = subprocess.check_output(["gh", "auth", "token"], text=True).strip()

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
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[HTTP {e.code}] {body[:200]}")
        raise

# Get current README sha
readme = api("GET", f"repos/{REPO}/readme")
sha = readme["sha"]
print(f"[README SHA] {sha}")

# New README content
new_readme = """# 灵元 OS (LingOS) — 已迁移 / MIGRATED

> **本仓库已迁移到 [deanhan2026-lang/anima-agent](https://github.com/deanhan2026-lang/anima-agent)**
>
> 品牌统一：LingOS → **ANIMA OS** · lingyuan-v1 → **anima-v1**
> 详情请移步新仓库。

---

## 迁移记录

| 项目 | 旧名 | 新名 |
|------|------|------|
| 产品 | LingOS / 灵元 OS | **ANIMA OS** |
| 框架 | MeshIdentity | **ANIMA Identity** |
| 协议 | lingyuan-v1 | **anima-v1** |

## 新仓库

[https://github.com/deanhan2026-lang/anima-agent](https://github.com/deanhan2026-lang/anima-agent)

---

**ANIMASTELLAR TECHNOLOGY © 2026 — AI Identity Sovereign Runtime**
"""

content_b64 = base64.b64encode(new_readme.encode()).decode()

# Update README
api("PUT", f"repos/{REPO}/contents/README.md", {
    "message": "chore: deprecate lingyuan-os, redirect to anima-agent",
    "content": content_b64,
    "sha": sha,
})
print("[README UPDATED]")

# Archive the repo
api("PATCH", f"repos/{REPO}", {"archived": True})
print("[REPO ARCHIVED]")

print("[DONE]")
