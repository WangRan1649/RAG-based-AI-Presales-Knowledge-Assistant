# Demo Guide 中文版：AI Pre-sales Copilot 演示说明

## 1. 项目概览

AI Pre-sales Copilot 是一个面向 B2B SaaS 售前与 AI Solutions 场景的求职作品集项目。

它从一个基础的 RAG 售前知识库助手，升级成了一个更完整的 AI 应用工作流：

```text
RAG 检索
→ Mock/API 双模式 LLM Client
→ 结构化回答生成
→ 来源引用
→ 置信度展示
→ 幻觉控制与拒答
→ 轻量 tracing
→ 用户反馈记录
→ Streamlit Demo 页面
```

这个项目的目标不是训练大模型，也不是做算法研究，而是展示实用的 LLM Application Engineering 能力。

---

## 2. 这个 Demo 展示什么

Streamlit Demo 支持用户：

* 输入客户售前问题
* 从知识库中检索相关 chunks
* 生成结构化 AI 回答
* 查看问题意图
* 查看 LLM 模式
* 查看置信度
* 查看来源引用
* 展开查看 retrieved chunks
* 测试超出知识库范围的问题是否会被拒答
* 提交 thumbs up / thumbs down 用户反馈

---

## 3. 环境准备

进入项目根目录：

```cmd
cd /d D:\chatgpt\RAG-based-AI-Presales-Knowledge-Assistant
```

安装依赖：

