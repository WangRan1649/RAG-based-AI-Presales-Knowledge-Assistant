# AI Pre-sales Copilot

## Agent Workbench V3.0 Portfolio Demo

Agent Workbench V3.0 is the portfolio-oriented version of this project. It keeps the existing RAG, Agent workflow, eval, and trace capabilities, then adds a clearer Streamlit showcase, Trace Viewer, demo questions, case study, interview Q&A, and resume bullets.

中文说明：V3.0 的目标是让项目更适合 GitHub、飞书作品集、简历和面试展示。它不是生产级平台，也没有引入 PostgreSQL、Redis、OpenSearch、Airflow、Docker Compose、MCP、LangGraph、复杂权限系统、真实邮件发送或自动外部网络调用。

### Architecture Overview

```text
User Question
-> Planner Agent
-> Safe Executor + Tool Registry
-> Retrieval Agent
   -> Chroma retrieval when available
   -> Markdown fallback when Chroma is unavailable
-> Risk Review Agent
-> Answer Agent
-> Critic Agent / grounding check
-> Email Agent draft only
-> Memory Manager / compression
-> Agent Trace JSONL
-> Agent Eval
-> Streamlit Agent Workbench V3 + Trace Viewer
```

Key files:

- `app_streamlit.py`: Streamlit demo with `RAG Copilot`, `Agent Workbench V3`, and `Trace Viewer` tabs.
- `agent_workbench/harness/agent_orchestrator.py`: end-to-end Agent workflow runner.
- `agent_workbench/traces/agent_traces.jsonl`: JSONL trace file for recent runs.
- `eval/run_agent_eval.py`: Agent Eval runner.
- `scripts/run_agent_workbench_smoke_test.py`: smoke test runner.
- `docs/demo_questions_agent_workbench.md`: screenshot and interview demo questions.
- `docs/agent_workbench_case_study_cn.md`: Chinese case study.
- `docs/interview_qa_agent_workbench_cn.md`: Chinese interview Q&A.
- `docs/resume_bullets_agent_workbench.md`: Chinese and English resume bullets.

### Run Commands

Run one Agent Workbench question:

```bash
python -m agent_workbench.harness.agent_orchestrator --question "Can InsightFlow support private deployment and SLA?"
```

Run without writing trace:

```bash
python -m agent_workbench.harness.agent_orchestrator --question "Can InsightFlow support private deployment and SLA?" --no-trace
```

Run Agent Eval:

```bash
python eval\run_agent_eval.py
```

Run smoke test:

```bash
python scripts\run_agent_workbench_smoke_test.py
```

Run Streamlit demo:

```bash
streamlit run app_streamlit.py
```

If Streamlit is not installed in the current environment, the CLI workflow and eval can still run. Install optional UI dependencies with:

```bash
pip install -r requirements.txt
```

If `chromadb` is not installed or the vector store is unavailable, Retrieval Agent records a clear error such as:

```text
Chroma retrieval unavailable: ModuleNotFoundError: No module named 'chromadb'
```

Then it automatically falls back to Markdown retrieval over `knowledge_base/*.md`. This is expected in lightweight portfolio environments and should not be treated as a workflow failure.

### V2 Eval Result Summary

Latest V2 Agent Eval summary:

- overall_pass: 22/22
- pass rate: 100.0%
- high-risk cases: 13/13 passed
- covered scenarios: product feature, pricing, SLA, HIPAA, GDPR, SOC2, private deployment, customer case, roadmap, security, integration, memory, invalid / non-sales question
- fallback behavior: Chroma unavailable is captured in trace and handled through Markdown fallback

### Portfolio Highlights

- RAG-based pre-sales knowledge assistant with source-grounded answers.
- Multi-Agent Workflow: Planner, Retrieval, Risk Review, Critic, Answer, Email Draft, Memory Manager.
- Tool Registry and Safe Executor for lightweight tool governance.
- Risk Review for pricing, SLA, compliance, private deployment, roadmap, and customer-reference questions.
- Critic / grounding check to reduce unsupported claims.
- Memory Compression that avoids saving hallucinated or unsupported facts.
- Agent Trace JSONL for debugging, eval, screenshots, and interview explanation.
- Agent Eval with 22/22 overall_pass on the current portfolio dataset.

