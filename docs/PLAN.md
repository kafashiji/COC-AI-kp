# COC AI Keeper —— 技术方案与开发计划

> 一个由 AI 担任守秘人（Keeper）的克苏鲁的呼唤（COC 第 7 版）跑团应用。

---

## 1. 项目目标

构建一个 Web 应用，让 AI 主持 COC 7 版跑团：
- 叙述场景、扮演 NPC、推进剧情
- 在恰当时机要求玩家进行技能检定
- 维护玩家的属性、HP、SAN、物品等状态
- 跨小时长程对话保持记忆与一致性
- 严格遵守规则书（不得自由发挥规则）、严格遵守模组（不得剧透）

非目标（暂不做）：
- AI 自动生成完整模组（仅按导入的模组运行）
- 实体桌面 / VR 体验
- 语音输入输出（一期文字）

---

## 2. 同类项目调研结论

| 项目 | 价值 |
|---|---|
| `StarsRail/Cocai` | **最直接的参考**：Python + LlamaIndex + Chainlit + DeepSeek 的 COC AI KP，已跑通单人版 |
| `kaoiki/AI-Game-DnD` | FastAPI + DeepSeek 事件驱动后端，多人状态机设计参考 |
| `Chronicle-Keeper` | Foundry VTT 模块，多层记忆系统设计参考 |
| `langraph-AI-Accompany-Agent` | LangGraph + ChromaDB 长短期记忆融合的最佳实践 |
| SillyTavern + DeepSeek | 中文社区主流跑团方案，但偏消费级 chat，不适合做产品 |

**关键启发（提炼自 Cocai）**：
> LLM 只做自然语言理解与生成；骰子、规则查询、状态变更、模组数据全部交给工具与确定性代码。这是规则强约束类 AI 应用的通用范式。

---

## 3. 核心架构

### 3.1 三层 AI 设计

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: 规则引擎（确定性、零 LLM）                │
│  · 骰点、检定、伤害、SAN、状态边界                   │
├─────────────────────────────────────────────────────┤
│  Layer 2: Agent + 工具集（LLM 路由 + 工具执行）     │
│  · LLM 决定调用哪个工具，工具结果回灌                │
├─────────────────────────────────────────────────────┤
│  Layer 3: 叙事生成（LLM 自由发挥）                  │
│  · 在工具结果之上做氛围渲染、NPC 对话                │
└─────────────────────────────────────────────────────┘
```

### 3.2 混合 RAG 策略（不是无脑全 RAG）

不同知识放不同位置：

```
System Prompt（吃 DeepSeek 缓存）
  ├─ 高频核心规则（精炼版，5–8k tokens）
  └─ KP 导演手册（叙事风格、节奏、克苏鲁氛围）

按需注入（每轮根据状态决定）
  ├─ 当前场景 + 邻接场景（来自模组结构图）
  ├─ 当前 NPC profile + 状态
  └─ 玩家显式状态（HP/SAN/物品/技能）

RAG 工具调用（按需）
  ├─ lookup_rulebook：长尾规则
  ├─ lookup_module：模组细节（限定已解锁场景，防剧透）
  └─ search_session_memory：跨小时的会话记忆
