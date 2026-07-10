# 贡献指南

感谢你对 Anima Agent 的关注！我们欢迎任何形式的贡献：代码、文档、Bug 报告、功能建议。

## 行为准则

- **尊重他人** — 保持专业和友善
- **中文优先** — 所有讨论、Issue、PR 默认使用中文（英文可接受但不要求）
- **建设性讨论** — 批评欢迎，但要提出替代方案
- **不跑题** — Issue 和 PR 聚焦于具体问题

## 如何贡献

### 报告 Bug

1. 先搜索 [已有 Issues](https://github.com/deanhan2026-lang/anima-agent/issues) 确认未被报告
2. 使用 Bug 报告模板创建新 Issue
3. 包含以下信息：
   - 操作系统和版本（`winver` / `uname -a`）
   - Node.js 版本（`node -v`）
   - OpenClaw 版本（`openclaw --version`）
   - Anima Agent 版本（`cat ~\.anima-agent\install.json` 中的 version 字段）
   - 复现步骤
   - 错误信息截图或日志

### 提交代码 (Pull Request)

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/你的功能名`
3. 编写代码 + 测试
4. 确保代码风格一致（见下方"代码风格"）
5. 提交 Commit：使用 [约定式提交](https://www.conventionalcommits.org/zh-hans/)
6. Push 到你的 Fork
7. 创建 Pull Request，描述：
   - 做了什么
   - 为什么这么做
   - 如何测试

### PR 审查流程

- 至少需要一位 Maintainer 的 Approve
- CI 检查必须通过（如有）
- 不允许包含 API Key 或敏感信息

### 文档贡献

文档和代码同等重要！欢迎改进：

- README.md — 项目主页
- docs/ — 所有 .md 文档
- 代码注释（中文）

## 代码风格

### 通用原则

- **命名清晰** — 变量、函数用有意义的名字，避免缩写
- **不超过 120 字符/行**（Python）/ **不超过 100 字符/行**（PowerShell）
- **UTF-8 编码**，LF 换行
- **Shell 脚本**: PowerShell (.ps1) for Windows, Bash (.sh) for Mac/Linux

### Python

- 遵循 [PEP 8](https://peps.python.org/pep-0008/)
- 使用 4 空格缩进
- 函数和类添加 docstring
- 类型注解推荐但非强制
- 优先使用 `pathlib.Path` 而非 `os.path`

```python
# 好的示例
def load_did(anima_dir: Path) -> dict:
    """加载或生成 MeshIdentity DID。

    Args:
        anima_dir: Anima Agent 根目录。

    Returns:
        包含 did/pub_hex 的字典。
    """
    did_path = anima_dir / "did.json"
    if did_path.exists():
        return json.loads(did_path.read_text(encoding="utf-8"))
    # ...生成逻辑
```

### PowerShell

- 使用完整参数名（`-ExecutionPolicy` 而非 `-ep`）
- 错误处理用 `try/catch` 而非 `$ErrorActionPreference`
- 注释用中文，代码用英文

### Markdown

- 标题层级清晰（`#` → `##` → `###`）
- 代码块标注语言
- 表格对齐
- 链接使用相对路径

## MIT 合规要求

Anima Agent 基于 OpenClaw（MIT 许可）进行分发。所有贡献者必须遵守以下要求：

### 必须做的 ✅

1. **保留原始版权声明** — 任何复制或修改 OpenClaw 代码的文件，必须在文件顶部保留原始版权声明：
   ```
   Copyright (c) 2026 OpenClaw Foundation
   ```
2. **保留 LICENSE 文件** — 项目的 LICENSE 文件包含 OpenClaw 原始许可声明，不得删除或修改其核心条款
3. **区分原始和新增代码** — 新增文件（如 `anima_mvp.py`、`scripts/install.ps1`）使用独立的版权声明：
   ```
   Copyright (c) 2026 LingYuan Stellar Tech (Shenzhen) Co., Ltd.
   ```
4. **文档中声明上游来源** — README 中明确标注基于 OpenClaw 构建，链接回原仓库

### 不能做的 ❌

1. **移除或模糊原始版权声明** — 不得删除 OpenClaw 核心代码中的版权信息
2. **暗示与 OpenClaw 官方有关联** — Anima Agent 是独立发行版，不是 OpenClaw 官方产品
3. **重新许可 OpenClaw 代码** — 不能将 MIT 许可的 OpenClaw 代码改为其他许可
4. **使用 OpenClaw 商标** — 不得在产品名称或 logo 中使用 "OpenClaw"（可以在文档中提及"基于 OpenClaw"）

### License Header 模板

**基于 OpenClaw 修改的文件：**
```
# Copyright (c) 2026 OpenClaw Foundation
# Modified by LingYuan Stellar Tech (Shenzhen) Co., Ltd.
# Licensed under the MIT License.
```

**Anima Agent 原创文件：**
```
# Copyright (c) 2026 LingYuan Stellar Tech (Shenzhen) Co., Ltd.
# Licensed under the MIT License.
```

## 开发流程

### 本地开发环境

```powershell
# 1. 克隆仓库
git clone https://github.com/deanhan2026-lang/anima-agent.git
cd anima-agent

# 2. 安装 OpenClaw（如未安装）
npm config set registry https://registry.npmmirror.com
npm install -g openclaw

# 3. 导入模型配置
openclaw config set models --file config/models.yaml

# 4. 运行 MVP 测试
python anima_mvp.py
```

### 提交信息格式

使用 [约定式提交](https://www.conventionalcommits.org/zh-hans/)：

```
<类型>(<范围>): <简短描述>

<详细描述>

<页脚>
```

类型：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试
- `chore`: 构建/工具

示例：
```
feat(install): 添加 Mac/Linux 安装脚本

- 新增 install.sh（Bash）
- 适配 macOS Homebrew + Linux apt
- 保持与 install.ps1 一致的功能

Closes #12
```

## 版本发布

- 由 Maintainer 负责
- 遵循 [语义化版本](https://semver.org/lang/zh-CN/)
- 发布前更新 CHANGELOG.md
- 当前 Pre-alpha 阶段，版本号 `v0.x`

## 获取帮助

- [GitHub Issues](https://github.com/deanhan2026-lang/anima-agent/issues)
- [FAQ](docs/FAQ.md)

---

🧬 灵元星辰科技 (深圳) · MIT License
