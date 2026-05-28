# RAG Flow Notes：load_documents 与 chunk_documents 理解

## 1. 当前阶段理解目标

本文件用于记录我对当前 RAG 项目前半段流程的理解，重点关注两个模块：

```text
rag_app/load_documents.py
rag_app/chunk_documents.py
```

这两个模块对应 RAG 流程中的前两步：

```text
Markdown 知识库
↓
Load Documents
↓
Chunk Documents
```

也就是说，本阶段要理解的是：

> 系统如何从 `knowledge_base/` 中的 Markdown 文件开始，把原始文档读取进程序，并进一步切分成后续可以 embedding 和 retrieval 的 chunks。

---

## 2. 当前项目的整体 RAG 流程

当前项目是一个面向 B2B SaaS 售前场景的 RAG 知识库助手。

它的整体流程可以理解为：

```text
Markdown Knowledge Base
↓
Load Documents
↓
Chunk Documents
↓
Generate Embeddings
↓
Store in Chroma Vector Database
↓
User Question
↓
Retrieve Top-K Relevant Chunks
↓
Generate Grounded Answer
↓
Return Answer + Sources
```

用中文解释就是：

> 系统先读取本地 Markdown 售前知识库，把长文档切分成较小的 chunks，然后将这些 chunks 转成 embeddings 并存入 Chroma 向量数据库。当用户提出问题时，系统会检索最相关的 chunks，再基于这些 chunks 生成带来源引用的回答。

---

## 3. load_documents.py 的作用

### 3.1 这个文件负责什么？

`load_documents.py` 是 RAG 流程的数据入口。

它负责从本地知识库文件夹中读取 Markdown 文件，并把这些文件加载成程序可以处理的 document 数据。

在当前项目中，它主要服务于这一段流程：

```text
knowledge_base/*.md
↓
load_documents.py
↓
documents
```

---

### 3.2 它的输入是什么？

`load_documents.py` 的输入是：

```text
knowledge_base/*.md
```

也就是 `knowledge_base/` 文件夹中的 Markdown 文件，例如：

```text
01_product_overview.md
02_faq.md
03_pricing_and_packaging.md
04_deployment_guide.md
05_security_and_governance.md
06_integrations_and_api.md
07_customer_case_studies.md
08_objection_handling.md
09_presales_email_templates.md
```

这些文件模拟的是一个 B2B SaaS 公司的售前知识库。

它们包括：

* 产品介绍
* 常见问题
* 价格与套餐
* 部署指南
* 安全与治理
* API 与集成
* 客户案例
* 异议处理
* 售前邮件模板

---

### 3.3 它的输出是什么？

`load_documents.py` 的输出可以理解为：

```text
documents
```

每个 document 至少应该包含两类信息：

```text
1. 文档正文内容
2. 文档来源信息
```

其中，文档来源信息非常重要，因为后续生成回答时需要告诉用户：

> 这个答案来自哪一份知识库文件。

这也是 source citation 的基础。

---

### 3.4 我对 load_documents.py 的理解

我对 `load_documents.py` 的理解是：

> `load_documents.py` 负责把本地 Markdown 知识库加载进 RAG 系统。它不是负责回答问题的模块，而是负责准备原始知识数据的模块。没有这一步，后续的 chunking、embedding、retrieval 和 answer generation 都无法进行。

在整个 RAG 流程中，它对应的是：

```text
Markdown Knowledge Base
↓
Load Documents
```

---

## 4. chunk_documents.py 的作用

### 4.1 这个文件负责什么？

`chunk_documents.py` 负责把读取进来的长文档切分成较小的 chunks。

在当前项目中，它主要服务于这一段流程：

```text
documents
↓
chunk_documents.py
↓
outputs/document_chunks.json
```

---

### 4.2 它的输入是什么？

`chunk_documents.py` 的输入是：

```text
documents
```

也就是 `load_documents.py` 读取出来的文档数据。

这些 documents 原本来自：

```text
knowledge_base/*.md
```

---

### 4.3 它的输出是什么？

`chunk_documents.py` 的输出是：

```text
outputs/document_chunks.json
```

我实际观察了 `outputs/document_chunks.json`，当前项目中每个 chunk 的真实结构如下：

```json
{
  "chunk_id": "chunk_0001",
  "source_file": "01_product_overview.md",
  "chunk_index": 1,
  "text": "# InsightFlow AI — Product Overview\n\nInsightFlow AI is a fictional B2B SaaS product..."
}
```