```

**RAG 不承担**：高频核心规则（性能差）、模组主线剧情（剧透风险）、玩家实时状态（应该读数据库）。

### 3.3 三层记忆架构

```
短期：最近 N=20 轮原文 → 直接进 prompt
中期：每 K 轮自动摘要 → "本场剧情概要" 进 prompt
长期：关键事件入向量库 → 按相关性检索
显式：场景/NPC/玩家状态 → 结构化数据库，必进 prompt
```

---

## 4. 技术选型

### 4.1 前端

| 分层 | 技术 | 作用 |
|---|---|---|
| 构建框架 | **Nuxt 3** | SSR + 路由 + Server API |
| 语言 | TypeScript | |
| UI 组件库 | **Naive UI** | 设计现代、TS 友好、深色模式 |
| 状态管理 | Pinia | |
| 数据请求 | `@tanstack/vue-query` + `ofetch` | |
| 流式输出 | 原生 `EventSource`（SSE） | 接 FastAPI |
| WebSocket（多人版） | 原生 WS / `socket.io-client` | 阶段二 |
| Markdown 渲染 | `md-editor-v3` + `shiki` | |
| 思维链组件 | **自研** `<AgentSteps>` | 替换 Chainlit `@cl.step` |
| 文件上传 | `@vueuse/core` 拖拽 | 导入 xlsx |
| 类型同步 | `openapi-typescript` | 从 FastAPI OpenAPI 生成 TS 类型 |

### 4.2 后端

| 分层 | 技术 | 作用 |
|---|---|---|
| 语言 | Python 3.12 + `uv` | |
| Web 框架 | **FastAPI** | REST + SSE + WebSocket |
| 流式响应 | `sse-starlette` | Agent 中间事件推流 |
| 数据校验 | Pydantic v2 | 请求/响应 + tool 入参 |
| 认证 | `fastapi-users` 或 JWT | 阶段二 |
| 异步任务 | Celery + Redis | 多人版 |

### 4.3 AI 层

| 分层 | 技术 | 作用 |
|---|---|---|
| Agent 框架 | **LlamaIndex**（`OpenAIAgent`） | 工具调度、ReAct 循环 |
| 状态机（多人） | LangGraph | 阶段二 |
| LLM 主力 | **DeepSeek-V3** | 叙事、对话、工具路由 |
| LLM 推理 | DeepSeek-R1 | NPC 关键决策、剧情分支 |
| Embedding | `bge-m3`（本地）或 `text-embedding-3-small` | 中文检索 |
| 文档解析 | `python-docx` + `unstructured` | 切手册、模组 |
| Excel 解析 | `openpyxl` | 导入人物卡 xlsx |
| 网络搜索 | Tavily | 阶段二 |
| 可观测性 | **Arize Phoenix** | Agent 思维链调试 |

### 4.4 存储

| 分层 | 技术 | 作用 |
|---|---|---|
| 主库 | **PostgreSQL 16** | 用户/角色/会话/事件/笔记 |
| 向量库 | **pgvector** | RAG 与主库共用 |
| ORM | SQLAlchemy 2.0 + Alembic | |
| 缓存 | Redis | 多人会话状态、pub/sub（阶段二） |
| 文件存储 | 本地磁盘 / MinIO | xlsx、模组文件 |

### 4.5 运维

| 分层 | 技术 |
|---|---|
| 本地开发 | **默认不用 Docker**：本机安装 Python / Node、PostgreSQL（需要 RAG 时再配 pgvector）；Phoenix 按需本机安装 |
| 容器化（可选） | `deploy/docker-compose.yml`：PostgreSQL（pgvector）+ Phoenix；多人阶段可再引入 Redis 等同文件扩展 |
| 反向代理 | Caddy（自动 HTTPS） |
| CI | GitHub Actions |
| 部署 | 自托管 VPS / Vercel（前端）+ Fly.io（后端）；生产环境再按需镜像化 |

---

## 5. AI Agent 工具集（Skills）

按"必装 → 扩展"分级，所有工具入参用 Pydantic 描述。

### 5.1 MVP 必装（9 个）

| Skill | 类别 | 作用 |
|---|---|---|
| `roll_dice(faces, count, modifier)` | 骰子 | 真随机骰点 |
| `skill_check(actor, skill, difficulty)` | 检定 | 取技能值 → 判 大成功/成功/困难/极难/失败/大失败 |
| `sanity_check(actor, loss_dice)` | SAN | SAN 检定 + 扣减 + 临时疯狂判定 |
| `get_character_sheet(player_id)` | 状态 | 读人物卡 |
| `update_player_status(player_id, patch)` | 状态 | 改 HP/MP/SAN/LUCK，带边界校验 |
| `get_current_scene()` | 场景 | 读当前场景 + 在场 NPC + 出口 |
| `move_to_scene(scene_id)` | 场景 | 切换场景 |
| `lookup_rulebook(query)` | RAG | 长尾规则查询 |
| `take_note(content, tags, importance)` | 记忆 | 写 KP 笔记，重要事件入向量库 |

### 5.2 阶段二扩展

`opposed_check` / `combat_round` / `manage_inventory` / `apply_modifier` / `reveal_clue` /
`get_npc_profile` / `update_npc_state` / `lookup_module` / `search_session_memory` /
`search_notes` / `summarize_recent_turns` / `suggest_actions` / `generate_npc_speech` /
`narrate_consequence` / `web_search` / `import_character_sheet`

### 5.3 设计原则

1. **每个 skill 入参用 Pydantic 描述**，否则 LLM 调用会乱传
2. **状态变更类返回结构化结果**（不是字符串），避免 LLM 误读
3. **危险操作幂等校验**：HP 不能减成负、SAN 不能超 99
4. **检定与叙述分离**：`skill_check` 只判定，`narrate_consequence` 才讲故事
5. **剧透字段隔离**：模组里凶手/真相用 `redact_until_revealed` 标记

---

## 6. 前后端通信契约（SSE 事件协议）

替换 Chainlit `@cl.step` 的核心机制。后端 `/api/chat/stream` 推流：

```ts
type AgentEvent =
  | { type: 'message_start';   id: string }
  | { type: 'message_delta';   id: string; content: string }
  | { type: 'message_end';     id: string }
  | { type: 'tool_call_start'; id: string; name: string; args: object }
  | { type: 'tool_call_end';   id: string; result: object }
  | { type: 'state_change';    patch: object }
  | { type: 'dice_roll';       faces: number; result: number; label: string }
  | { type: 'error';           message: string }