```cmd
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

当前项目主要依赖：

```text
scikit-learn
sentence-transformers
chromadb
python-dotenv
openai
streamlit
```

---

## 4. 构建或重建向量库

如果本地 Chroma 向量库不存在，需要先运行：

```cmd
.\.venv\Scripts\python.exe rag_app\build_vector_store.py
```

这个命令会读取：

```text
knowledge_base/
```

下面的 Markdown 产品知识库文档，并构建本地向量数据库。

向量库会保存到：

```text
vector_store/
```

`vector_store/` 不提交到 GitHub，因为它可以在本地重新生成。

---

## 5. 运行命令行版本

如果要测试命令行版本，输入：

```cmd
.\.venv\Scripts\python.exe rag_app\main_chroma.py
```

示例问题：

```text
Can InsightFlow AI support private deployment?
```

退出命令：

```text
exit
```

生成的回答会保存到：

```text
outputs/sample_answer_chroma.md
```

---

## 6. 运行 Streamlit Demo

启动 Streamlit 页面：

```cmd
.\.venv\Scripts\streamlit.exe run app_streamlit.py --server.fileWatcherType none
```

然后打开：

```text
http://localhost:8501
```

这里使用：

```text
--server.fileWatcherType none
```

是为了减少 Streamlit 对 Transformers 等大型 ML 库进行文件监听时产生的无关 warning。

---

## 7. 推荐测试问题

### 测试 1：部署问题

```text
Can InsightFlow AI support private deployment?
```

预期效果：

* 系统会检索产品说明、FAQ、安全治理或部署相关文档。
* 回答会说明部署需要结合客户架构、部署偏好和安全要求确认。
* 回答会展示 confidence、missing information、suggested follow-up 和 sources。

---

### 测试 2：幻觉控制 / 拒答问题

```text
Can InsightFlow AI guarantee stock trading profits?
```

预期效果：

* 系统应该拒答。
* LLM mode 应该显示：

```text
rule_based_refusal
```

* 回答应该说明知识库没有依据支持这个承诺。
* 系统不能编造任何“保证股票收益”的结论。

这个测试展示的是 hallucination control 和 grounded refusal 能力。

---

### 测试 3：安全治理问题

```text
How does the assistant reduce hallucinations?
```

预期效果：

* 系统应该检索安全治理相关文档。
* 回答应该提到 retrieved context、source references、human review 和 evaluation。

---

### 测试 4：集成问题

```text
Can InsightFlow AI connect to MySQL and Power BI?
```

预期效果：

* 系统应该检索集成与部署相关文档。
* 回答应该提到 data sources、BI workflows、refresh 和 system integration。

---

## 8. 用户反馈记录

Streamlit Demo 支持两个反馈按钮：

```text
Helpful
Not helpful
```

反馈会保存在本地：

```text
logs/user_feedback.csv
```

每条反馈记录包括：

```text
timestamp
user_query
feedback
comment
answer_preview
```

`logs/` 目录不会提交到 GitHub，因为它可能包含用户问题和生成回答。

---

## 9. Query Tracing

每次问答都会记录到：

```text
logs/query_logs.jsonl
```

每条 query trace 包含：

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

这些日志可以帮助排查：

* 检索失败
* 来源不相关
* 相似度太低
* 拒答逻辑是否生效
* 当前使用 mock、api 还是 rule_based_refusal
* 响应耗时问题
* prompt 版本效果

---

## 10. 运行 RAG Evaluation

运行轻量评估流程：

```cmd
.\.venv\Scripts\python.exe eval\run_eval.py
```

评估数据集：

```text
eval/eval_dataset.csv
```

运行后会生成：

```text
eval/eval_results.csv
docs/evaluation_report.md
```

当前评估指标包括：

```text
retrieval_hit_rate
source_accuracy
answer_keyword_coverage
low_confidence_refusal_count
```

---

## 11. Mock 模式和 API 模式

项目支持两种 LLM 模式：

```text
mock
api
```

默认是 mock 模式，通过 `.env` 配置：

```env
LLM_MODE=mock
LLM_PROVIDER=openai
LLM_MODEL=gpt-5.5
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
```

Mock 模式可以在没有 API Key、不消耗 API 成本的情况下测试完整流程。

后续如果要切换真实 API，可以把：

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

## 12. 面试表达

英文简洁版：

> I upgraded a RAG-based pre-sales knowledge assistant into an AI Pre-sales Copilot. It includes semantic retrieval with Chroma, a provider-switchable LLM client with mock/API modes, structured grounded answers, hallucination guardrails, a lightweight evaluation pipeline, query tracing, user feedback logging, and a Streamlit demo.

中文理解：

> 我把原来的 RAG 售前知识库助手升级成了 AI Pre-sales Copilot。它包括 Chroma 语义检索、Mock/API 双模式 LLM Client、结构化回答、来源引用、低置信度拒答、RAG Evaluation、轻量 tracing、用户反馈记录和 Streamlit 展示页面。

更口语化面试版：

> 这个项目不是单纯调用大模型回答问题。我先手写了 RAG 检索流程，再接入 Mock/API 双模式 LLM Client，加入来源引用、置信度、拒答机制、评估脚本和 tracing，最后用 Streamlit 做成一个可交互 Demo。这样面试官可以直接看到系统如何回答客户问题、如何引用来源、如何拒答超出知识库范围的问题。

---

## 13. 作品集价值

这个 Demo 展示了以下 AI 应用工程能力：

```text
RAG pipeline design
LLM API abstraction
Mock/API development mode
Source grounding
Hallucination control
Evaluation dataset design
Retrieval quality measurement
Lightweight observability
User feedback loop
Streamlit demo delivery
```

中文对应能力：

```text
RAG 流程设计
LLM API 抽象封装
Mock/API 双模式开发
来源引用与回答 grounding
幻觉控制与拒答机制
评估数据集设计
检索质量评估
轻量可观测性
用户反馈闭环
Streamlit Demo 交付
```

这个项目适合用于申请：

```text
AI Solutions Intern
LLM Application Engineer Intern
AI Pre-sales Intern
Technical Consultant Intern
AI Product / Technical Operations Intern
```





# Demo Guide: AI Pre-sales Copilot

## 1. Project Overview

AI Pre-sales Copilot is a portfolio project for B2B SaaS pre-sales and AI solution scenarios.

It upgrades a basic RAG-based knowledge assistant into a more complete AI application workflow:

```text
RAG retrieval
→ Mock/API LLM client
→ Structured answer generation
→ Source grounding
→ Confidence display
→ Hallucination guardrails
→ Lightweight tracing
→ User feedback logging
→ Streamlit demo
```

The goal is to demonstrate practical LLM application engineering skills rather than model training or algorithm research.

---

## 2. What This Demo Shows

The Streamlit demo allows users to:

* Enter a customer pre-sales question
* Retrieve relevant knowledge base chunks
* Generate a structured AI answer
* View detected intent
* View LLM mode
* View confidence
* View source references
* Inspect retrieved chunks
* Test refusal behavior for unsupported questions
* Submit thumbs up / thumbs down feedback

---

## 3. Environment Setup

From the project root:

```cmd
cd /d D:\chatgpt\RAG-based-AI-Presales-Knowledge-Assistant
```

Install dependencies:

```cmd
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The project uses:

```text
scikit-learn
sentence-transformers
chromadb
python-dotenv
openai
streamlit
```

---

## 4. Build or Rebuild the Vector Store

If the Chroma vector store does not exist, run:

```cmd
.\.venv\Scripts\python.exe rag_app\build_vector_store.py
```

This builds the local vector database from Markdown files in:

```text
knowledge_base/
```

The vector store is saved under:

