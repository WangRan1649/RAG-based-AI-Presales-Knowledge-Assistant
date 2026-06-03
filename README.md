# RAG-based AI Pre-sales Knowledge Assistant

## 1. 项目概览

本项目是一个面向 **B2B SaaS 售前场景** 的 **RAG 知识库助手**。

它可以帮助销售工程师、售前顾问、解决方案顾问和客户成功团队，基于结构化的产品知识文档回答客户问题。

系统会从 Markdown 格式的知识库中检索相关内容，并生成带有来源引用的回答。

本项目不是一个通用聊天机器人，而是一个面向 **企业知识检索、售前问答、来源可追溯回答生成** 的 AI 应用原型。

---

## 2. 业务问题

在 B2B SaaS 售前场景中，客户经常会提出以下问题：

* 产品支持哪些功能？
* 价格和套餐有什么区别？
* 是否支持私有化部署？
* 数据安全如何保障？
* 是否支持 API 集成？
* 有没有类似行业的客户案例？
* 如何回应客户的异议？
* 如何撰写售前跟进邮件？

如果销售或售前团队完全依赖人工查找资料，通常会遇到以下问题：

1. **响应速度慢**
   团队成员需要在多个产品文档中手动查找信息。

2. **回答不一致**
   不同成员可能对同一产品能力给出不同解释。

3. **缺少来源依据**
   价格、部署、安全和客户承诺等敏感问题需要可靠来源支撑。

4. **直接使用通用大模型存在幻觉风险**
   如果大模型没有接入企业内部知识库，可能生成流畅但没有依据的回答。

本项目通过 RAG 流程提升回答的一致性、可追溯性和可靠性。

---

## 3. 解决方案概述

本项目构建了一个本地 RAG 流程，整体工作流如下：

```text
Markdown 知识库
↓
文档加载
↓
文档切分
↓
Embedding 向量化
↓
Chroma 向量数据库
↓
Top-K 语义检索
↓
回答生成
↓
答案 + 来源引用
```

当用户提出问题时，系统不会直接依赖模型内部知识生成回答。

它会先从知识库中检索相关文档片段，再基于检索到的内容生成回答。

---

## 4. 核心功能

* 结构化 B2B SaaS 售前知识库
* Markdown 文档加载
* 文档切分
* 基于 sentence-transformers 的 embedding 生成
* Chroma 本地向量数据库
* Top-K 语义检索
* 带来源引用的回答生成
* 使用 Mock LLM / 模板化生成，保证本地可复现
* 基于 CSV 的评估问题集
* 面向高风险售前回答的 Human-in-the-loop 设计

---

## 5. 技术栈

| 模块           | 工具 / 方法                              |
| ------------ | ------------------------------------ |
| 编程语言         | Python                               |
| 知识库格式        | Markdown                             |
| Embedding 模型 | sentence-transformers                |
| 向量数据库        | Chroma                               |
| 检索方式         | Top-K semantic retrieval             |
| 回答生成         | Mock LLM / template-based generation |
| 评估方式         | CSV-based manual evaluation          |
| 版本控制         | Git / GitHub                         |
| 未来 Demo 页面   | Streamlit                            |
| 未来 API 层     | FastAPI                              |
| 未来 LLM API   | OpenAI / Qwen / DeepSeek             |

---

## 6. 系统架构

```text
Markdown 知识库
↓
Load Documents
↓
Chunk Documents
↓
Document Chunks
↓
Embedding Model
↓
Chroma Vector Store
↓
User Question
↓
Question Embedding
↓
Top-K Retrieval
↓
Retrieved Context
↓
Answer Generation
↓
Answer + Sources
```

详细架构说明见：

```text
docs/architecture.md
```

---

## 7. 项目结构