# AI 售前助手项目

> RAG + LLM Client + Evaluation + Guardrails + Lightweight Tracing + Streamlit Demo
> 面向 B2B SaaS 售前场景的 RAG + LLM 应用工程项目

---

## Agent Workbench V2.0 Engineering Workflow

Agent Workbench V2.0 是在 V1 workflow 上做的工程增强版，目标是更稳定、更容易运行、更容易评估、更容易演示。它仍然保持轻量：不引入 PostgreSQL、Redis、OpenSearch、Airflow、Docker Compose、MCP、LangGraph，也不把作品集项目改造成复杂生产系统。

### V2.0 运行命令

默认 demo question：

```bash
python -m agent_workbench.harness.agent_orchestrator
```

指定客户问题：

```bash
python -m agent_workbench.harness.agent_orchestrator --question "Can InsightFlow support private deployment and SLA?"
```

不写 trace：

```bash
python -m agent_workbench.harness.agent_orchestrator --question "Can InsightFlow support private deployment and SLA?" --no-trace
```

评估：

```bash
python eval/run_agent_eval.py
```

Smoke test：

```bash
python scripts/run_agent_workbench_smoke_test.py
```

### V2.0 工程增强点

- 新增 `AnswerAgent`：输入 user_question、retrieved_sources、risk_decision，输出 raw_answer 和 final_answer，并避免 unsupported commitment。
- Orchestrator CLI 支持 `--question`、`--no-trace` 和默认 demo question；命令式输入不会被当成售前问题回答。
- Retrieval Agent 保持 Chroma 优先、Markdown fallback；没有 chromadb 时不会崩溃，会记录 `retrieval_mode`、`original_query`、`rewritten_query`、`retrieval_attempts`。
- Markdown fallback 支持 query rewrite：当 top sources 分数过低或无结果时，自动扩展查询再检索一次。
- Risk Review 覆盖 pricing、SLA、HIPAA、GDPR、SOC2、private deployment、customer case、roadmap、legal、security、integration；高风险问题必须 human review。
- Critic 对 pricing、SLA、HIPAA、customer case、private deployment 等 unsupported claim 更严格；source 不足时标记 uncertain 或 partially_supported。
- Email Agent 只生成 draft，不发送；高风险邮件会加入 cautious wording，并清理明显 unsupported commitment。
- Memory Manager 不保存用户命令、脚本命令或 unsupported claim 作为 confirmed facts，只保留客户需求、风险关注点、open questions、next actions。
- Output Validator 增加 `parse_json_safely` 和 `repair_json_once`，JSON parse error 不会打断 workflow。
- Tool Registry 增加简化 input_schema/output_schema，Safe Executor 在执行前后做基础校验。

### V2.0 Fallback 说明

当前本地环境如果没有 `chromadb`，Retrieval Agent 会记录：

```text
Chroma retrieval unavailable: ModuleNotFoundError: No module named 'chromadb'
```

随后自动使用 Markdown fallback 检索 `knowledge_base/*.md`。这不是失败，而是为了保证 demo 可以在轻量环境中运行。对于非售前问题或脚本命令，系统会返回安全提示，不会编造产品答案。

### V2.0 Eval 输出

评估数据集扩展到 22 条，覆盖 product feature、pricing、SLA、HIPAA、GDPR、SOC2、private deployment、customer case、roadmap、security、integration、memory、invalid/non-sales question。

输出文件：

```text
eval/agent_eval_results.csv
docs/agent_eval_report_v2.md
```

报告包含 pass rate、失败案例、风险案例表现、average_latency_ms、max_latency_ms，并保留 `overall_pass`。

### V2.0 面试亮点

