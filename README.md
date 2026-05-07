# COC AI Keeper

> 一个由 AI 担任守秘人（Keeper）的克苏鲁的呼唤（COC 7 版）跑团 Web 应用。

让无法凑齐 KP 的玩家，也能体验完整的 COC 跑团：AI 叙述场景、扮演 NPC、推动剧情，并在恰当时机要求玩家进行技能检定，严格遵循规则书与模组。

## 核心特性

- **真随机骰子与确定性规则**：骰点、检定、伤害、SAN 一律由代码执行，不交给 LLM
- **混合 RAG 知识系统**：核心规则进 system prompt，长尾规则按需检索，模组按场景结构化防剧透
- **三层记忆**：短期原文 + 中期摘要 + 长期向量记忆，支撑 4–8 小时长程跑团
- **思维链可视化**：玩家能看到 AI 的工具调用过程（"AI 正在掷骰…"、"AI 正在查规则…"）
- **人物卡导入**：兼容仓库中 `七版COC人物卡2.98.xlsx` 模板

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | **Nuxt 3** + Vue 3 + TypeScript + Naive UI + Pinia |
| 后端 | **FastAPI** + Python 3.12 + `uv` + Pydantic v2 |
| AI | **LlamaIndex** + **DeepSeek-V3 / R1** + Arize Phoenix |
| 存储 | **PostgreSQL 16** + **pgvector** + Redis（多人版） |
| 流式协议 | SSE（Agent 事件流）+ WebSocket（多人房间，阶段二） |
| 部署 | 自托管（本地开发默认不用 Docker；可选 `deploy/docker-compose.yml`） |

完整选型与设计详见 [docs/PLAN.md](docs/PLAN.md)。

## 项目状态

🚧 **阶段一 Week 1 工程骨架已就绪**：FastAPI（`/health`、`/api/chat/stream` SSE）、Nuxt 3 对话页；数据库与 Phoenix 按需在本地安装（默认不走 Docker）。后续周次见 [docs/PLAN.md](docs/PLAN.md) §8。

## 仓库结构

```
.
├── backend/                 # FastAPI + DeepSeek 流式 SSE（agents/tools/rag 占位）
├── frontend/                # Nuxt 3 + Naive UI + useAgentStream
├── docs/
│   └── PLAN.md              # 完整技术方案与 MVP 计划
├── deploy/
│   └── docker-compose.yml   # 可选：容器化 PG + Phoenix（当前默认不用）
├── package.json             # 根目录 npm run dev（并行前后端）
├── scripts/
│   ├── dev.ps1              # Windows：多窗口启动
│   ├── dev.bat
│   └── run-backend.mjs      # npm run dev 调用的后端启动器
├── .env.example
├── 七版COC人物卡2.98.xlsx
├── 克苏鲁的呼唤第七版调查员手册1.16.docx
├── LICENSE
└── README.md
```

## 开发路线

| 阶段 | 周期 | 目标 |
|---|---|---|
| **MVP 单人跑团** | 4 周 | 一个玩家与 AI KP 跑通一场 30–60 分钟短团 |
| **多人工程化** | +4 周 | 多人房间 + LangGraph 状态机 + 用户系统 |
| **产品化** | 开放式 | 模组市场、回放、移动端等 |

详细周计划见 [docs/PLAN.md § 8](docs/PLAN.md)。

## 快速开始（默认：不使用 Docker）

### 1. 准备环境