```text
RAG-based-AI-Presales-Knowledge-Assistant/
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
├── rag_app/
│   ├── load_documents.py
│   ├── chunk_documents.py
│   ├── embedding_client.py
│   ├── build_vector_store.py
│   ├── retrieve_context_chroma.py
│   ├── generate_answer_chroma.py
│   ├── generate_answer.py
│   ├── main_chroma.py
│   └── main.py
│
├── outputs/
│   ├── document_chunks.json
│   ├── sample_answer.md
│   ├── sample_answer_chroma.md
│   ├── demo_answer_01.md
│   ├── demo_answer_02.md
│   └── demo_answer_03.md
│
├── eval/
│   └── sample_eval_questions.csv
│
├── docs/
│   ├── architecture.md
│   ├── embedding_notes.md
│   ├── vector_store_notes.md
│   ├── retrieval_test_notes.md
│   ├── answer_generation_notes.md
│   ├── engineering_notes.md
│   ├── evaluation_report.md
│   ├── interview_pitch.md
│   ├── resume_bullets.md
│   └── images/
│
├── vector_store/
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 8. 知识库设计

本项目的知识库模拟了一个虚拟 B2B SaaS 产品 **InsightFlow AI** 的产品与售前资料。

知识库包含以下文档：

| 文件                               | 作用                     |
| -------------------------------- | ---------------------- |
| `01_product_overview.md`         | 产品总览、目标用户和核心模块         |
| `02_faq.md`                      | 客户常见问题                 |
| `03_pricing_and_packaging.md`    | 价格套餐与包装说明              |
| `04_deployment_guide.md`         | 云部署、私有化部署和实施说明         |
| `05_security_and_governance.md`  | 数据安全、权限控制、审计日志和治理      |
| `06_integrations_and_api.md`     | API 集成、CRM 集成和 BI 工具连接 |
| `07_customer_case_studies.md`    | 客户案例和业务成果              |
| `08_objection_handling.md`       | 常见销售异议和回应策略            |
| `09_presales_email_templates.md` | 售前跟进邮件模板               |

该知识库不是随机文本，而是为了模拟真实 B2B SaaS 售前资料体系而设计。

---

## 9. RAG Pipeline

### Step 1：加载文档

对应文件：

```text
rag_app/load_documents.py
```

作用：

* 读取 `knowledge_base/` 中的 Markdown 文件
* 保留文档来源信息
* 将原始文档转换成程序可以处理的数据

---

### Step 2：文档切分

对应文件：

```text
rag_app/chunk_documents.py
```

作用：

* 将较长的 Markdown 文档切分成较小的 chunks
* 将 chunk 信息保存到 `outputs/document_chunks.json`

每个 chunk 包含：

```text
chunk_id
source_file
chunk_index
text
```

其中：

* `text` 字段用于后续 embedding 和 retrieval
* `source_file` 字段用于支持来源引用

---

### Step 3：生成 Embeddings

对应文件：

```text
rag_app/embedding_client.py
```

作用：

* 将 chunk text 转换为 embedding 向量
* 支持基于语义相似度的检索

Embedding 的价值在于，用户问题和知识库内容即使使用了不同表达，也可以通过语义相似度匹配。

例如：

```text
用户问题：
Can we host the product ourselves?