因此，当前项目的 chunk 并不是使用下面这种结构：

```text
chunk_id
source_file
content
metadata
```

而是实际使用下面这种结构：

```text
chunk_id
source_file
chunk_index
text
```

---

## 5. 当前 chunk 字段说明

| 字段            | 含义                                                    |
| ------------- | ----------------------------------------------------- |
| `chunk_id`    | 每个 chunk 的唯一编号，例如 `chunk_0001`                        |
| `source_file` | 这个 chunk 来自哪个 Markdown 文件，例如 `01_product_overview.md` |
| `chunk_index` | 这个 chunk 在原始文档中的顺序                                    |
| `text`        | chunk 的正文内容，也是后续 embedding 和 retrieval 的主要输入          |

---

## 6. text、source_file、chunk_index 的关系

在当前项目中：

```text
text
```

相当于 chunk 的正文内容。

它是后续进行 embedding 的主要文本。

而：

```text
source_file
chunk_index
```

可以理解为 chunk 的来源信息。

虽然当前项目没有单独使用一个叫做 `metadata` 的字段，但 `source_file` 和 `chunk_index` 实际上承担了 metadata 的作用。

也就是说，当前项目采用的是一种扁平化结构：

```json
{
  "chunk_id": "...",
  "source_file": "...",
  "chunk_index": 1,
  "text": "..."
}
```

而不是嵌套式结构：

```json
{
  "chunk_id": "...",
  "text": "...",
  "metadata": {
    "source_file": "...",
    "chunk_index": 1
  }
}
```

这两种结构本质上都可以支持 RAG，只是数据组织方式不同。

---

## 7. 我对 chunk_documents.py 的理解

我对 `chunk_documents.py` 的理解是：

> `chunk_documents.py` 负责把长文本切分成多个较小的 chunks。每个 chunk 会保留自己的唯一编号、来源文件、顺序编号和正文文本。这样后续系统在检索到某个 chunk 时，不仅能拿到相关文本，还能知道它来自哪一份知识库文件，从而支持 source citation。

在整个 RAG 流程中，它对应的是：

```text
Load Documents
↓
Chunk Documents
```

---

## 8. 为什么 RAG 需要 Chunking？

RAG 系统通常不能直接把整篇长文档全部丢给模型或向量数据库处理。

原因主要有三个：

### 8.1 长文档会影响检索精准度

如果直接把整篇文档作为一个整体进行检索，那么一个文档里可能包含很多无关内容。

例如，`01_product_overview.md` 里可能同时包含：

* 产品介绍
* 核心模块
* 目标用户
* 不支持的功能
* 使用场景

如果整个文档作为一个大块进入检索结果，系统很难精准定位到真正回答问题的部分。

---

### 8.2 长文档会增加上下文成本

LLM 的上下文窗口是有限的。

如果每次都把整篇文档塞进 prompt，会带来几个问题：

1. 输入内容太长。
2. 成本更高。
3. 响应速度更慢。
4. 模型容易被无关内容干扰。  

---

### 8.3 长文档不利于 source citation

RAG 项目强调回答要有来源引用。

如果文档没有被切分，系统只能说答案来自某一整篇文档。

但如果文档被切成 chunks，系统可以更精确地知道：

```text
答案来自哪个文件的哪个 chunk
```

这有助于提高回答的可追溯性。

---

## 9. Chunk 太大和太小的问题

### 9.1 Chunk 太大有什么问题？

如果 chunk 太大，会出现以下问题：

1. 一个 chunk 里混入太多无关信息。
2. 检索结果看起来相关，但实际答案不够精准。
3. 生成回答时，模型容易被无关内容干扰。
4. source citation 的颗粒度不够细。

例如，用户问：

```text
Does the product support private deployment?
```

如果系统返回的是整篇 deployment guide，里面可能包含部署方式、上线流程、环境要求、权限设置等很多内容。

这样虽然方向相关，但不够精准。

---

### 9.2 Chunk 太小有什么问题？

如果 chunk 太小，也会出现问题：

1. 单个 chunk 缺少上下文。
2. 模型拿到的信息不完整。
3. 回答可能片面。
4. 某些关键信息可能被拆散。

例如，如果一句话被拆成两个 chunk：

```text
The product supports private deployment
```

和：

```text
for enterprise customers only.
```

如果系统只检索到第一段，没有检索到第二段，就可能遗漏重要限制条件。

---

### 9.3 好的 chunking 应该追求什么？

