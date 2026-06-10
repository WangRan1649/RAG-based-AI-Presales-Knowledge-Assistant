# Resume Bullets: Agent Workbench V3.0

> 不夸大为生产级系统，定位为 portfolio / internship project。

## 中文简历 Bullet

### AI Solutions Intern

- 构建面向 B2B SaaS 售前场景的 RAG-based AI Pre-sales Knowledge Assistant，基于本地 Markdown knowledge base、retrieval、grounded answer、trace 和 eval 支持产品问答演示。
- 在原 RAG 项目上升级 Multi-Agent Workflow，引入 Planner、Retrieval、Risk Review、Critic、Email Draft、Memory Manager 等模块，提升售前问答的可解释性和可复盘性。
- 设计 Tool Registry 与 Safe Executor，统一管理 tool 调用、latency、status、error 和 fallback notes，避免 workflow 因单点异常崩溃。
- 实现 Agent Trace JSONL 与 Agent Eval，覆盖 22 条售前评估样例并达到 22/22 overall_pass，用于展示 intent、risk、tool selection、grounding 和 memory checks。

### AI Pre-sales Intern

- 面向 pricing、SLA、private deployment、HIPAA、security、integration、customer case、roadmap 等售前高频问题，构建可演示的 Agent Workbench。
- 实现 Risk Review Agent，对价格、SLA、合规、客户案例和路线图承诺触发 human review，避免在 demo 中输出过度承诺。
- 实现 Critic / grounding check，对 final answer 中的关键 claim 做 source support 检查，并在 unsupported 或 uncertain 时标记复核风险。
- 构建 Streamlit Agent Workbench V3 展示页，展示 user question、final answer、planner output、retrieved sources、risk decision、critic decision、email draft、memory summary、tools called 和 trace preview。

### LLM Application Intern

- 将单次 RAG QA 升级为轻量 Multi-Agent Workflow，在不引入 LangGraph、MCP、Docker Compose 等复杂依赖的前提下实现 planning、retrieval、review、draft、memory 和 trace。
- 设计 Retrieval fallback：Chroma 不可用时自动降级到 Markdown retrieval，并在 trace 中记录 Chroma unavailable、retrieval_mode 和 errors，保证轻量环境可运行。
- 实现 Memory Compression，结构化保存 customer profile、confirmed facts、risk concerns、open questions 和 next actions，避免把 unsupported claims 保存为事实。
- 编写端到端 Agent Eval 脚本，评估 intent classification、tool selection、risk classification、safe answer、email draft 和 memory retention。

### Technical Consultant Intern

- 围绕售前顾问工作流设计 AI assistant demo，支持产品能力、部署、安全、集成、SLA、价格和客户案例等问题的结构化回答。
- 使用 Trace Viewer 展示 Agent decision path，帮助非工程面试官理解 Planner、Risk Review、Critic、Memory 和 Tool Calls 的职责边界。
- 编写中文 Case Study、Demo Questions、Interview Q&A 和中英文 Resume Bullets，将工程实现转化为可用于 GitHub、飞书作品集和面试讲解的材料。
- 保持项目轻量可复现：不引入 PostgreSQL、Redis、OpenSearch、Airflow、Docker Compose、MCP、LangGraph 或真实邮件发送。

## English Resume Bullets

### AI Solutions Intern

- Built a RAG-based AI Pre-sales Knowledge Assistant for B2B SaaS scenarios using a local Markdown knowledge base, retrieval, grounded answer generation, trace, and evaluation.
- Upgraded the original RAG demo into a lightweight Multi-Agent Workflow with Planner, Retrieval, Risk Review, Critic, Email Draft, and Memory Manager components.
- Designed a Tool Registry and Safe Executor to standardize tool calls, latency tracking, status, error handling, and fallback notes across the workflow.
- Implemented Agent Trace in JSONL and Agent Eval covering 22 pre-sales cases, achieving 22/22 overall_pass across intent, risk, tool selection, grounding, and memory checks.

### AI Pre-sales Intern

- Developed an Agent Workbench demo for common pre-sales questions, including pricing, SLA, private deployment, HIPAA, security, integration, customer cases, and roadmap topics.
- Implemented a Risk Review Agent to flag high-risk pricing, SLA, compliance, customer reference, and roadmap commitment questions for human review.
- Added a Critic / grounding check to identify unsupported claims in final answers and trigger review when source support is insufficient.
- Built a Streamlit Agent Workbench V3 view showing user question, final answer, planner output, retrieved sources, risk decision, critic decision, email draft, memory summary, tools called, and trace preview.

### LLM Application Intern

- Converted a single-turn RAG QA flow into a lightweight Multi-Agent Workflow without introducing LangGraph, MCP, Docker Compose, or heavy infrastructure dependencies.
- Designed retrieval fallback behavior so the system gracefully falls back from unavailable Chroma retrieval to local Markdown retrieval while recording errors and retrieval metadata in trace.
- Implemented Memory Compression to store customer profile, confirmed facts, risk concerns, open questions, and next actions while avoiding unsupported claims as memory facts.
- Created an end-to-end Agent Eval script to assess intent classification, tool selection, risk classification, safe answer behavior, email draft generation, and memory retention.

### Technical Consultant Intern

- Designed a pre-sales AI assistant demo that supports structured answers for product features, deployment, security, integration, SLA, pricing, and customer reference questions.
- Added a Trace Viewer to explain the Agent decision path across Planner, Risk Review, Critic, Memory, and Tool Calls for portfolio and interview demos.
- Wrote Chinese case study, demo questions, interview Q&A, and bilingual resume bullets to translate engineering work into GitHub, Feishu portfolio, and interview-ready materials.
- Kept the project lightweight and reproducible without PostgreSQL, Redis, OpenSearch, Airflow, Docker Compose, MCP, LangGraph, or real email sending.