知识库表达：
private deployment
```

虽然关键词不同，但语义上都与私有化部署相关。

---

### Step 4：构建向量库

对应文件：

```text
rag_app/build_vector_store.py
```

输出位置：

```text
vector_store/
```

作用：

* 读取文档 chunks
* 生成 embeddings
* 将向量和来源信息存入 Chroma

`vector_store/` 不是普通文档文件夹，而是 Chroma 本地向量数据库的存储位置。

---

### Step 5：检索上下文

对应文件：

```text
rag_app/retrieve_context_chroma.py
```

作用：

* 将用户问题转换成 embedding
* 在 Chroma 中检索最相关的 chunks
* 返回 Top-K retrieved context 和对应 sources

---

### Step 6：生成回答

对应文件：

```text
rag_app/generate_answer_chroma.py
```

作用：

* 接收用户问题
* 接收 retrieved context
* 生成回答
* 返回来源引用

当前版本使用 Mock LLM 或模板化回答，以保证项目可以在本地稳定复现。

未来可以将该模块替换为真实 LLM API。

---

## 10. 版本演进

### RAG v1：本地 TF-IDF 原型

第一版使用更简单的本地 TF-IDF 检索方式。

它用于验证基础 RAG 思路：

```text
documents
↓
chunks
↓
keyword-based retrieval
↓
template-based answer
```

该版本的价值是快速跑通第一个原型，但也存在限制：

* 更依赖关键词匹配
* 语义匹配能力较弱
* 如果用户表达和文档表达不同，可能漏掉相关内容

---

### RAG v2：Embedding + Chroma 语义检索

当前主版本使用：

```text
sentence-transformers
+
Chroma vector database
```

与 v1 相比，RAG v2 支持语义检索。

这意味着系统可以更好地处理用户表达和文档表达不完全一致的问题。

例如：

```text
Can we host the product ourselves?
```

可以匹配到：

```text
private deployment
```

这让项目更接近真实售前问答场景。

---

## 11. Demo Questions

项目包含三个能体现 B2B SaaS 售前价值的 Demo 问题。

| Demo Question                                   | Expected Source                 | Business Scenario |
| ----------------------------------------------- | ------------------------------- | ----------------- |
| Does the product support private deployment?    | `04_deployment_guide.md`        | 企业部署与合规           |
| Can this product integrate with our CRM system? | `06_integrations_and_api.md`    | 系统集成              |
| How does the system protect customer data?      | `05_security_and_governance.md` | 数据安全与治理           |

Demo 输出文件：

```text
outputs/demo_answer_01.md
outputs/demo_answer_02.md
outputs/demo_answer_03.md
```

示例输出文件：

```text
outputs/sample_answer_chroma.md
```

---

## 12. 示例输出格式

典型生成结果包含：

```text
Question:
Does the product support private deployment?

Retrieved Source:
04_deployment_guide.md

Answer:
The product supports private deployment for enterprise customers, depending on deployment requirements and implementation scope.

Sources:
04_deployment_guide.md
```

关键点是，系统不仅返回回答，也返回来源。

这可以支持 source grounding，并降低无依据回答的风险。

---

## 13. Evaluation

项目包含一个评估问题集：

```text
eval/sample_eval_questions.csv
```

评估问题覆盖：

* 产品总览
* FAQ
* 价格
* 部署
* 安全
* API 集成
* 客户案例
* 异议处理
* 售前邮件模板

评估关注以下维度：

| 指标                   | 含义                               |
| -------------------- | -------------------------------- |
| Retrieval Hit        | 检索到的 source 是否匹配 expected source |
| Citation Correctness | 回答中引用的来源是否正确                     |
| Answer Relevance     | 回答是否真正回应用户问题                     |
| Faithfulness         | 回答是否忠于检索到的 context               |
| Failure Case         | 系统是否失败，以及失败原因是什么                 |

评估报告：

```text
docs/evaluation_report.md
```

本项目不仅关注回答是否流畅，也关注回答是否基于正确的知识来源。

---

## 14. 本地运行方式

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd RAG-based-AI-Presales-Knowledge-Assistant
```

---

### 2. 创建虚拟环境

```bash
python -m venv .venv
```

---

### 3. 激活虚拟环境

Windows PowerShell：

```powershell
.venv\Scripts\Activate.ps1
```

Windows cmd：

```cmd
.venv\Scripts\activate
```

---

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

---

### 5. 构建向量库

```bash
python rag_app/build_vector_store.py
```

如果需要以模块方式运行：

```bash
python -m rag_app.build_vector_store
```

这一步会读取 Markdown 知识库，生成 embeddings，并将其保存到本地 Chroma 向量数据库 `vector_store/` 中。

---

### 6. 运行 Chroma 版本 RAG Pipeline

```bash
python rag_app/main_chroma.py
```

如果需要以模块方式运行：

```bash
python -m rag_app.main_chroma
```

这一步会从 vector store 中检索相关 chunks，并生成带来源引用的回答。

---

## 15. 为什么要先构建向量库？

RAG 系统分为两个阶段：

```text
Stage 1：构建索引
Markdown documents → chunks → embeddings → vector_store/

Stage 2：用户问答
user question → retrieve from vector_store/ → answer + sources
```