一个好的 chunking 策略应该在两者之间平衡：

```text
上下文完整性
+
检索精准度
```

理想的 chunk 应该：

* 不太长，避免混入太多无关信息。
* 不太短，避免丢失上下文。
* 尽量按语义边界切分。
* 保留来源文件信息。
* 最好保留标题或段落结构。

---

## 10. outputs/document_chunks.json 真实观察

我打开了：

```text
outputs/document_chunks.json
```

观察到当前 chunk 结构如下：

```json
{
  "chunk_id": "chunk_0001",
  "source_file": "01_product_overview.md",
  "chunk_index": 1,
  "text": "# InsightFlow AI — Product Overview\n\nInsightFlow AI is a fictional B2B SaaS product created for a portfolio RAG project..."
}
```

这说明当前项目已经完成了文档切分，并且每个 chunk 都保存了来源信息。

其中：

```text
source_file
```

非常重要，因为它可以支持后续回答中的来源引用。

例如，当系统回答一个关于产品功能的问题时，可以引用：

```text
Source: 01_product_overview.md
```

当系统回答一个关于部署方式的问题时，可以引用：

```text
Source: 04_deployment_guide.md
```

---

## 11. 当前 chunking 的一个限制

我也观察到一个细节：

部分 chunk 可能会从单词中间开始，例如：

```text
ecurity documents, and customer cases into a searchable RAG knowledge base.
```

这说明当前 chunking 可能存在切分边界不够自然的问题。

也就是说，当前版本可能采用了比较简单的固定长度切分方式，或者切分时没有完全按单词、句子、段落或 Markdown 标题边界对齐。

这不是严重错误，因为当前阶段的目标是先跑通 RAG 流程。

但它是一个很好的后续优化点。

---

## 12. 当前 chunking 后续可以怎么优化？

后续可以从以下几个方向优化 chunking：

### 12.1 按 Markdown 标题切分

优先按照 Markdown 标题结构切分，例如：

```text
# 一级标题
## 二级标题
### 三级标题
```

这样可以让每个 chunk 更接近一个完整语义单元。

---

### 12.2 按段落切分

尽量不要从单词中间切断，也不要从一句话中间切断。

可以优先按段落进行切分。

---

### 12.3 增加 chunk overlap

如果两个 chunk 之间完全没有重叠，可能会丢失上下文。

可以增加一定 overlap，例如：

```text
chunk_size = 800
chunk_overlap = 100
```

这样可以让相邻 chunk 共享一小部分上下文。

---

### 12.4 保留 section title

在每个 chunk 中保留对应的标题信息。

例如：

```text
source_file: 04_deployment_guide.md
section_title: Private Deployment
text: ...
```

这样可以提高 retrieval 和 answer generation 的效果。

---

### 12.5 避免切断关键词

对于 B2B 售前场景中的关键词，例如：

```text
private deployment
on-premise deployment
role-based access control
enterprise plan
data encryption
```

应该尽量避免被切断。

因为这些关键词往往直接影响检索质量。

---

## 13. Chunking 与后续 Embedding 的关系

Chunking 的输出会成为 embedding 的输入。

当前项目中，后续 embedding 模块主要会处理每个 chunk 的：

```text
text
```

也就是说：

```text
chunk text
↓
embedding model
↓
vector representation
```

然后这些向量会被存入 Chroma 向量数据库。

因此，chunk 的质量会直接影响 embedding 和 retrieval 的质量。

如果 chunk 切得不好，后续即使 embedding 模型正常，检索效果也可能不理想。

---

## 14. Chunking 与 Source Citation 的关系

Source citation 是这个项目的重要特点。

在当前项目中，source citation 依赖于：

```text
source_file
```

因为每个 chunk 都保留了自己来自哪个 Markdown 文件。

当系统检索到某个 chunk 时，就可以知道它来自：

```text
01_product_overview.md
```

或者：

```text
04_deployment_guide.md
```

这使得最终回答可以带上来源引用。

在 B2B 售前场景中，这一点非常重要。

因为售前回答不能只是“听起来合理”，还要能追溯到公司资料。

---

## 15. 这两个模块在整个项目中的位置

`load_documents.py` 和 `chunk_documents.py` 在整个项目中的位置如下：

```text
knowledge_base/*.md
↓
load_documents.py
↓
documents
↓
chunk_documents.py
↓
outputs/document_chunks.json
↓
embedding_client.py
↓
build_vector_store.py
↓
vector_store/
↓
retrieve_context_chroma.py
↓
generate_answer_chroma.py
↓
sample_answer_chroma.md
```