- 展示从 RAG QA 到 agentic workflow 的演进，同时保持工程克制。
- 能解释 Planner、Retrieval、Risk Review、Critic、Answer、Email、Memory 的职责边界。
- 有 Tool Registry、Safe Executor、Output Validator，体现 agent tool governance 和 graceful fallback。
- 有 trace、eval、report、smoke test，便于现场 demo 和工程复盘。
- 明确把 unsupported claims 拦在最终答案、邮件草稿和 memory confirmed facts 之外。

---

## Agent Workbench V2 / AI Presales Agent Workbench

本项目在原有 RAG-based AI Pre-sales Knowledge Assistant 基础上，新增了一个轻量级、可运行、可测试、可追踪的 **AI Pre-sales Agent Workbench**。V1 目标不是堆复杂框架，而是把售前问答中的关键工程能力串成完整 workflow：planning、tool execution、retrieval、risk review、critic grounding check、email draft、memory、trace 和 eval。

### 架构说明

```text
User Question
-> Memory Manager
-> Planner Agent
-> Safe Executor
-> Retrieval Agent
-> raw answer
-> Risk Review Agent
-> Critic Agent
-> final answer
-> Email Agent
-> Memory Manager
-> Agent Trace
```

核心模块：

- `agent_workbench/schemas/agent_schemas.py`：统一 dataclass schema，包括 PlannerOutput、RetrievedSource、RiskDecision、CriticDecision、EmailDraft、MemorySummary、AgentRunState。
- `agent_workbench/harness/tool_registry.py`：注册允许调用的 tools，避免 agent 任意调用函数。
- `agent_workbench/harness/safe_executor.py`：统一执行 tools，捕获异常、超时和 fallback。
- `agent_workbench/harness/output_validator.py`：校验 agent 输出，非法输出会转成安全 fallback。
- `agent_workbench/agents/retrieval_agent.py`：封装现有 Chroma RAG 检索，按 risk_level 调整 top_k；如果 Chroma import 或运行失败，会 fallback 到本地 Markdown 检索并写入 trace errors。
- `agent_workbench/agents/risk_review_agent.py`：识别 pricing、SLA、HIPAA、compliance、private deployment、customer case、security、roadmap、legal 等售前风险。
- `agent_workbench/agents/critic_agent.py`：检查 final/raw answer 中高风险 claim 是否被 retrieved sources 支持；unsupported claim 会触发 revision_required。
- `agent_workbench/agents/email_agent.py`：生成 follow-up email draft，只生成草稿，不发送。
- `agent_workbench/agents/memory_manager.py`：实现 short-term memory、session memory、customer profile memory 和 memory compression；unsupported claims 不会进入 confirmed facts。
- `agent_workbench/harness/agent_orchestrator.py`：串联完整 agent workflow，并写入 JSONL trace。

本阶段刻意不引入 PostgreSQL、Redis、OpenSearch、Airflow、Docker Compose、MCP、LangGraph，保持作品集项目可以本地运行、可以截图、可以讲清楚。

### 运行命令

```bash
python -m agent_workbench.harness.agent_orchestrator
```

运行后输入客户问题，例如：

```text
Can InsightFlow AI support private deployment and HIPAA compliance?
```

每次运行会写入一行 trace：

```text
agent_workbench/traces/agent_traces.jsonl
```

Trace 字段包括 run_id、timestamp、user_question、planner_output、tools_called、retrieved_sources、raw_answer、risk_decision、critic_decision、final_answer、email_draft、memory_summary、human_review_required、latency_ms、errors。

### 评估命令

```bash
python eval/run_agent_eval.py
```

评估数据集：

```text
eval/agent_eval_dataset.csv
```

覆盖 10 类售前场景：product feature、pricing、SLA、private deployment、HIPAA、customer case、integration、roadmap、security、memory。

输出结果：

```text
eval/agent_eval_results.csv
```

评估维度包括 intent_pass、tool_selection_pass、risk_classification_pass、refusal_or_safe_answer_pass、email_draft_pass、memory_retention_pass、overall_pass。

### 面试亮点