`build_vector_store.py` 负责准备可检索的向量索引。

`main_chroma.py` 负责使用已经存在的向量库进行检索和回答生成。

如果还没有构建向量库，系统可能无法检索到相关 chunks。

---

## 16. 为什么使用 Mock LLM？

当前版本使用 Mock LLM 或模板化回答，以保证本地可复现。

这样设计有几个好处：

1. 项目不依赖 API key。
2. 避免不必要的 API 调用成本。
3. 面试时更容易复现。
4. 可以先聚焦核心 RAG 流程。

当前版本仍然展示了完整 RAG pipeline：

```text
documents
↓
chunks
↓
embeddings
↓
vector store
↓
retrieval
↓
answer + sources
```

未来版本可以替换为：

* OpenAI API
* Qwen API
* DeepSeek API

---

## 17. Human-in-the-loop 设计

在 B2B 售前场景中，并不是所有 AI 生成的回答都应该直接发送给客户。

以下高风险问题需要人工审核：

* 价格承诺
* 安全声明
* 合同条款
* 部署保证
* 合规说明
* 客户定制化承诺

本项目遵循 Human-in-the-loop 思路：

```text
AI 检索并生成草稿
↓
人工审核和确认
↓
对客户输出正式回答
```

该设计可以降低幻觉风险和无依据承诺风险。

---

## 18. 风险控制

本项目强调基于来源的回答生成。

主要风险控制机制包括：

1. **来源引用**
   系统会在生成回答时返回对应 source files。

2. **评估问题集**
   项目通过测试问题检查 retrieved source 是否匹配 expected source。

3. **Mock LLM 保证可复现**
   当前版本避免了 API 行为不稳定对早期开发的影响。

4. **Human-in-the-loop 审核**
   高风险回答在对外发送前应由人工确认。

5. **未来 fallback 逻辑**
   如果 retrieved context 不足，系统应该说明无法确认，而不是编造答案。

---

## 19. 岗位相关性

本项目适合展示给以下岗位：

* AI Solutions Intern
* AI Pre-sales Intern
* Technical Consultant Intern
* LLM Application Intern
* Overseas Technical Operations Intern
* AI Application Engineer Intern

它体现了以下能力：

* 理解业务场景
* 将业务问题转化为 AI 应用流程
* 构建可运行的 RAG 应用原型
* 清楚解释 LLM 应用层概念
* 设计基于来源的回答生成
* 评估检索和回答质量
* 将 AI 项目包装为 GitHub 和面试作品

---

## 20. 当前限制

当前项目仍然存在以下限制：

1. 回答生成模块尚未接入真实 LLM API。
2. Evaluation 目前主要依赖人工评估。
3. 项目目前主要通过命令行运行。
4. Chunking 仍可升级为 Markdown-aware splitting。
5. Retrieval 质量可以通过 reranking 进一步优化。
6. 系统尚未包含 Web Demo 页面。
7. 系统尚未包含 API endpoint。
8. 对 retrieved context 不足的 fallback 逻辑仍可改进。

---

## 21. 下一步计划

后续计划包括：

1. 增加 Streamlit Demo 页面。
2. 增加 FastAPI 接口，例如 `POST /ask`。
3. 接入真实 LLM API。
4. 增加自动化评估脚本。
5. 使用 section title 和 chunk overlap 优化 chunking。
6. 增加 retrieved context 不足时的 fallback 逻辑。
7. 增加 reranking，提高检索精度。
8. 增加高风险回答的人工审核状态。
9. 对比 Chroma 和 FAISS 在更大规模检索下的表现。
10. 优化 README 截图和 Demo 证据展示。

---

## 22. 面试介绍

如果需要介绍这个项目，我会这样说：

> 这个项目是一个面向 B2B SaaS 售前场景的 RAG 知识库助手。
>
> 它解决的问题是：售前团队经常需要基于分散的产品文档，回答客户关于产品功能、价格、部署、安全、API 集成和客户案例的问题。
>
> 系统会读取 Markdown 知识库，将文档切分成 chunks，再通过 embedding 转成向量并存入 Chroma。用户提问时，系统会检索相关 chunks，并基于 retrieved context 生成带来源引用的回答。
>
> 这个项目的核心价值不只是生成文本，而是提升售前回答的准确性、一致性和可追溯性。

