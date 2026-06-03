# Interview Pitch：RAG-based AI Pre-sales Knowledge Assistant

## 1. 60 秒中文项目介绍

我的项目是一个面向 B2B SaaS 售前场景的 RAG 知识库助手。

它解决的问题是：售前人员在回答客户关于产品功能、价格、部署、安全、API 集成和客户案例等问题时，往往需要查找很多分散资料，效率低，而且不同人员回答可能不一致。

所以我构建了一个本地 RAG 系统。系统会先读取 Markdown 格式的售前知识库，把文档切分成 chunks，再通过 embedding 转成向量，并存入 Chroma 向量数据库。

当用户提出问题时，系统会把问题也转成 embedding，在 Chroma 中检索最相关的 Top-K chunks，然后基于这些 retrieved context 生成回答，并返回来源引用。

这个项目的重点不是做一个普通聊天机器人，而是模拟真实 B2B 售前知识管理场景，强调 source grounding、可追溯回答和降低幻觉风险。

---

## 2. 高频面试问题与回答

### Q1：请介绍一下你的 RAG 项目。

我的项目是一个面向 B2B SaaS 售前场景的 RAG 知识库助手。

它基于产品文档、FAQ、价格说明、部署指南、安全文档、API 文档和客户案例，帮助售前人员生成带来源引用的回答。

技术流程包括：

```text
Document Loading
↓
Chunking
↓
Embedding
↓
Chroma Vector Store
↓
Top-K Retrieval
↓
Answer Generation
↓
Source Citation
```

---

### Q2：为什么要做这个项目？

因为在 B2B 售前场景中，客户经常会问产品、价格、部署、安全和集成相关问题。

如果靠人工查资料，会出现三个问题：

1. 响应速度慢。
2. 不同人员回答不一致。
3. 回答容易缺少依据。

这个项目用 RAG 把分散的售前资料变成可检索知识库，让系统先找依据，再生成回答。

---

### Q3：为什么选择 RAG，而不是普通 ChatGPT？

普通 ChatGPT 不知道企业内部最新产品资料、价格策略、部署方案和客户案例。

如果直接让模型回答，它可能会产生幻觉，生成看起来合理但没有依据的内容。

RAG 的优势是：

```text
先从企业知识库中检索相关内容
↓
再基于 retrieved context 生成回答
↓
最后返回 source citation
```

因此，RAG 更适合需要准确性、可追溯性和风险控制的 B2B 售前场景。

---

### Q4：RAG 的完整流程是什么？

RAG 的完整流程是：

```text
Documents
↓
Chunking
↓
Embedding
↓
Vector Store
↓
Retrieval
↓
Answer Generation
↓
Sources
```

在我的项目中，Markdown 文档先被切成 chunks，再转成 embeddings 存入 Chroma。

用户提问时，系统会检索最相关的 chunks，并基于这些 chunks 生成回答。

---

### Q5：为什么需要 chunking？

因为长文档不适合直接检索。

如果 chunk 太大，会混入很多无关内容，影响检索精准度。

如果 chunk 太小，又容易丢失上下文，导致回答不完整。

所以 chunking 的目标是在：

```text
检索精准度
+
上下文完整性
```

之间取得平衡。

---

### Q6：什么是 embedding？

Embedding 是把文本转换成向量表示的方法。

它让系统可以基于语义相似度检索内容，而不是只依赖关键词匹配。

例如客户问：

```text
Can we host the product ourselves?
```

系统应该能匹配到知识库中的：

```text
private deployment
```

这就是 embedding 的价值。

---

### Q7：为什么选择 Chroma？

我选择 Chroma 是因为它适合快速构建本地 RAG 应用，使用简单，并且可以方便地管理文档、向量和来源信息。

FAISS 更偏底层高性能向量检索，后续如果数据规模扩大，可以考虑对比 FAISS。

在当前项目阶段，Chroma 更适合快速实现：

```text
本地向量库
↓
语义检索
↓
source citation
↓
可复现 Demo
```

---

### Q8：为什么 source citation 很重要？

在 B2B 售前场景中，价格、安全、部署、合同和客户承诺类问题不能让模型随便编。

Source citation 可以告诉用户答案来自哪份知识库文档，提升回答的可信度和可追溯性。

它的价值是：

1. 降低幻觉风险。
2. 方便人工复核。
3. 提升客户沟通的专业度。
4. 避免售前回答过度承诺。

---

### Q9：为什么当前版本用 Mock LLM？

当前版本重点是验证 RAG pipeline 的完整性和本地可复现性。

Mock LLM 可以让项目在没有 API key 的情况下运行，展示从文档读取、chunking、embedding、retrieval 到 answer + sources 的完整流程。

未来可以把 answer generation 模块替换成真实 LLM API，例如：

```text
OpenAI API
Qwen API
DeepSeek API
```

---

### Q10：你怎么评估这个项目？

我设计了 evaluation question set，覆盖产品、价格、部署、安全、API、客户案例和异议处理等典型售前场景。