- 从单次 RAG QA 升级为多 agent workflow，能解释每一步的职责边界。
- Safe Executor + Tool Registry 展示了 agentic system 里的 tool governance。
- Risk Review + Critic 分工清晰：前者判断售前风险，后者检查 grounding 和 unsupported claims。
- Retrieval Agent 对现有 Chroma RAG 做兼容封装，依赖不可用时 graceful fallback，不影响整体 demo。
- Agent Trace 使用 JSONL，方便调试、评估、截图和复盘。
- Memory Manager 明确区分 confirmed facts 与 unsupported claims，避免把未证实内容沉淀为客户记忆。
- Eval 脚本跑完整 workflow，而不是只测单点函数，更接近真实 AI application engineering。

---

## 1. Project Overview / 项目概览

**AI Pre-sales Copilot** is a portfolio project for B2B SaaS pre-sales, AI Solutions, and LLM application engineering scenarios.

It upgrades a basic RAG-based pre-sales knowledge assistant into a more complete AI application workflow:

```text
Markdown knowledge base
→ document loading
→ chunking
→ sentence-transformers embeddings
→ Chroma vector store
→ semantic retrieval
→ Mock/API LLM client
→ grounded answer generation
→ hallucination guardrails
→ evaluation
→ lightweight tracing
→ Streamlit demo
```

中文说明：

**AI Pre-sales Copilot** 是一个面向 B2B SaaS 售前、AI Solutions、LLM 应用工程方向的求职作品集项目。

它从一个基础的 RAG 售前知识库助手，升级成了一个更完整的 AI 应用系统：

```text
Markdown 知识库
→ 文档加载
→ 文档切分
→ sentence-transformers embedding
→ Chroma 向量数据库
→ 语义检索
→ Mock/API 双模式 LLM Client
→ 基于来源的结构化回答
→ 幻觉控制与拒答
→ RAG Evaluation
→ 轻量 tracing
→ Streamlit 展示页面
```

This project does **not** train a foundation model from scratch.
It focuses on practical LLM application engineering: retrieval, grounding, evaluation, tracing, feedback, and demo delivery.

本项目不是训练大模型，也不是算法研究项目。
它重点展示实用的 LLM 应用工程能力：检索、来源引用、评估、tracing、反馈闭环和 Demo 交付。

---

## 2. Business Problem / 业务问题

In B2B SaaS pre-sales scenarios, customers often ask questions such as:

* Can the product support private deployment?
* Can it connect to MySQL, Power BI, or other business systems?
* How does the system reduce hallucination risk?
* What pricing or packaging options are available?
* Can the assistant generate customer-facing follow-up emails?
* Can the answer be traced back to reliable product documentation?

中文说明：

在 B2B SaaS 售前场景中，客户经常会问：

* 产品是否支持私有化部署？
* 是否能连接 MySQL、Power BI 或其他业务系统？
* 系统如何降低幻觉风险？
* 有哪些价格或套餐方案？
* 是否能生成面向客户的英文跟进邮件？
* 回答是否能追溯到可靠的产品文档？

Traditional manual pre-sales support can be slow, inconsistent, and hard to trace.
A generic chatbot may also generate unsupported claims if it is not grounded in the company knowledge base.

传统人工售前支持可能响应慢、回答不一致、缺少来源依据。
如果直接使用通用聊天机器人，也可能生成没有文档依据的回答。

This project uses a RAG-based workflow to improve consistency, source grounding, and reviewability.

本项目通过 RAG 流程提升回答的一致性、可追溯性和可审核性。

---

## 3. Key Features / 核心功能

### English

* Local Markdown-based pre-sales knowledge base
* Document chunking and metadata tracking
* Sentence-transformers embeddings
* Chroma local vector store
* Semantic Top-K retrieval
* Mock/API dual-mode LLM client
* Structured answer output
* Source-grounded response generation
* Confidence display
* Missing information extraction
* Suggested customer follow-up
* Hallucination guardrails
* Rule-based refusal for unsupported questions
* Lightweight RAG evaluation pipeline
* Query tracing with JSONL logs
* User feedback logging
* Streamlit demo UI

### 中文