---

## 23. 核心总结

本项目展示了如何通过 RAG pipeline，将静态 B2B SaaS 产品文档转化为一个可检索、可引用、可解释的 AI 售前知识库助手。

它不仅体现了技术实现能力，也体现了业务理解、风险控制、评估思维和 AI 解决方案包装能力。

# RAG-based AI Pre-sales Knowledge Assistant

## 1. Overview

This project is a **RAG-based AI pre-sales knowledge assistant** designed for a simulated **B2B SaaS** scenario.

It helps sales engineers, pre-sales consultants, solution consultants, and customer success teams answer customer-facing questions based on structured product knowledge documents.

The system retrieves relevant context from Markdown-based knowledge files and generates grounded answers with source references.

This project is not a general-purpose chatbot. It is designed as an AI application prototype for **enterprise knowledge retrieval, pre-sales Q&A, and source-grounded answer generation**.

---

## 2. Business Problem

In B2B SaaS pre-sales, customers often ask questions about:

* Product capabilities
* Pricing and packaging
* Private deployment
* Data security
* API integration
* Customer case studies
* Objection handling
* Follow-up email drafting

If sales or pre-sales teams answer these questions manually, they may face several problems:

1. **Slow response time**
   Team members need to search through multiple product documents before answering.

2. **Inconsistent answers**
   Different team members may give different explanations for the same product capability.

3. **Lack of source grounding**
   Sensitive topics such as pricing, deployment, security, and customer commitments require reliable references.

4. **High risk of hallucination when using a general LLM directly**
   A general LLM may generate fluent but unsupported answers if it does not have access to the company’s internal knowledge base.

This project uses a RAG pipeline to improve answer consistency, traceability, and reliability.

---

## 3. Solution Summary

The project builds a local RAG pipeline that follows this workflow:

```text
Markdown Knowledge Base
↓
Document Loading
↓
Chunking
↓
Embedding
↓
Chroma Vector Store
↓
Top-K Semantic Retrieval
↓
Answer Generation
↓
Answer + Sources
```

When a user asks a question, the system does not directly generate an answer from the model’s internal knowledge.

Instead, it first retrieves relevant chunks from the knowledge base, then generates an answer grounded in those retrieved contexts.

---

## 4. Key Features

* Structured B2B SaaS knowledge base
* Markdown document loading
* Document chunking
* Sentence-transformers based embeddings
* Chroma local vector database
* Top-K semantic retrieval
* Source-grounded answer generation
* Mock LLM / template-based generation for local reproducibility
* Evaluation question set for retrieval and answer quality checking
* Human-in-the-loop design for high-risk pre-sales answers

---

## 5. Tech Stack

| Area                  | Tools / Methods                      |
| --------------------- | ------------------------------------ |
| Programming Language  | Python                               |
| Knowledge Base        | Markdown                             |
| Embedding Model       | sentence-transformers                |
| Vector Database       | Chroma                               |
| Retrieval Method      | Top-K semantic retrieval             |
| Answer Generation     | Mock LLM / template-based generation |
| Evaluation            | CSV-based manual evaluation          |
| Version Control       | Git / GitHub                         |
| Future Demo Interface | Streamlit                            |
| Future API Layer      | FastAPI                              |
| Future LLM API        | OpenAI / Qwen / DeepSeek             |

---

## 6. Architecture

```text
Markdown Knowledge Base
↓
Load Documents
↓
Chunk Documents
↓
Document Chunks
↓
Embedding Model
↓
Chroma Vector Store
↓
User Question
↓
Question Embedding
↓
Top-K Retrieval
↓
Retrieved Context
↓
Answer Generation
↓
Answer + Sources
```

Detailed architecture explanation:

```text
docs/architecture.md
```

---

## 7. Project Structure