也就是说：

* `load_documents.py` 负责读取原始知识库。
* `chunk_documents.py` 负责切分文档。
* `outputs/document_chunks.json` 是 chunking 阶段的结果。
* 后续 embedding 和 vector store 都基于这些 chunks 继续进行。

---

## 16. 面试表达：中文版本

如果面试官问：

> 你的 RAG 项目里文档是怎么处理的？

我可以这样回答：

> 在我的项目中，原始知识库是 `knowledge_base/` 文件夹中的 Markdown 文档，模拟的是 B2B SaaS 售前资料，包括产品介绍、价格、部署、安全、API、客户案例和异议处理等内容。
>
> 系统首先通过 `load_documents.py` 读取这些 Markdown 文件，然后通过 `chunk_documents.py` 把长文档切分成多个 chunks。
>
> 我实际观察了输出文件 `outputs/document_chunks.json`，每个 chunk 包含 `chunk_id`、`source_file`、`chunk_index` 和 `text` 字段。其中 `text` 会用于后续 embedding 和 retrieval，而 `source_file` 可以支持最终回答中的来源引用。
>
> 这样做的原因是，RAG 系统需要检索的是最相关的文档片段，而不是整篇文档。合理的 chunking 可以提升检索精准度，也能减少模型被无关上下文干扰的风险。

---

## 17. 面试表达：英文版本

If the interviewer asks:

> How do you process documents in your RAG project?

I can answer:

> In my project, the original knowledge base is stored as Markdown files under the `knowledge_base/` folder. These files simulate B2B SaaS pre-sales materials, including product overview, pricing, deployment guide, security documents, API integrations, customer case studies, and objection-handling notes.
>
> The system first uses `load_documents.py` to load these Markdown files, and then uses `chunk_documents.py` to split long documents into smaller chunks.
>
> I checked the actual output file `outputs/document_chunks.json`. Each chunk contains `chunk_id`, `source_file`, `chunk_index`, and `text`. The `text` field is used for embedding and retrieval, while `source_file` supports source citation in the final answer.
>
> This design allows the RAG system to retrieve the most relevant document segments instead of passing entire documents to the model. It improves retrieval precision and helps reduce hallucination by grounding answers in specific source documents.

---

## 18. 当前学习结论

通过阅读 `load_documents.py`、`chunk_documents.py` 和 `outputs/document_chunks.json`，我理解了当前 RAG 项目的前半段数据流：

```text
Markdown 文件
↓
读取为 documents
↓
切分为 chunks
↓
保存到 document_chunks.json
```

我也确认了当前项目中 chunk 的真实结构：

```text
chunk_id
source_file
chunk_index
text
```

这一步让我理解到：

> RAG 项目不是直接让 LLM 回答问题，而是先把企业知识库处理成可以被检索的结构化 chunks。后续的 embedding、vector database、retrieval 和 answer generation 都建立在这些 chunks 之上。

---

## 19. 当前版本可记录的优化方向

当前版本已经能完成基础 chunking，但后续可以继续优化：

1. 使用 Markdown-aware chunking，按标题和段落切分。
2. 避免从单词中间截断。
3. 增加 chunk overlap，保留上下文连续性。
4. 在 chunk 中增加 section title。
5. 对不同类型文档采用不同 chunking 策略。
6. 比较不同 chunk size 对 retrieval quality 的影响。
7. 在 evaluation 中记录 chunking 对回答质量的影响。

这些优化方向可以作为后续 RAG v3 的升级计划。

---

## 20. 今日完成标准

完成本文件后，我应该能够说清楚：

1. `load_documents.py` 的作用是什么。
2. `chunk_documents.py` 的作用是什么。
3. `outputs/document_chunks.json` 里每个 chunk 的真实结构是什么。
4. 为什么 RAG 需要 chunking。
5. chunk 太大和太小分别有什么问题。
6. 当前 chunking 有什么限制。
7. 后续可以如何优化 chunking。
8. 这部分内容如何在面试中表达。

---

## 21. 一句话总结

`load_documents.py` 负责把 Markdown 知识库读进系统，`chunk_documents.py` 负责把长文档切分成包含 `chunk_id`、`source_file`、`chunk_index` 和 `text` 的 chunks；这些 chunks 是后续 embedding、Chroma 检索和带来源回答生成的基础。