- Python **3.12+**，包管理推荐 **[uv](https://docs.astral.sh/uv/)**
- Node.js **18+**（npm / pnpm 均可；若用 **NVM**，见下节）
- 复制仓库根目录 `.env.example` 为 **`backend/.env`**，至少填写 **`DEEPSEEK_API_KEY`**

### 已安装 NVM 时

**`npm` / `node` 找不到**，多半是**当前终端还没切换到 NVM 里的 Node**，或集成终端没读到 NVM 改过的 PATH。

**Windows（[nvm-windows](https://github.com/coreybutler/nvm-windows)）**

```powershell
nvm list
nvm install 22
nvm use 22
node -v
npm -v
```

每次新开 Cursor 终端若仍提示找不到命令：**先在同一终端执行一次 `nvm use 22`（或你已安装的版本号）**，再跑 `npm install`。仍不行则 **重启 Cursor**，避免沿用旧的 PATH。

**若 `nvm list` 已显示 `* 22.x`（当前在用）但 `npm` / `node` 仍提示无法识别**（常见于 **Cursor / VS Code 集成终端**）：

1. 在同一 PowerShell 里**刷新 PATH**（从系统 + 用户环境变量重新读入），再试 `node -v`、`npm -v`：

   ```powershell
   $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
   nvm use 22.22.0
   npm -v
   ```

2. 确认 **`npm.cmd` 是否存在**（nvm-windows 默认符号链接目录多为 `C:\Program Files\nodejs`，也取决于你的 `NVM_SYMLINK`）：

   ```powershell
   Get-ChildItem "C:\Program Files\nodejs" -ErrorAction SilentlyContinue
   ```

   若目录为空或没有 `npm.cmd`：用 **管理员身份**打开「命令提示符」或 PowerShell，执行 `nvm use 22.22.0`（必要时先 `nvm uninstall 22.22.0` 再 `nvm install 22.22.0`），保证符号链接创建成功。

3. **PATH 冲突**：若曾安装过独立安装包的 Node，环境变量里可能抢先指向别的目录；可在「环境变量 → Path」里把 **`%NVM_SYMLINK%` 对应的路径**（或上述 `nodejs` 目录）**移到 Node 相关条目的最前**，或暂时卸载独立 Node。

4. 仍异常时改用 **Windows 自带的「命令提示符 cmd」或新开外部 PowerShell** 试 `npm -v`，以判断是 NVM 安装问题还是仅集成终端未刷新 PATH。

5. **`node -v` 正常，但 `where npm` 找不到**（例如 `where node` 指向 `C:\nvm4w\nodejs\node.exe`）：符号链接目录里往往**缺少 `npm.cmd`**，属于 NVM 下该版本 **安装不完整** 或被安全软件删文件。可先试 Node 自带的 **Corepack**：

   ```powershell
   corepack enable
   npm -v
   ```

   仍无效则检查目录（路径以你的 `NVM_SYMLINK` 为准，常见为 `C:\nvm4w\nodejs`）：

   ```powershell
   Get-ChildItem "C:\nvm4w\nodejs"
   ```

   若没有 `npm.cmd`：用**管理员**打开终端，执行 `nvm uninstall 22.22.0`，再 `nvm install 22.22.0`，然后 `nvm use 22.22.0`。必要时重装前暂时关闭杀毒/防护，避免误删。

6. **PowerShell 报错「禁止运行脚本」「无法加载 …\npm.ps1」**：当前会话把 `npm` 解析成了 **`npm.ps1`**，被 **ExecutionPolicy** 拦截。任选其一：

   - **推荐（当前用户永久放宽）**：在新 PowerShell 执行  
     `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`  
     再执行 `npm -v`。
   - **仅本次会话**：  
     `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process`
   - **不改策略**：使用 CMD 运行 npm，或显式调用  
     `npm.cmd -v`、`npm.cmd install`

**macOS / Linux（[nvm-sh/nvm](https://github.com/nvm-sh/nvm)）**

```bash
nvm install --lts
nvm use --lts
node -v
npm -v
```

若只有 Cursor 里报错、系统自带终端正常：检查默认 Shell 配置（如 `~/.bashrc`、`~/.zshrc`）是否在**非交互 shell** 里也会加载 `nvm.sh`；可把 NVM 初始化脚本一并写入 Cursor 终端所使用的配置文件。

### 常见问题：`npm` / `node` 无法识别（未使用 NVM 时）

说明当前终端找不到 Node.js（**`npm` 随 Node 一起安装**，不会单独出现）。

1. 打开 [Node.js 官网](https://nodejs.org/)，下载并安装 **LTS**，安装向导里勾选 **Add to PATH**。  
2. **完全退出 Cursor（或至少关掉所有终端标签）再打开**，在新终端执行：`node -v`、`npm -v`，应能显示版本号。  
3. 若仍报错：在 Windows **设置 → 系统 → 关于 → 高级系统设置 → 环境变量** 里检查「用户变量」或「系统变量」中的 **Path** 是否包含 Node 目录（常见为 `C:\Program Files\nodejs\`）。

仅调试后端时可以不装 Node：在 **`backend`** 里用 `uv run uvicorn ...` 即可；**前端与根目录 `npm run dev` 必须在本终端中能运行 `node` / `npm`。**

### 命令行快速启动（仓库根目录）

首次准备：`cd backend` → `uv sync --extra dev`；`cd frontend` → `npm install`；再回到根目录安装并行工具：

```bash
npm install
```

**一起启动**（同一终端，后端 8000 + 前端多为 3000；**Ctrl+C** 结束两边）：

```bash
npm run dev
```

**只启后端**（仍建议在仓库根目录执行，会自动切到 `backend` 并带上 `uv` 的 PATH）：

```bash
npm run dev:backend
```

**只启前端**：

```bash
npm run dev:frontend
```

**不用 npm、直接进子目录时**：

```bash
cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cd frontend && npm run dev
```

### （可选）Windows 多窗口一键启动

首次准备同上。之后在仓库根目录任选其一：

- **双击** `scripts\dev.bat`
- 或在 PowerShell 中：`powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1`

会各开一个窗口。关闭窗口或在该窗口 **Ctrl+C** 即停止。

### 2. 后端

**以下命令必须在 `backend` 目录执行**（仓库根目录没有 `pyproject.toml`，会出现 `No pyproject.toml found`）。

```bash
cd backend
uv sync --extra dev
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

若提示 **`'uv' 不是内部或外部命令`**：尚未安装 `uv` 或未加入 PATH。PowerShell 安装（官方脚本）：

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

装好后**重新打开终端**，再执行 `uv sync`。若已可用 Python，也可：`python -m pip install uv`。

**不用 uv 时**（`venv` + pip，效果等价）：

```bash
cd backend
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

当前 **`/api/chat/stream` 不依赖数据库**，上述命令即可联调前端。

若已安装 **PostgreSQL** 并启用 **[pgvector](https://github.com/pgvector/pgvector)**，可在库里建好库与用户后配置 `DATABASE_URL`，再执行迁移：

```bash
uv run alembic upgrade head
# 若使用 venv：先 activate，再执行 alembic upgrade head
```

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开终端提示的本地地址（多为 `http://localhost:3000`）。

### 数据库（本地安装提要）

在 PostgreSQL 中创建数据库（示例名 `coc_ai_keeper`），安装 `vector` 扩展后，将连接串写入 `backend/.env` 的 `DATABASE_URL`，例如：

```bash
DATABASE_URL=postgresql+asyncpg://你的用户:你的密码@localhost:5432/coc_ai_keeper
```

具体安装步骤因操作系统与发行版而异，请以你所用的 PostgreSQL 文档为准。

### Phoenix（可选）

需要可观测性时，可在本机用官方文档安装 **[Arize Phoenix](https://arize.com/docs/phoenix)**（例如 `pip install arize-phoenix` 后启动），不必使用 Docker。

### 可选：Docker Compose

若你希望仍用容器跑 PostgreSQL / Phoenix，可使用 **`deploy/docker-compose.yml`**（非默认路径），在 `deploy` 目录下执行 `docker compose up -d`。

## 设计原则

1. **LLM 不算数、不骰点、不改状态** —— 全部交给确定性工具
2. **RAG 不是万能** —— 高频规则进 prompt，模组按结构化处理，避免剧透
3. **可观测性第一天就装** —— Phoenix 看思维链，否则调 prompt 抓瞎
4. **前后端彻底分离** —— SSE 事件协议固定，后端可换 UI、UI 可换后端

## 致谢

- [`StarsRail/Cocai`](https://github.com/StarsRail/Cocai) —— 同类项目的核心架构启发
- [`Cocai` 设计文章](https://building.theatlantic.com/lets-write-an-ai-keeper-for-call-of-cthulhu-part-i-design-demo-703ae46ece1b) —— Agent + Tools + RAG 的完整推导
- 海豹骰、Dice!、TRPG Saikou 等中文 TRPG 社区项目

## License

MIT —— 详见 [LICENSE](LICENSE)