```text
RAG-based-AI-Presales-Knowledge-Assistant/
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
├── rag_app/
│   ├── load_documents.py
│   ├── chunk_documents.py
│   ├── embedding_client.py
│   ├── build_vector_store.py
│   ├── retrieve_context_chroma.py
│   ├── generate_answer_chroma.py
│   ├── generate_answer.py
│   ├── main_chroma.py
│   └── main.py
│
├── outputs/
│   ├── document_chunks.json
│   ├── sample_answer.md
│   ├── sample_answer_chroma.md
│   ├── demo_answer_01.md
│   ├── demo_answer_02.md
│   └── demo_answer_03.md
│
├── eval/
│   └── sample_eval_questions.csv
│
├── docs/
│   ├── architecture.md
│   ├── embedding_notes.md
│   ├── vector_store_notes.md
│   ├── retrieval_test_notes.md
│   ├── answer_generation_notes.md
│   ├── engineering_notes.md
│   ├── evaluation_report.md
│   ├── interview_pitch.md
│   ├── resume_bullets.md
│   └── images/
│
├── vector_store/
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 8. Knowledge Base Design

The knowledge base simulates product and pre-sales materials for a fictional B2B SaaS product named **InsightFlow AI**.

It contains the following documents:

| File                             | Purpose                                                        |
| -------------------------------- | -------------------------------------------------------------- |
| `01_product_overview.md`         | Product overview, target users, and core modules               |
| `02_faq.md`                      | Frequently asked customer questions                            |
| `03_pricing_and_packaging.md`    | Pricing plans and packaging information                        |
| `04_deployment_guide.md`         | Cloud deployment, private deployment, and implementation notes |
| `05_security_and_governance.md`  | Data security, access control, audit logs, and governance      |
| `06_integrations_and_api.md`     | API integration, CRM integration, and BI tool connection       |
| `07_customer_case_studies.md`    | Customer success stories and business outcomes                 |
| `08_objection_handling.md`       | Common sales objections and response strategies                |
| `09_presales_email_templates.md` | Pre-sales follow-up email templates                            |

This knowledge base is not random text. It is designed to simulate real B2B SaaS pre-sales materials.

---

## 9. RAG Pipeline

### Step 1: Load Documents

File:

```text
rag_app/load_documents.py
```

Purpose:

* Reads Markdown files from `knowledge_base/`
* Preserves source file information
* Converts raw documents into program-readable data

---

### Step 2: Chunk Documents

File:

```text
rag_app/chunk_documents.py
```

Purpose:

* Splits long Markdown documents into smaller chunks
* Saves chunk information into `outputs/document_chunks.json`

Each chunk contains:

```text
chunk_id
source_file
chunk_index
text
```

The `text` field is used for embedding and retrieval.

The `source_file` field supports source citation.

---

### Step 3: Generate Embeddings

File:

```text
rag_app/embedding_client.py
```

Purpose:

* Converts chunk text into embedding vectors
* Enables semantic similarity search

Embedding is useful because users may ask questions using different wording from the knowledge base.

Example:

```text
User question:
Can we host the product ourselves?