* 本地 Markdown 售前知识库
* 文档切分与 metadata 记录
* sentence-transformers embedding
* Chroma 本地向量数据库
* Top-K 语义检索
* Mock/API 双模式 LLM Client
* 结构化回答输出
* 基于来源的回答生成
* 置信度展示
* 缺失信息提示
* 客户后续跟进建议
* 幻觉控制机制
* 对无依据问题进行规则拒答
* 轻量 RAG Evaluation 流程
* JSONL query tracing 日志
* 用户反馈记录
* Streamlit 可交互 Demo 页面

---

## 4. Architecture / 架构流程

```text
User Question
    ↓
Embedding Model
    ↓
Chroma Vector Store
    ↓
Top-K Retrieved Chunks
    ↓
Similarity Score + Source Metadata
    ↓
Hallucination Guardrails
    ↓
Mock/API LLM Client
    ↓
Structured Grounded Answer
    ↓
Tracing + Feedback Logging
    ↓
Streamlit Demo / CLI Output
```

中文理解：

```text
用户问题
    ↓
Embedding 模型
    ↓
Chroma 向量数据库
    ↓
Top-K 检索结果
    ↓
相似度分数 + 来源 metadata
    ↓
幻觉控制与拒答判断
    ↓
Mock/API 双模式 LLM Client
    ↓
结构化来源回答
    ↓
Tracing + 用户反馈日志
    ↓
Streamlit 页面 / 命令行输出
```

---

## 5. Tech Stack / 技术栈

| Area            | Tools                                        |
| --------------- | -------------------------------------------- |
| Language        | Python                                       |
| Retrieval       | sentence-transformers, Chroma                |
| Vector Store    | ChromaDB                                     |
| LLM Client      | Mock mode, OpenAI-compatible API mode        |
| Configuration   | python-dotenv, `.env`, `.env.example`        |
| Evaluation      | CSV dataset, custom Python evaluation script |
| Observability   | JSONL query logs, CSV feedback logs          |
| Demo UI         | Streamlit                                    |
| Version Control | Git, GitHub                                  |

中文说明：

| 模块         | 工具                                    |
| ---------- | ------------------------------------- |
| 编程语言       | Python                                |
| 检索         | sentence-transformers, Chroma         |
| 向量数据库      | ChromaDB                              |
| LLM Client | Mock 模式，OpenAI-compatible API 模式      |
| 配置管理       | python-dotenv, `.env`, `.env.example` |
| 评估         | CSV 测试集，自定义 Python 评估脚本               |
| 可观测性       | JSONL query logs，CSV 用户反馈日志           |
| 展示页面       | Streamlit                             |
| 版本管理       | Git, GitHub                           |

---

## 6. Project Structure / 项目结构

```text
RAG-based-AI-Presales-Knowledge-Assistant/
│
├── rag_app/
│   ├── build_vector_store.py
│   ├── chunk_documents.py
│   ├── embedding_client.py
│   ├── generate_answer_chroma.py
│   ├── llm_client.py
│   ├── main_chroma.py
│   ├── retrieve_context_chroma.py
│   └── trace_logger.py
│
├── eval/
│   ├── eval_dataset.csv
│   ├── eval_results.csv
│   ├── run_eval.py
│   └── sample_eval_questions.csv
│
├── knowledge_base/
│   ├── 01_product_overview.md
│   ├── 02_faq.md
│   ├── 03_pricing_and_packaging.md
│   ├── 04_deployment_guide.md
│   ├── 05_security_and_governance.md
│   ├── 06_integrations_and_api.md
│   ├── 07_customer_case_studies.md
│   ├── 08_objection_handling.md
│   └── 09_presales_email_templates.md
│
├── docs/
│   ├── architecture.md
│   ├── demo_guide.md
│   ├── demo_guide_zh.md
│   ├── evaluation_report.md
│   ├── observability_notes.md
│   ├── observability_notes_zh.md
│   ├── project_explanation_zh.md
│   └── interview_pitch.md
│
├── app_streamlit.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 7. Setup / 环境准备

### 7.1 Enter Project Directory / 进入项目目录

```cmd
cd /d D:\chatgpt\RAG-based-AI-Presales-Knowledge-Assistant
```

### 7.2 Create Virtual Environment / 创建虚拟环境

```cmd
python -m venv .venv
```

### 7.3 Install Dependencies / 安装依赖

```cmd
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 7.4 Environment Variables / 环境变量

