# COC AI Keeper — 任务进度

> 与 [`docs/PLAN.md`](docs/PLAN.md) 阶段规划对齐；**你可随时在下方「进度日志」追加条目**，Agent 协作时请参见根目录 [`agent.md`](agent.md)。

---

## 当前焦点

- **阶段**：阶段一 MVP · Week 1（工程骨架 + DeepSeek 流式）
- **下一步建议**：按 PLAN 推进 Week 1 余项（如本地 PG/pgvector、可选 Docker）或进入 Week 2

---

## 阶段一 · MVP 单人跑团（勾选即视为已完成）

### Week 1 — 工程骨架与流式对话

| 状态 | 任务 |
| :---: | --- |
| [x] | 仓库脚本：`backend` / `frontend` 并行启动 |
| [x] | FastAPI：`/health`、`CORS`、聊天路由前缀 `/api` |
| [x] | DeepSeek：OpenAI 兼容客户端、流式 `chat.completions` |
| [x] | SSE：`POST /api/chat/stream`，事件类型 `message_*` / `error` |
| [x] | 配置：`DEEPSEEK_*`、读取 **仓库根 `.env`** 与 **`backend/.env`**（后者覆盖） |
| [x] | 前端：fetch 流式消费 SSE；**CRLF→LF** 解析（兼容 `sse-starlette`） |
| [x] | `GET /api/chat/models`（服务端 Key 拉列表）+ 前端模型下拉；`POST stream` 支持 `model` |
| [ ] | 本地 PostgreSQL + pgvector（按需） |
| [ ] | Phoenix 观测（按需） |
| [ ] | 可选 `deploy/docker-compose.yml` |

### Week 2 — Skill + Agent + Phoenix

| 状态 | 任务 |
| :---: | --- |
| [ ] | 9 个核心 skill 设计落地 |
| [ ] | LlamaIndex Agent 接通 |
| [ ] | Phoenix 可看思维链 |

### Week 3 — RAG + 人物卡

| 状态 | 任务 |
| :---: | --- |
| [ ] | 规则书 docx → pgvector → `lookup_rulebook` |
| [ ] | 人物卡 xlsx 导入 |

### Week 4 — 记忆 + 短模组 + 短团验证

| 状态 | 任务 |
| :---: | --- |
| [ ] | 三层记忆 |
| [ ] | 模组结构化（先试一个短模组） |
| [ ] | 完整短团测试（30–60 分钟） |

---

## 阶段二 / 三（占位）

- [ ] 阶段二：多人、WS、认证、状态机等（见 PLAN §5）
- [ ] 阶段三：产品化（见 PLAN）

---

## 进度日志（可随时追加）

> **用法**：在表格 **上方**插入新行（最新在上）；日期可用 `YYYY-MM-DD`。

| 日期 | 记录 |
| --- | --- |
| 2026-05-07 | 完成 DeepSeek 双路径 `.env`、SSE CRLF 修复、`/api/chat/models` 与前端模型切换；已 Git 提交。 |

<!-- 在此注释下方复制模板追加：
| YYYY-MM-DD | 简短说明（做了啥 / 阻塞啥 / 下一步） |
-->