Knowledge base expression:
private deployment
```

Even though the wording is different, embedding-based retrieval can match them by semantic similarity.

---

### Step 4: Build Vector Store

File:

```text
rag_app/build_vector_store.py
```

Output:

```text
vector_store/
```

Purpose:

* Reads document chunks
* Generates embeddings
* Stores vectors and source information in Chroma

`vector_store/` is not a normal document folder. It is the local Chroma vector database storage location.

---

### Step 5: Retrieve Context

File:

```text
rag_app/retrieve_context_chroma.py
```

Purpose:

* Converts the user question into an embedding
* Searches Chroma for the most relevant chunks
* Returns Top-K retrieved contexts and their sources

---

### Step 6: Generate Answer

File:

```text
rag_app/generate_answer_chroma.py
```

Purpose:

* Receives the user question
* Receives retrieved context
* Generates an answer
* Returns source references

The current version uses Mock LLM or template-based generation to keep the project locally reproducible.

Future versions can replace this module with a real LLM API.

---

## 10. Version Evolution

### RAG v1: Local TF-IDF Prototype

The first version used a simpler local retrieval approach based on TF-IDF.

It helped validate the basic idea:

```text
documents
↓
chunks
↓
keyword-based retrieval
↓
template-based answer
```

This version was useful for building the first working prototype, but it had limitations:

* It relied more on keyword matching
* It was weaker at semantic matching
* It could miss relevant documents if the user used different wording

---

### RAG v2: Embedding + Chroma Semantic Retrieval

The current main version uses:

```text
sentence-transformers
+
Chroma vector database
```

Compared with v1, RAG v2 supports semantic retrieval.

This means the system can better handle questions where the user’s wording differs from the document’s wording.

Example:

```text
Can we host the product ourselves?
```

can match:

```text
private deployment
```

This makes the project more suitable for realistic pre-sales Q&A scenarios.

---

## 11. Demo Questions

The project includes demo questions that reflect common B2B SaaS pre-sales scenarios.

| Demo Question                                   | Expected Source                 | Business Scenario                    |
| ----------------------------------------------- | ------------------------------- | ------------------------------------ |
| Does the product support private deployment?    | `04_deployment_guide.md`        | Enterprise deployment and compliance |
| Can this product integrate with our CRM system? | `06_integrations_and_api.md`    | System integration                   |
| How does the system protect customer data?      | `05_security_and_governance.md` | Data security and governance         |

Demo outputs:

```text
outputs/demo_answer_01.md
outputs/demo_answer_02.md
outputs/demo_answer_03.md
```

Sample output:

```text
outputs/sample_answer_chroma.md
```

---

## 12. Example Output Format

A typical generated answer includes:

```text
Question:
Does the product support private deployment?

Retrieved Source:
04_deployment_guide.md

Answer:
The product supports private deployment for enterprise customers, depending on deployment requirements and implementation scope.

Sources:
04_deployment_guide.md
```

The key idea is that the system returns both an answer and its source.

This supports source grounding and reduces the risk of unsupported claims.

---

## 13. Evaluation

The project includes an evaluation question set:

```text
eval/sample_eval_questions.csv
```

The evaluation questions cover:

* Product overview
* FAQ
* Pricing
* Deployment
* Security
* API integration
* Customer case studies
* Objection handling
* Pre-sales email templates

Evaluation focuses on the following dimensions:

| Metric               | Meaning                                                  |
| -------------------- | -------------------------------------------------------- |
| Retrieval Hit        | Whether the retrieved source matches the expected source |
| Citation Correctness | Whether the answer cites the correct source              |
| Answer Relevance     | Whether the answer addresses the question                |
| Faithfulness         | Whether the answer is grounded in the retrieved context  |
| Failure Case         | Whether the system fails and why                         |

Evaluation report:

```text
docs/evaluation_report.md
```

This project does not only check whether the answer looks fluent. It also checks whether the answer is based on the correct knowledge source.

---

## 14. How to Run Locally

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd RAG-based-AI-Presales-Knowledge-Assistant
```

---

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

---

### 3. Activate Virtual Environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows cmd:

```cmd
.venv\Scripts\activate
```

---

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 5. Build the Vector Store

```bash
python rag_app/build_vector_store.py
```

If module execution is needed:

```bash
python -m rag_app.build_vector_store
```

This step reads the Markdown knowledge base, generates embeddings, and stores them in a local Chroma vector database under `vector_store/`.

---

### 6. Run the Chroma-based RAG Pipeline

```bash
python rag_app/main_chroma.py
```

If module execution is needed:

```bash
python -m rag_app.main_chroma
```

This step retrieves relevant chunks from the vector store and generates an answer with source references.

---

## 15. Why Build the Vector Store First?

The RAG system has two stages:

```text
Stage 1: Build Index
Markdown documents → chunks → embeddings → vector_store/

Stage 2: Ask Questions
user question → retrieve from vector_store/ → answer + sources
```

`build_vector_store.py` prepares the searchable vector index.

`main_chroma.py` uses the existing vector store to perform retrieval and answer generation.

If the vector store has not been built, the system may not be able to retrieve relevant chunks.