Copy `.env.example` to `.env`:

```cmd
copy .env.example .env
```

Default local mode:

```env
LLM_MODE=mock
LLM_PROVIDER=openai
LLM_MODEL=gpt-5.5
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
```

中文说明：

默认使用 `mock` 模式，不需要 API Key，也不会产生 API 成本。

如果后续要切换真实 API，可以把：

```env
LLM_MODE=mock
```

改成：

```env
LLM_MODE=api
```

注意：

```text
.env 不提交 GitHub
.env.example 可以提交 GitHub
```

---

## 8. Build Vector Store / 构建向量库

If the vector store does not exist, run:

```cmd
.\.venv\Scripts\python.exe rag_app\build_vector_store.py
```

This builds a Chroma vector store from Markdown files in:

```text
knowledge_base/
```

The generated vector store is saved under:

```text
vector_store/
```

中文说明：

如果本地没有向量库，先运行上面的命令。
它会读取 `knowledge_base/` 下的 Markdown 文档，并构建 Chroma 本地向量数据库。

`vector_store/` 可以本地重建，所以不会提交到 GitHub。

---

## 9. Run CLI Demo / 运行命令行 Demo

```cmd
.\.venv\Scripts\python.exe rag_app\main_chroma.py
```

Example question:

```text
Can InsightFlow AI support private deployment?
```

Exit:

```text
exit
```

Generated output:

```text
outputs/sample_answer_chroma.md
```

中文说明：

命令行版本适合快速测试 RAG 检索和回答生成流程。
回答会保存到 `outputs/sample_answer_chroma.md`。

---

## 10. Run Streamlit Demo / 运行 Streamlit 页面

```cmd
.\.venv\Scripts\streamlit.exe run app_streamlit.py --server.fileWatcherType none
```

Then open:

```text
http://localhost:8501
```

The Streamlit page supports:

* Customer question input
* Structured AI answer display
* Intent display
* LLM mode display
* Confidence display
* Source table
* Retrieved chunks expander
* Human review reminder
* Thumbs up / thumbs down feedback

中文说明：

Streamlit 页面可以作为作品集展示入口。
它支持输入客户问题、查看结构化回答、查看来源表格、展开 retrieved chunks，并提交用户反馈。

---

## 11. Recommended Test Questions / 推荐测试问题

### 11.1 Deployment / 部署问题

```text
Can InsightFlow AI support private deployment?
```

Expected behavior:

* Retrieves product, FAQ, security, or deployment-related chunks.
* Shows confidence and sources.
* Suggests confirming architecture, deployment preference, and security requirements.

中文预期：

* 检索产品、FAQ、安全治理或部署相关文档。
* 展示置信度和来源。
* 建议进一步确认客户架构、部署偏好和安全要求。

---

### 11.2 Hallucination Guardrail / 幻觉控制测试

```text
Can InsightFlow AI guarantee stock trading profits?
```

Expected behavior:

* The system should refuse to answer.
* LLM mode should be:

```text
rule_based_refusal
```

* The answer should explain that the knowledge base does not support this claim.

中文预期：

* 系统应该拒答。
* LLM mode 应显示 `rule_based_refusal`。
* 回答应说明知识库没有依据支持“保证股票收益”这种承诺。

---

### 11.3 Security / 安全问题

```text
How does the assistant reduce hallucinations?
```

Expected behavior:

* Retrieves security and governance content.
* Mentions retrieved context, source references, human review, and evaluation.

中文预期：

* 检索安全治理文档。
* 回答应提到 retrieved context、source references、human review 和 evaluation。

---

### 11.4 Integration / 集成问题

```text
Can InsightFlow AI connect to MySQL and Power BI?
```