```

前端 `<AgentSteps>` 按 `type` 分类渲染（思维链 / 骰点动效 / 状态变化提示）。

---

## 7. 项目结构

```
coc-ai-keeper/
├── backend/                     # FastAPI + LlamaIndex
│   ├── app/
│   │   ├── api/                # REST + SSE 路由
│   │   ├── agents/             # Agent 编排
│   │   ├── tools/              # 9 个 skill 实现
│   │   ├── rag/                # 切块 / 索引 / 检索
│   │   ├── models/             # SQLAlchemy 模型
│   │   ├── schemas/            # Pydantic schema
│   │   └── llm/                # DeepSeek 客户端封装
│   ├── alembic/
│   ├── tests/
│   ├── pyproject.toml          # uv
│   └── Dockerfile              # 可选；阶段一再补
├── frontend/                    # Nuxt 3 + Vue 3
│   ├── components/
│   │   ├── chat/
│   │   │   ├── MessageList.vue
│   │   │   ├── AgentSteps.vue           # 思维链
│   │   │   └── DiceRoll.vue
│   │   ├── character/
│   │   │   └── CharacterSheet.vue
│   │   └── upload/
│   ├── composables/
│   │   ├── useAgentStream.ts            # SSE 客户端
│   │   └── useCharacter.ts
│   ├── pages/
│   ├── stores/                          # Pinia
│   ├── types/
│   │   └── api.ts                       # openapi-typescript 生成
│   └── nuxt.config.ts
├── docs/
│   └── PLAN.md
├── deploy/
│   └── docker-compose.yml       # 可选：PG + pgvector + Phoenix（本地默认不用）
├── .env.example
└── README.md
```

---

## 8. 开发计划

### 阶段 1：MVP 单人跑团（4 周）

| 周次 | 目标 | 验收 |
|---|---|---|
| Week 1 | 工程骨架：本地 Python/Node + FastAPI + Nuxt 3 + DeepSeek 流式 SSE；PG/pgvector 与 Phoenix 按需本地安装，**可选** `deploy/docker-compose.yml` | 浏览器能与 DeepSeek 流式对话 |
| Week 2 | 实现 9 个核心 skill + LlamaIndex Agent 接通 + Phoenix 能看思维链 | AI 能调 `roll_dice` 并把结果叙述出来 |
| Week 3 | 规则书 docx 解析 → pgvector 入库 → `lookup_rulebook` RAG 跑通 + 人物卡 xlsx 导入 | AI 能查冷门规则、能读玩家人物卡 |
| Week 4 | 三层记忆 + 模组结构化（先手动一个简单短模组） + 跑通一场完整短团（30–60 分钟） | 一场短团测试录像 |

### 阶段 2：工程化（4 周）

- 多人房间（FastAPI WebSocket + Redis pub/sub）
- LangGraph 显式状态机
- 用户认证与会话隔离
- 阶段二的 16 个扩展 skill
- DeepSeek-R1 接入关键决策点
- 模组导入工具（半自动场景图生成）

### 阶段 3：产品化（开放式）

- 模组市场 / 社区分享
- 跑团回放与导出
- 美术资产（地图、立绘、骰子动效）
- 移动端适配
- 计费与限流

---

## 9. 关键避坑清单

| 陷阱 | 规避 |
|---|---|
| 让 LLM 自己骰、自己改 HP/SAN | 一律走工具，system prompt 明令禁止 |
| 把整本手册 / 整本模组塞 prompt | 上下文必爆，且注意力稀释；用混合 RAG |
| 把模组也丢进向量库 | 会剧透；按场景结构化 + 进度指针 |
| 一开始就上 SillyTavern | 消费级前端，不适合产品化 |
| 不装可观测性 | 调 prompt 抓瞎；第一天就上 Phoenix |
| LlamaIndex 用 ReAct 模式 | 中文场景幻觉率高；用 `OpenAIAgent` + DeepSeek 原生 function calling |
| 把检定与叙述塞一个工具 | LLM 会跳步；拆成 `skill_check` + `narrate_consequence` |
| 直接 PDF 喂模组 | 必须人工 / 半自动结构化为场景图 JSON |
| Chainlit 里强塞 Vue 组件 | 两边好处都丢；要么纯 Chainlit 要么纯 Vue |

---

## 10. 资料引用

- COC 第 7 版调查员手册（项目根目录 `克苏鲁的呼唤第七版调查员手册1.16.docx`）
- 七版 COC 人物卡 2.98（项目根目录 `七版COC人物卡2.98.xlsx`）
- Cocai 项目：https://github.com/StarsRail/Cocai
- Cocai 设计文章：https://building.theatlantic.com/lets-write-an-ai-keeper-for-call-of-cthulhu-part-i-design-demo-703ae46ece1b
- DeepSeek API 文档：https://api-docs.deepseek.com
- LlamaIndex：https://docs.llamaindex.ai
- Naive UI：https://www.naiveui.com
- pgvector：https://github.com/pgvector/pgvector