---

## 16. Why Mock LLM?

The current version uses Mock LLM or template-based answer generation for local reproducibility.

This design has several advantages:

1. The project can run without an API key.
2. It avoids unnecessary API costs.
3. It makes the pipeline easier to reproduce during interviews.
4. It allows the project to focus on the core RAG workflow first.

The full RAG pipeline is still demonstrated:

```text
documents
↓
chunks
↓
embeddings
↓
vector store
↓
retrieval
↓
answer + sources
```

Future versions can replace Mock LLM with:

* OpenAI API
* Qwen API
* DeepSeek API

---

## 17. Human-in-the-loop Design

In B2B pre-sales scenarios, not all AI-generated answers should be sent directly to customers.

High-risk topics should involve human review, including:

* Pricing commitments
* Security claims
* Contract terms
* Deployment guarantees
* Compliance statements
* Customer-specific promises

The project follows a human-in-the-loop mindset:

```text
AI retrieves and drafts
↓
Human reviews and confirms
↓
Customer-facing answer is delivered
```

This design reduces the risk of hallucination and unsupported claims.

---

## 18. Risk Control

This project focuses on source-grounded answer generation.

Key risk control mechanisms include:

1. **Source citation**
   The system returns source files together with generated answers.

2. **Evaluation question set**
   The project tests whether retrieval results match expected sources.

3. **Mock LLM for reproducibility**
   The current version avoids unpredictable API behavior during early development.

4. **Human-in-the-loop review**
   High-risk answers should be reviewed before customer delivery.

5. **Future fallback logic**
   If the retrieved context is insufficient, the system should say that it cannot confirm the answer instead of fabricating information.

---

## 19. Role Relevance

This project is designed to match the skill requirements of roles such as:

* AI Solutions Intern
* AI Pre-sales Intern
* Technical Consultant Intern
* LLM Application Intern
* Overseas Technical Operations Intern
* AI Application Engineer Intern

It demonstrates the following capabilities:

* Understanding business scenarios
* Translating business needs into AI workflows
* Building a working RAG application prototype
* Explaining LLM application concepts clearly
* Designing source-grounded answer generation
* Evaluating retrieval and answer quality
* Packaging an AI project for GitHub and interviews

---

## 20. Limitations

Current limitations include:

1. The answer generation module does not yet use a real LLM API.
2. Evaluation is still mostly manual.
3. The project currently runs from the command line.
4. Chunking can be improved with Markdown-aware splitting.
5. Retrieval quality can be further improved with reranking.
6. The system does not yet include a web interface.
7. The system does not yet include an API endpoint.
8. Fallback logic for insufficient context can be improved.

---

## 21. Next Steps

Planned improvements:

1. Add a Streamlit demo interface.
2. Add a FastAPI endpoint such as `POST /ask`.
3. Connect to a real LLM API.
4. Add automatic evaluation scripts.
5. Improve chunking with section titles and chunk overlap.
6. Add fallback logic for insufficient retrieved context.
7. Add reranking to improve retrieval precision.
8. Add human review status for high-risk answers.
9. Compare Chroma with FAISS for larger-scale retrieval.
10. Improve README screenshots and demo evidence.

---

## 22. Interview Summary

If asked to introduce this project, I would say:

> This project is a RAG-based AI pre-sales knowledge assistant for a B2B SaaS scenario.
>
> It solves the problem that pre-sales teams often need to answer customer questions about product features, pricing, deployment, security, API integration, and customer cases based on scattered documents.
>
> The system loads Markdown knowledge documents, splits them into chunks, converts the chunks into embeddings, stores them in Chroma, retrieves relevant chunks based on a user question, and generates an answer with source references.
>
> The key value is not just generating text, but improving answer accuracy, consistency, and traceability in customer-facing pre-sales workflows.

---

## 23. Key Takeaway

This project shows how a RAG pipeline can turn static B2B SaaS product documents into a searchable, source-grounded AI pre-sales assistant.

It demonstrates not only technical implementation, but also business understanding, risk control, evaluation thinking, and AI solution packaging.