每个问题都有 expected source。

运行后，我会记录：

```text
retrieved source
answer quality
citation correctness
failure cases
```

这样可以判断系统是否真的检索到了正确资料，而不是只生成了看起来流畅的回答。

---

## 3. 面试时不会的问题怎么回答？

### 3.1 如果问到 Transformer 数学细节

我可以这样回答：

> 我了解 Transformer 的核心机制是通过 self-attention 建模 token 之间的关系，但我的项目重点不是训练模型本身，而是 LLM 应用层的 RAG pipeline，包括文档处理、向量检索、prompt 构建和答案评估。

---

### 3.2 如果问到 Fine-tuning

我可以这样回答：

> Fine-tuning 更适合让模型学习特定任务格式或表达风格。但我的项目是企业知识库问答，知识更新频繁，而且需要来源引用，所以 RAG 比 fine-tuning 更适合当前场景。

---

### 3.3 如果问到 Agent

我可以这样回答：

> Agent 通常涉及工具调用、任务规划和多步执行。我的当前项目先聚焦可靠的 RAG 问答，因为售前场景最重要的是准确、可追溯和低幻觉。后续可以扩展成 Agent，例如自动生成邮件、调用 CRM 或创建 follow-up task。

---

### 3.4 如果问到大模型训练

我可以这样回答：

> 我目前没有训练基础大模型的经验。我的定位更偏 AI 应用工程和解决方案落地，关注如何把已有 LLM、embedding model 和 vector database 组合起来，解决真实业务问题。

---

## 4. 6.11 验收标准

完成本部分后，我需要能够不看稿回答以下问题：

```text
请介绍一下你的项目。
为什么选择 RAG？
为什么用 Chroma？
为什么要 source citation？
为什么当前用 Mock LLM？
你怎么评估这个项目？
```

验收标准：

* 能用中文 60 秒介绍项目。
* 能解释 RAG 完整流程。
* 能把每个技术点拉回自己的项目文件。
* 能说明项目和 AI Solutions / AI Pre-sales 岗位的关系。

---

# English Pitch

## 5. 60-second English Project Pitch

This project is a RAG-based AI pre-sales knowledge assistant for a B2B SaaS scenario.

The business problem is that pre-sales teams often need to answer customer questions about product features, pricing, deployment, security, API integration, and customer case studies.

If they rely only on manual document search, the response can be slow, inconsistent, and difficult to trace back to official sources.

To solve this problem, I built a local RAG pipeline.

The system first loads Markdown-based knowledge documents, splits them into chunks, converts the chunks into embeddings, and stores them in a Chroma vector database.

When a user asks a question, the system retrieves the most relevant chunks from Chroma and generates a grounded answer with source references.

The key value of this project is not just generating text, but improving answer accuracy, consistency, and traceability in a real pre-sales workflow.

In the next version, I would like to add a Streamlit demo interface, connect a real LLM API, and improve evaluation with more test questions and failure analysis.

---

## 6. Short English Version

I built a RAG-based AI knowledge assistant for B2B SaaS pre-sales.

It helps sales and solution teams answer customer questions based on product documents, pricing notes, deployment guides, security documents, API materials, and customer case studies.

The system uses chunking, embeddings, Chroma vector search, answer generation, and source citation to produce grounded responses.

The goal is to reduce hallucination and make customer-facing answers more accurate and traceable.

---

## 7. English Resume Bullets

* Built a local RAG-based AI pre-sales knowledge assistant using Python, sentence-transformers, and Chroma to retrieve relevant product knowledge and generate source-grounded answers.

* Designed a structured B2B SaaS knowledge base covering product overview, pricing, deployment, security, API integration, customer cases, and objection handling.

* Created an evaluation question set to assess retrieval relevance, citation correctness, answer quality, and failure cases across key pre-sales scenarios.

---

## 8. 英文录音练习方法

今天至少录音 3 遍。

每一遍只检查一个点：

```text
第 1 遍：是否能完整讲完
第 2 遍：是否语速稳定
第 3 遍：是否能自然停顿，不像背稿
```

不要追求口音完美。

目标是：

```text
清楚
稳定
自信
有结构
```

---

## 9. 6.12 验收标准

完成英文 Pitch 后，我需要能够用英文讲清楚：

```text
Business Problem
Technical Solution
RAG Pipeline
Project Value
Next Improvements
```

具体标准：

1. 能在 60 秒内完成英文项目介绍。
2. 能自然说出项目解决的业务问题。
3. 能讲清楚 RAG pipeline。
4. 能说明 source citation 和 traceability 的价值。
5. 能说出下一步计划，例如 Streamlit、真实 LLM API 和 evaluation improvement。

---

## 10. 一句话总结

这个 `interview_pitch.md` 的目标不是写一篇漂亮文章，而是让我能够在中文和英文面试中稳定讲清楚：

```text
我做了什么项目
解决了什么业务问题
用了什么 AI 应用技术
为什么适合 B2B 售前场景
如何控制幻觉风险
下一步如何升级
```