Expected behavior:

* Retrieves integration and deployment documents.
* Mentions data sources, BI workflows, refresh, and integration requirements.

中文预期：

* 检索集成和部署文档。
* 回答应提到数据源、BI 工作流、刷新和系统集成要求。

---

## 12. Structured Output / 结构化输出

The generated answer includes:

```text
answer
sources
confidence
missing_info
suggested_follow_up
```

中文说明：

系统输出不只是普通自然语言回答，而是包含：

```text
回答正文
来源引用
置信度
缺失信息
建议追问
```

This makes the answer more useful for pre-sales and solution consultant scenarios.

这让回答更适合售前和解决方案顾问场景。

---

## 13. Hallucination Guardrails / 幻觉控制

The system includes lightweight guardrails before LLM generation.

It refuses to answer when:

* The question is clearly outside the product pre-sales scope.
* Retrieved evidence is too weak.
* The knowledge base does not support the claim.

中文说明：

系统在调用 LLM 生成前加入了轻量拒答机制。

当出现以下情况时，系统会拒答：

* 问题明显超出产品售前知识库范围
* 检索证据太弱
* 知识库没有依据支持该承诺

Example:

```text
Can InsightFlow AI guarantee stock trading profits?
```

The system refuses instead of inventing unsupported financial claims.

对于这种问题，系统会拒答，而不是编造没有依据的金融收益承诺。

---

## 14. RAG Evaluation / RAG 评估

Run evaluation:

```cmd
.\.venv\Scripts\python.exe eval\run_eval.py
```

Evaluation dataset:

```text
eval/eval_dataset.csv
```

Generated files:

```text
eval/eval_results.csv
docs/evaluation_report.md
```

Current evaluation metrics:

```text
retrieval_hit_rate
source_accuracy
answer_keyword_coverage
low_confidence_refusal_count
```

中文说明：

本项目包含轻量 RAG Evaluation 流程，用来评估：

```text
检索命中率
来源准确性
回答关键词覆盖率
低置信度拒答数量
```

这说明项目不只是“能回答”，还可以量化检查 RAG 质量。

---

## 15. Observability and Tracing / 可观测性与 Tracing

The project includes a custom lightweight tracing module:

```text
rag_app/trace_logger.py
```

Query traces are written to:

```text
logs/query_logs.jsonl
```

User feedback is written to:

```text
logs/user_feedback.csv
```

Each query log includes:

```text
timestamp
user_query
retrieved_sources
top_k_chunks
similarity_scores
prompt_version
llm_mode
answer
confidence
latency_ms
error_message
```

中文说明：

项目加入了轻量 tracing，不只是输出最终答案，还会记录每次问答的运行链路：

```text
用户问题
检索来源
Top-K chunks
相似度分数
prompt 版本
LLM 模式
回答预览
置信度
耗时
错误信息或拒答原因
```

这有助于排查问题到底出在检索、prompt、LLM 生成，还是知识库本身。

---

## 16. User Feedback Loop / 用户反馈闭环

The Streamlit demo supports:

```text
Helpful
Not helpful
```

Feedback records are saved to:

```text
logs/user_feedback.csv
```

中文说明：

Streamlit 页面支持用户反馈。
后续这些反馈可以用于优化：

* evaluation dataset
* prompt design
* retrieval quality
* refusal thresholds
* knowledge base coverage

---

## 17. Why Mock/API Mode / 为什么要做 Mock/API 双模式

### English

Mock mode allows local development without API costs.
API mode allows future connection to real LLM providers.

The rest of the RAG pipeline calls a unified `llm_client.py`, so the system is not tightly coupled to one specific provider.

### 中文

Mock 模式可以在没有 API Key、不消耗成本的情况下测试完整流程。
API 模式则用于后续接入真实大模型。

RAG 主流程只调用统一的 `llm_client.py`，这样系统不会和某一个模型供应商强绑定。

---

## 18. Why Not LangChain First / 为什么没有一开始用 LangChain

This project intentionally implements the RAG pipeline manually first.