```text
vector_store/
```

The `vector_store/` directory is ignored by Git because it can be rebuilt locally.

---

## 5. Run the Command-Line Version

To test the command-line version:

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

The generated answer will be saved to:

```text
outputs/sample_answer_chroma.md
```

---

## 6. Run the Streamlit Demo

Start the Streamlit UI:

```cmd
.\.venv\Scripts\streamlit.exe run app_streamlit.py --server.fileWatcherType none
```

Then open:

```text
http://localhost:8501
```

The `--server.fileWatcherType none` option is used to reduce unnecessary watcher warnings from large ML libraries such as Transformers.

---

## 7. Recommended Test Questions

### Test 1: Deployment Question

```text
Can InsightFlow AI support private deployment?
```

Expected behavior:

* The system retrieves relevant product, FAQ, security, or deployment-related chunks.
* The answer explains that implementation depends on architecture, deployment preference, and security requirements.
* The answer includes confidence, missing information, suggested follow-up, and sources.

---

### Test 2: Hallucination Guardrail Question

```text
Can InsightFlow AI guarantee stock trading profits?
```

Expected behavior:

* The system should refuse to answer.
* LLM mode should show:

```text
rule_based_refusal
```

* The answer should explain that the knowledge base does not support this claim.
* The system should not invent any financial guarantee.

This demonstrates hallucination control and grounded refusal behavior.

---

### Test 3: Security Question

```text
How does the assistant reduce hallucinations?
```

Expected behavior:

* The system should retrieve security and governance content.
* The answer should mention retrieved context, source references, human review, and evaluation.

---

### Test 4: Integration Question

```text
Can InsightFlow AI connect to MySQL and Power BI?
```

Expected behavior:

* The system should retrieve integration and deployment-related documents.
* The answer should mention data sources, BI workflows, refresh, and system integration.

---

## 8. Feedback Logging

The Streamlit demo supports feedback buttons:

```text
Helpful
Not helpful
```

Feedback is saved locally to:

```text
logs/user_feedback.csv
```

Each feedback record includes:

```text
timestamp
user_query
feedback
comment
answer_preview
```

The logs directory is ignored by Git because it may contain user questions or generated answers.

---

## 9. Query Tracing

Each query is logged to:

```text
logs/query_logs.jsonl
```

Each query trace includes:

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

This helps debug:

* Retrieval failures
* Irrelevant sources
* Weak similarity scores
* Refusal behavior
* LLM mode
* Latency issues
* Prompt version behavior

---

## 10. Run RAG Evaluation

To run the lightweight evaluation pipeline:

```cmd
.\.venv\Scripts\python.exe eval\run_eval.py
```

The evaluation uses:

```text
eval/eval_dataset.csv
```

It generates:

```text
eval/eval_results.csv
docs/evaluation_report.md
```

Current metrics include:

```text
retrieval_hit_rate
source_accuracy
answer_keyword_coverage
low_confidence_refusal_count
```

---

## 11. Mock Mode and API Mode

The project supports two LLM modes:

```text
mock
api
```

The default mode is mock mode, configured in:

```text
.env
```

Example:

```env
LLM_MODE=mock
LLM_PROVIDER=openai
LLM_MODEL=gpt-5.5
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
```

Mock mode allows local testing without API costs.

API mode can be enabled later by changing:

```env
LLM_MODE=api
```

Do not commit `.env` to GitHub.
Only `.env.example` should be committed.

---

## 12. Interview Explanation

A concise English explanation:

> I upgraded a RAG-based pre-sales knowledge assistant into an AI Pre-sales Copilot. It includes semantic retrieval with Chroma, a provider-switchable LLM client with mock/API modes, structured grounded answers, hallucination guardrails, a lightweight evaluation pipeline, query tracing, user feedback logging, and a Streamlit demo.

A concise Chinese explanation:

> 我把原来的 RAG 售前知识库助手升级成了 AI Pre-sales Copilot。它包括 Chroma 语义检索、Mock/API 双模式 LLM Client、结构化回答、来源引用、低置信度拒答、RAG Evaluation、轻量 tracing、用户反馈记录和 Streamlit 展示页面。

---

## 13. Portfolio Value

This demo demonstrates the following AI application engineering capabilities:

```text
RAG pipeline design
LLM API abstraction
Mock/API development mode
Source grounding
Hallucination control
Evaluation dataset design
Retrieval quality measurement
Lightweight observability
User feedback loop
Streamlit demo delivery
```

It is designed for AI Solutions, LLM Application Engineer, AI Pre-sales, and Technical Consultant internship roles.
