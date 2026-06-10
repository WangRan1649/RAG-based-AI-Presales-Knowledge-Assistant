# Agent Workbench V3.0 Case Study

## 项目背景

本项目原本是一个面向 B2B SaaS 售前场景的 RAG-based AI Pre-sales Knowledge Assistant。它使用本地 Markdown knowledge base、embedding、Chroma retrieval、LLM client、guardrails、eval 和 lightweight tracing，帮助售前或解决方案团队回答客户关于产品能力、价格、部署、安全、集成和案例的问题。

V3.0 的目标不是把项目改造成生产级平台，而是把它升级成更适合 GitHub、飞书作品集、简历和面试展示的 Agent Workbench portfolio demo。

## 原 RAG 项目的局限

单次 RAG QA 能解决“从知识库找资料并回答”的问题，但在真实售前场景里还不够：

- 问题需要先识别 intent 和 risk level，而不是直接检索。
- pricing、SLA、HIPAA、private deployment、customer case、roadmap 需要 human review。
- 回答之后需要 grounding check，避免 unsupported claims。
- 客户 follow-up email 应该只生成 draft，不应该自动发送。
- 多轮对话需要 memory compression，但不能把幻觉或未证实承诺保存为事实。
- demo 和 eval 需要可复盘的 trace，而不是只看最后答案。

## 升级目标

Agent Workbench V3.0 在 V2.0 engineering workflow 基础上加强展示能力：

- 保留现有 RAG、Agent workflow、eval 和 trace。
- 新增 Streamlit Agent Workbench V3 页面和 Trace Viewer。
- 补充 demo questions、case study、interview Q&A、resume bullets。
- 让项目更容易被截图、讲解、复盘和面试追问。
- 不引入 PostgreSQL、Redis、OpenSearch、Airflow、Docker Compose、MCP、LangGraph。

## 系统架构

```text
User Question
-> Planner Agent
-> Safe Executor
-> Retrieval Agent
   -> Chroma retrieval
   -> Markdown fallback when Chroma unavailable
-> Risk Review Agent
-> Answer Agent
-> Critic Agent
-> Answer Agent revision / finalization
-> Email Agent draft
-> Memory Manager compression
-> Agent Trace JSONL
-> Agent Eval
-> Streamlit Workbench / Trace Viewer
```

核心目录：

- `agent_workbench/agents`: 各 Agent 的规则化实现
- `agent_workbench/harness`: orchestrator、tool registry、safe executor、output validator
- `agent_workbench/schemas`: dataclass schemas
- `agent_workbench/traces/agent_traces.jsonl`: Agent run trace
- `eval/run_agent_eval.py`: 端到端 Agent Eval
- `app_streamlit.py`: RAG Copilot + Agent Workbench V3 + Trace Viewer

## Agent Workflow

一次 run 的流程如下：

1. Planner Agent 判断 intent、risk_level、required_tools、是否需要 email draft 和 human review。
2. Retrieval Agent 通过 Safe Executor 调用，优先使用 Chroma；不可用时 fallback 到 Markdown。
3. Risk Review Agent 独立判断售前风险，尤其关注 pricing、SLA、HIPAA、security、private deployment、customer case、roadmap。
4. Answer Agent 基于 retrieved sources 和 risk decision 生成 raw answer。
5. Critic Agent 检查 grounding_status 和 unsupported_claims。
6. Answer Agent 生成 final answer，避免没有依据的承诺。
7. Email Agent 只生成 follow-up email draft，不发送真实邮件。
8. Memory Manager 压缩对话记忆，只保存 confirmed facts、risk concerns、open questions、next actions。
9. Orchestrator 写入 JSONL trace，用于 Trace Viewer、debug 和 eval。

## 各 Agent 职责

Planner Agent:

- 识别售前 intent。
- 判断风险等级。
- 决定是否需要 retrieval、email draft、human review。

Retrieval Agent:

- 封装现有 RAG retrieval。
- 根据 risk level 调整 top_k。
- Chroma 不可用时降级到 Markdown keyword retrieval。
- 对非售前问题返回安全结果，不编造来源。

Risk Review Agent:

- 判断售前承诺风险。
- 对 pricing、SLA、compliance、private deployment 等问题触发 human review。
- 给 Answer Agent 提供 safe_response_guidance。

Answer Agent:

- 基于 retrieved sources 生成回答。
- 对高风险问题使用谨慎措辞。
- 避免 exact pricing、legal promise、contractual SLA 等 unsupported commitment。

Critic Agent:

- 检查回答中的关键 claim 是否有 source 支撑。
- 标记 supported、partially_supported、unsupported、uncertain。
- 必要时触发 revision_required 和 human review。

Email Agent:

- 生成客户 follow-up email draft。
- 不发送邮件，不调用外部网络。
- 高风险场景加入人工复核提醒。