The goal is to understand:

```text
document loading
chunking
embedding
vector store
retrieval
prompt construction
LLM call
source grounding
evaluation
tracing
refusal logic
```

LangChain can be added later as an optional comparison, but the main project keeps the core logic transparent and easy to explain.

中文说明：

本项目先手写 RAG 主流程，而不是一开始就用 LangChain 重构。

原因是：
求职作品集最重要的是说明自己理解底层流程，而不是只会调用框架。

后期可以加一个 LangChain 对照版本，但主流程保留手写实现，方便面试讲解。

---

## 19. Key Documents / 关键文档

```text
docs/demo_guide.md
docs/demo_guide_zh.md
docs/evaluation_report.md
docs/observability_notes.md
docs/observability_notes_zh.md
docs/project_explanation_zh.md
docs/interview_pitch.md
docs/architecture.md
```

中文说明：

这些文档分别用于：

* Demo 运行说明
* 中文 Demo 说明
* Evaluation 报告
* Observability 说明
* 中文 Observability 说明
* 中文项目解释
* 面试 Pitch
* 架构说明

---

## 20. Interview Explanation / 面试表达

### English Version

> I upgraded a RAG-based pre-sales knowledge assistant into an AI Pre-sales Copilot. It uses sentence-transformers and Chroma for semantic retrieval, includes a provider-switchable LLM client with mock/API modes, generates structured source-grounded answers, adds hallucination guardrails, evaluates retrieval and answer quality, logs query traces and feedback, and provides a Streamlit demo for interactive testing.

### 中文版本

> 我把原来的 RAG 售前知识库助手升级成了 AI Pre-sales Copilot。它使用 sentence-transformers 和 Chroma 做语义检索，封装了 Mock/API 双模式 LLM Client，可以生成结构化、带来源引用的回答，并加入了幻觉控制、RAG Evaluation、query tracing、用户反馈记录和 Streamlit 展示页面。

### Short English Version

> This project demonstrates practical LLM application engineering: RAG, LLM API abstraction, evaluation, hallucination control, observability, feedback logging, and demo delivery.

### 中文简洁版

> 这个项目展示的是实用 LLM 应用工程能力，包括 RAG、LLM API 抽象、评估、幻觉控制、可观测性、反馈记录和 Demo 交付。

---

## 21. Portfolio Value / 作品集价值

This project demonstrates skills relevant to:

* AI Solutions Intern
* LLM Application Engineer Intern
* AI Pre-sales Intern
* Technical Consultant Intern
* AI Product / Technical Operations Intern

中文说明：

这个项目适合用于申请：

* AI Solutions Intern
* LLM Application Engineer Intern
* AI Pre-sales Intern
* Technical Consultant Intern
* AI 产品 / 技术运营实习

It shows that the project is not just a simple chatbot, but a structured AI application with retrieval, grounding, evaluation, guardrails, tracing, feedback, and demo delivery.

它说明这个项目不是简单聊天机器人，而是一个包含检索、来源引用、评估、拒答机制、tracing、反馈闭环和展示页面的结构化 AI 应用项目。

---

## 22. Current Status / 当前状态

Implemented:

```text
Manual RAG pipeline
Chroma semantic retrieval
Mock/API LLM client
Structured grounded answers
Hallucination guardrails
RAG evaluation pipeline
Lightweight tracing
User feedback logging
Streamlit demo
Bilingual documentation
```

中文说明：

目前已完成：

```text
手写 RAG 流程
Chroma 语义检索
Mock/API 双模式 LLM Client
结构化来源回答
幻觉控制与拒答
RAG Evaluation
轻量 tracing
用户反馈记录
Streamlit Demo
中英双语文档
```

Potential next steps:

```text
FastAPI service
Dockerfile
Lightweight tool-calling workflow
Optional LangChain comparison
Optional LangSmith tracing
```

后续可升级方向：

```text
FastAPI 服务化
Dockerfile 容器化
轻量 tool-calling workflow
LangChain 对照版本
LangSmith tracing 对照
```
