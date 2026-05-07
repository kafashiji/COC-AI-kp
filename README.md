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
| 部署 | Docker Compose |

完整选型与设计详见 [docs/PLAN.md](docs/PLAN.md)。

## 项目状态

🚧 **方案设计阶段** —— 代码尚未开始，技术方案与开发计划已确定。

## 仓库结构

```
.
├── docs/
│   └── PLAN.md                        # 完整技术方案与 4 周 MVP 计划
├── 七版COC人物卡2.98.xlsx              # 人物卡模板（含公式、技能列表）
├── 克苏鲁的呼唤第七版调查员手册1.16.docx # 规则书（用于 RAG 索引）
├── LICENSE
└── README.md
```

代码骨架（计划中）：

```
backend/    # FastAPI + LlamaIndex + DeepSeek
frontend/   # Nuxt 3 + Vue 3
```

## 开发路线

| 阶段 | 周期 | 目标 |
|---|---|---|
| **MVP 单人跑团** | 4 周 | 一个玩家与 AI KP 跑通一场 30–60 分钟短团 |
| **多人工程化** | +4 周 | 多人房间 + LangGraph 状态机 + 用户系统 |
| **产品化** | 开放式 | 模组市场、回放、移动端等 |

详细周计划见 [docs/PLAN.md § 8](docs/PLAN.md)。

## 快速开始

> ⚠️ 代码尚未开始实现。下方为目标使用流程，作为开发参照。

```bash
# 启动基础设施（PostgreSQL + pgvector + Phoenix）
docker compose up -d

# 启动后端
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload

# 启动前端
cd frontend
pnpm install
pnpm dev
```

环境变量（`.env`）：

```bash
DEEPSEEK_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://coc:coc@localhost:5432/coc
EMBEDDING_MODEL=bge-m3
```

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