Memory Manager:

- 压缩多轮对话信息。
- 只保存可确认的客户偏好和需求。
- 不把 unsupported claims、命令型输入或幻觉保存为 confirmed facts。

## Tool Registry / Safe Executor 设计

Tool Registry 的作用是明确哪些工具可以被 Agent workflow 调用，以及每个工具的输入输出边界。这样可以避免“Agent 想调用什么就调用什么”的混乱。

Safe Executor 不是完整 sandbox，也不执行任意外部命令。它的定位是 workflow-level guardrail：

- 统一记录 tool_name、input_summary、output_summary、latency_ms、status、error。
- 捕获 tool exception，转换为 workflow 可处理的 errors。
- 让 Agent Trace 能复盘工具调用路径。

## Retrieval Fallback 设计

Retrieval Agent 优先调用现有 Chroma RAG。如果当前环境没有安装 `chromadb`，或向量库不可用，系统不会崩溃，而是记录：

```text
Chroma retrieval unavailable: ModuleNotFoundError: No module named 'chromadb'
```

然后 fallback 到 `knowledge_base/*.md` 的 Markdown retrieval。对于分数低或无结果的情况，会进行 query rewrite fallback，例如把 SLA 扩展成 `service level availability human review`，把 private deployment 扩展成 `private deployment on-prem enterprise deployment guide`。

这个设计适合作品集，因为它说明项目能在轻量环境下运行，也能解释为什么本地 demo 没有完整向量库时仍然可演示。

## Risk Review / Critic 设计

Risk Review 和 Critic 不是同一个东西：

- Risk Review 关注“这个问题能不能直接承诺”，属于 business risk / compliance risk。
- Critic 关注“这个回答有没有文档依据”，属于 grounding / unsupported claim check。

例如客户问 `Can you guarantee 99.99 percent uptime SLA in the contract?`：

- Risk Review 会判断为 high risk，并要求 human review。
- Critic 会检查 final answer 是否避免了没有来源的 SLA 承诺。

## Memory Compression 设计

Memory Manager 的目标不是记录所有聊天内容，而是把有价值的信息压缩成结构化摘要：

- customer_profile
- confirmed_facts
- risk_concerns
- open_questions
- next_actions
- summary

它会避免保存：

- 未被来源支持的产品承诺
- 用户输入的命令或脚本
- 非售前问题里的无关信息
- 可能由模型幻觉产生的事实

## Trace / Eval 设计

Trace 使用 JSONL，每次 run 写一行，便于追加、查看和评估：

```text
agent_workbench/traces/agent_traces.jsonl
```

Trace 字段包括：

- run_id、timestamp、user_question
- planner_output
- tools_called
- retrieved_sources
- risk_decision
- critic_decision
- final_answer
- email_draft
- memory_summary
- human_review_required
- latency_ms
- errors

Agent Eval 运行完整 workflow，而不是只测单个函数。评估维度包括 intent_pass、tool_selection_pass、risk_classification_pass、refusal_or_safe_answer_pass、email_draft_pass、memory_retention_pass、overall_pass。

## V2.0 Eval 结果

当前 V2.0 eval dataset 共 22 条，覆盖 product feature、pricing、SLA、HIPAA、GDPR、SOC2、private deployment、customer case、roadmap、security、integration、memory、invalid / non-sales question。

结果摘要：

- overall_pass: 22/22
- pass rate: 100.0%
- high-risk cases: 13/13 passed
- fallback behavior: 当前轻量环境没有 `chromadb` 时，全部走 Markdown fallback，workflow 不崩溃

## 项目亮点

- 从传统 RAG QA 升级到可解释的 Multi-Agent Workflow。
- 每个 Agent 职责边界清晰，适合面试讲解。
- Tool Registry + Safe Executor 体现 tool governance。
- Risk Review + Critic 双层检查，分别处理业务风险和 grounding 风险。
- Memory Compression 避免保存幻觉。
- Trace + Eval 让 demo 可复盘、可截图、可量化。
- 保持轻量，不依赖复杂中间件或编排框架。

## 局限性

- 当前不是生产级系统，没有复杂权限、审计、租户隔离和高可用部署。
- Agent 逻辑主要是规则化和轻量工程封装，不是自训练模型。
- Markdown fallback 是轻量检索，不能替代高质量向量检索。
- Eval dataset 规模小，更适合作品集和面试展示。
- Email Agent 只生成 draft，不做真实发送。

## 后续升级方向

- 扩展 eval dataset，加入更多真实售前对话样本。
- 增加 source citation quality score。
- 增加前端 trace diff，比较不同 run 的 Agent decisions。
- 增加更细粒度的 risk taxonomy。
- 增加人工复核 UI，用于标注高风险回答。
- 在不破坏轻量性的前提下，支持更多 retrieval backends。

