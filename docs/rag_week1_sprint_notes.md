# 6.1 - 6.7 RAG 项目学习执行手册

## 0. 本周总目标

本周目标不是“继续学一堆 AI 概念”，而是把当前 RAG 项目中最核心的 7 个模块彻底讲清楚：

```text
6.1 Embedding
6.2 Chroma Vector Store
6.3 Retrieval
6.4 Answer Generation
6.5 Project Engineering
6.6 Evaluation v1
6.7 Evaluation Report
```

本周结束后，我要达到三个结果：

1. 能解释每个核心模块在 RAG 流程中的作用。
2. 能把每个模块和自己项目中的具体文件对应起来。
3. 能产出一批可以放进 GitHub、简历和面试材料的文档。

---

## 1. 本周最终交付物

本周需要完成以下文件：

```text
docs/embedding_notes.md
docs/vector_store_notes.md
docs/retrieval_test_notes.md
docs/answer_generation_notes.md
docs/engineering_notes.md
docs/evaluation_report.md
eval/sample_eval_questions.csv
```

本周 Git 提交建议：

```bash
git add docs/embedding_notes.md docs/vector_store_notes.md docs/retrieval_test_notes.md docs/answer_generation_notes.md docs/engineering_notes.md docs/evaluation_report.md eval/sample_eval_questions.csv
git commit -m "docs: add RAG module notes and evaluation report"
git push origin main
```

---

## 2. 每天固定执行流程

每天按照下面流程执行，不要乱跳。

```text
第一步：读对应代码文件 20-30 分钟
第二步：写清输入、输出、作用 20 分钟
第三步：运行或观察项目结果 20-30 分钟
第四步：写项目文档 30-40 分钟
第五步：写一句面试表达 10 分钟
```

每天结束前必须问自己：

```text
1. 今天我理解了哪个 RAG 模块？
2. 这个模块在我的项目里对应哪个文件？
3. 它的输入是什么？
4. 它的输出是什么？
5. 面试官问到时我能不能讲 60 秒？
```

---

# 6.1 Embedding 理解

## 今日目标

今天要理解：

```text
Embedding 是什么？
为什么它比关键词搜索强？
它在我的项目里对应哪个文件？
```

今日对应文件：

```text
rag_app/embedding_client.py
```

今日产出文件：

```text
docs/embedding_notes.md
```

---

## 第一步：打开并阅读 `embedding_client.py`

阅读时只看三个问题：

```text
1. 这个文件是否负责生成 embedding？
2. 它输入的是什么？
3. 它输出的是什么？
```

不用逐行死磕代码，先理解它在 RAG 流程中的位置。

---

## 第二步：理解 Embedding 在 RAG 中的位置

Embedding 位于 RAG 流程中的这一段：

```text
Document Chunks
↓
Embedding Model
↓
Vector Representations
↓
Vector Store
```

它的作用是：

> 把文本转换成向量，让计算机可以比较不同文本之间的语义相似度。

---

## 第三步：新建文档

在 `docs/` 中新建：

```text
embedding_notes.md
```

粘贴以下内容。

---

# Embedding Notes：RAG 项目中的语义向量理解

## 1. Embedding 是什么？

Embedding 是一种把文本转换成数字向量的方法。

在 RAG 系统中，原始文本不能直接被向量数据库用于语义检索，所以需要先通过 embedding model 把文本转换成向量表示。

简单来说：

```text
一段文本
↓
Embedding Model
↓
一组数字向量
```

这些数字向量可以表示文本的语义含义。

---

## 2. 为什么 Embedding 比关键词搜索强？

关键词搜索主要依赖字面匹配。

例如用户问：

```text
Can we host the product ourselves?
```

但知识库中可能写的是：

```text
The product supports private deployment for enterprise customers.
```

这两个句子没有完全相同的关键词：

```text
host it ourselves
private deployment
```

但它们在语义上都在问：

```text
是否支持私有化部署？
```

Embedding 的价值就在于：

> 即使用户问题和文档内容使用了不同表达方式，系统也可以根据语义相似度找到相关内容。

---

## 3. 在我的项目中，Embedding 对应哪里？

在当前项目中，Embedding 相关逻辑主要对应：

```text
rag_app/embedding_client.py
```

这个文件的作用可以理解为：

```text
输入文本
↓
生成 embedding
↓
返回向量表示
```

后续这些向量会被存入 Chroma 向量数据库，用于语义检索。

---

## 4. Embedding 的输入是什么？

Embedding 的输入通常是 chunk 的文本内容。

在当前项目中，`outputs/document_chunks.json` 中每个 chunk 包含：

```text
chunk_id
source_file
chunk_index
text
```

其中真正用于 embedding 的主要字段是：

```text
text
```

也就是说：

```text
chunk["text"]
↓
embedding_client.py
↓
embedding vector
```

---

## 5. Embedding 的输出是什么？

Embedding 的输出是一组数字向量。

这些向量本身不是给人直接阅读的，而是给向量数据库用于计算相似度。

例如：

```text
Question Embedding
与
Chunk Embedding
```

可以通过相似度计算判断它们是否语义相关。

---

## 6. 三个语义相似但关键词不同的例子

### 例子 1：私有化部署

用户问题：

```text
Can we host the product ourselves?
```

知识库表达：

```text
The product supports private deployment for enterprise customers.
```

语义关系：

```text
host the product ourselves ≈ private deployment
```

---

### 例子 2：系统集成

用户问题：

```text
Can this tool connect with our CRM?
```

知识库表达：

```text
InsightFlow AI supports integration with third-party CRM systems through APIs.
```

语义关系：

```text
connect with our CRM ≈ CRM integration
```

---

### 例子 3：权限控制

用户问题：

```text
Can different team members have different access levels?
```

知识库表达：

```text
The platform supports role-based access control.
```

语义关系：

```text
different access levels ≈ role-based access control
```

---

## 7. 面试表达

如果面试官问：

> 什么是 Embedding？为什么你的 RAG 项目需要 Embedding？

我可以这样回答：

> Embedding 是把文本转换成向量表示的方法。它可以让系统基于语义相似度检索内容，而不是只依赖关键词匹配。
>
> 在我的 RAG 项目中，知识库文档会先被切分成 chunks，然后每个 chunk 的 `text` 会通过 embedding model 转成向量，并存入 Chroma 向量数据库。
>
> 当用户提出问题时，系统也会把问题转成 embedding，再和数据库中的 chunk embeddings 做相似度匹配，从而找到最相关的文档片段。
>
> 这对于 B2B 售前场景很重要，因为客户可能不会使用和文档完全一样的词。例如客户问 “Can we host the product ourselves?”，系统应该能匹配到文档中的 “private deployment”。

---

## 8. 一句话总结

Embedding 让 RAG 系统可以从关键词匹配升级为语义检索，是连接用户自然语言问题和知识库文档 chunks 的关键步骤。

---

# 6.2 Chroma 向量库

## 今日目标

今天要理解：

```text
Chroma 是什么？
vector_store/ 是什么？
什么时候需要重建向量库？
```

今日对应文件：

```text
rag_app/build_vector_store.py
vector_store/
```

今日产出文件：

```text
docs/vector_store_notes.md
```

---

## 第一步：阅读 `build_vector_store.py`

重点看三个问题：

```text
1. 它从哪里读取 chunks？
2. 它如何生成或调用 embedding？
3. 它把向量保存到哪里？
```

---

## 第二步：理解 `vector_store/`

`vector_store/` 不是普通输出文件夹。

它的含义是：

> Chroma 本地向量数据库的存储位置。

它保存的是：

```text
chunk text 的 embedding
chunk 对应的 source_file
chunk 对应的 metadata 或来源信息
```

---

## 第三步：重新构建一次向量库

如果你的项目支持删除并重建，可以执行：

```powershell
Remove-Item -Recurse -Force vector_store
python rag_app/build_vector_store.py
```

如果命令报错，先不要慌，记录报错内容即可。

如果项目入口是模块方式，尝试：

```powershell
python -m rag_app.build_vector_store
```

---

## 第四步：新建文档

在 `docs/` 中新建：

```text
vector_store_notes.md
```

粘贴以下内容。

---

# Vector Store Notes：Chroma 向量库理解

## 1. Chroma 是什么？

Chroma 是一个向量数据库，常用于 RAG 应用中存储和检索文本向量。

在我的项目中，它的作用是：

```text
保存文档 chunks 的 embeddings
支持用户问题的语义检索
返回最相关的 Top-K chunks
```

---

## 2. 为什么 RAG 需要向量数据库？

RAG 系统需要根据用户问题找到最相关的知识库片段。

如果只靠普通关键词搜索，可能无法处理语义相似但表达不同的问题。

向量数据库可以保存每个 chunk 的 embedding，并在用户提问时进行相似度检索。

流程如下：

```text
chunk text
↓
embedding
↓
Chroma vector store
↓
semantic retrieval
```

---

## 3. 在我的项目中，Chroma 对应哪里？

当前项目中，Chroma 相关逻辑主要对应：

```text
rag_app/build_vector_store.py
vector_store/
```

其中：

```text
build_vector_store.py
```

负责构建向量库。

```text
vector_store/
```

是 Chroma 本地向量索引的保存位置。

---

## 4. build_vector_store.py 的作用

`build_vector_store.py` 的作用可以理解为：

```text
读取 document_chunks.json
↓
提取每个 chunk 的 text
↓
生成 embeddings
↓
写入 Chroma 向量数据库
↓
保存到 vector_store/
```

它通常不是每次用户提问都运行。

它更像是一个索引构建脚本。

---

## 5. 什么时候需要重建向量库？

以下情况需要重新构建向量库：

1. 新增了知识库 Markdown 文件。
2. 修改了已有知识库内容。
3. 改变了 chunking 策略。
4. 更换了 embedding model。
5. 删除或重命名了 source_file。
6. vector_store 文件夹损坏或丢失。

如果只是用户提出新问题，通常不需要重建向量库。

---

## 6. vector_store/ 为什么不是普通文件夹？

`vector_store/` 看起来像普通文件夹，但它实际保存的是 Chroma 的本地索引数据。

它不是给人直接阅读的，而是给程序查询使用的。

可以理解为：

```text
Markdown 文档是人类可读知识
document_chunks.json 是切分后的中间结果
vector_store/ 是机器可检索的向量索引
```

---

## 7. Chroma 和 FAISS 的简单区别

| 对比          | Chroma         | FAISS     |
| ----------- | -------------- | --------- |
| 定位          | 应用友好的向量数据库     | 高性能向量检索库  |
| 易用性         | 更适合快速构建 RAG 应用 | 更偏底层和工程优化 |
| Metadata 管理 | 比较方便           | 通常需要自己管理  |
| 当前项目适配度     | 更适合当前阶段        | 可作为后续优化方向 |

---

## 8. 面试表达

如果面试官问：

> 你为什么用 Chroma？vector_store/ 是什么？

我可以这样回答：

> 在我的项目中，我使用 Chroma 作为本地向量数据库，用来保存知识库 chunks 的 embeddings。
>
> `build_vector_store.py` 会读取切分后的 chunks，生成 embeddings，并把它们写入 Chroma。`vector_store/` 文件夹就是 Chroma 的本地持久化存储位置。
>
> 当用户提问时，系统会把问题也转成 embedding，然后在 Chroma 中做相似度检索，返回最相关的 Top-K chunks。
>
> 我选择 Chroma 是因为它比较适合快速构建本地 RAG 应用，并且方便管理文档和来源信息。后续如果数据规模更大，可以考虑对比 FAISS。

---

## 9. 一句话总结

Chroma 是当前项目的本地向量数据库，`vector_store/` 保存的是知识库 chunks 的向量索引；当知识库、chunking 或 embedding 发生变化时，需要重建向量库。

---

# 6.3 检索模块

## 今日目标

今天要理解：

```text
Retrieval 是什么？
Top-K 是什么？
source citation 是什么？
retrieval relevance 是什么？
```

今日对应文件：

```text
rag_app/retrieve_context_chroma.py
```

今日产出文件：

```text
docs/retrieval_test_notes.md
```

---

## 第一步：阅读 `retrieve_context_chroma.py`

重点看：

```text
1. 用户问题是如何进入检索流程的？
2. 系统是否会把问题转成 embedding？
3. 系统如何调用 Chroma？
4. 返回的结果里是否包含 source_file？
```

---

## 第二步：准备 5 个测试问题

使用下面 5 个问题测试：

```text
1. Does the product support private deployment?
2. Can this product integrate with our CRM system?
3. How does the system protect customer data?
4. Which pricing plan is suitable for enterprise customers?
5. Do you have customer case studies in similar industries?
```

---

## 第三步：新建文档

在 `docs/` 中新建：

```text
retrieval_test_notes.md
```

粘贴以下内容。

---

# Retrieval Test Notes：Chroma 检索模块理解

## 1. Retrieval 是什么？

Retrieval 是 RAG 流程中负责“找资料”的步骤。

它的作用是：

```text
用户问题
↓
转成 embedding
↓
到向量数据库中检索
↓
返回最相关的 chunks
```

RAG 的关键不是让模型凭空回答，而是先找出和问题最相关的知识库内容。

---

## 2. 在我的项目中，Retrieval 对应哪里？

当前项目中，检索模块主要对应：

```text
rag_app/retrieve_context_chroma.py
```

它的作用可以理解为：

```text
输入 question
↓
生成 question embedding
↓
查询 Chroma vector store
↓
返回 Top-K relevant chunks
```

---

## 3. Top-K 是什么？

Top-K 表示系统返回最相关的前 K 个检索结果。

例如：

```text
Top-K = 3
```

表示系统会返回最相关的 3 个 chunks。

Top-K 太小可能漏掉重要信息。

Top-K 太大可能引入无关内容。

因此，Top-K 需要在召回率和精准度之间平衡。

---

## 4. Source Citation 是什么？

Source citation 指的是回答中包含来源引用。

在当前项目中，来源通常来自：

```text
source_file
```

例如：

```text
Source: 04_deployment_guide.md
```

这对于 B2B 售前场景非常重要，因为客户关于价格、安全、部署的问题都需要有依据，不能靠模型自由发挥。

---

## 5. Retrieval Relevance 是什么？

Retrieval relevance 指检索结果和用户问题的相关程度。

例如用户问：

```text
Does the product support private deployment?
```

理想情况下，系统应该检索到：

```text
04_deployment_guide.md
```

如果检索到了 `03_pricing_and_packaging.md`，说明结果可能不够相关。

---

## 6. 5 个测试问题记录

| 测试问题                                                     | 预期来源                            | 实际来源 | 是否合理 | 备注           |
| -------------------------------------------------------- | ------------------------------- | ---- | ---- | ------------ |
| Does the product support private deployment?             | `04_deployment_guide.md`        | 待填写  | 待填写  | 部署相关问题       |
| Can this product integrate with our CRM system?          | `06_integrations_and_api.md`    | 待填写  | 待填写  | API / CRM 集成 |
| How does the system protect customer data?               | `05_security_and_governance.md` | 待填写  | 待填写  | 安全治理         |
| Which pricing plan is suitable for enterprise customers? | `03_pricing_and_packaging.md`   | 待填写  | 待填写  | 企业套餐         |
| Do you have customer case studies in similar industries? | `07_customer_case_studies.md`   | 待填写  | 待填写  | 客户案例         |

---

## 7. 一个成功案例

成功案例待填写：

```text
Question:
Expected Source:
Retrieved Source:
Why it is successful:
```

示例：

```text
Question:
Does the product support private deployment?

Expected Source:
04_deployment_guide.md

Retrieved Source:
04_deployment_guide.md

Why it is successful:
The question is about deployment options, and the retrieved source is the deployment guide. This means the system correctly matched the user's intent with the relevant knowledge document.
```

---

## 8. 一个失败案例

失败案例待填写：

```text
Question:
Expected Source:
Retrieved Source:
Problem:
Possible Improvement:
```

示例：

```text
Question:
Can different team members have different access levels?

Expected Source:
05_security_and_governance.md

Retrieved Source:
01_product_overview.md

Problem:
The system retrieved a general product overview instead of the security and governance document.

Possible Improvement:
Improve chunking, include section titles, adjust Top-K, or add more explicit security-related text in the knowledge base.
```

---

## 9. 面试表达

如果面试官问：

> 你怎么判断 RAG 检索结果好不好？

我可以这样回答：

> 我会用一组测试问题检查 retrieval relevance。
>
> 例如用户问 “Does the product support private deployment?”，理想情况下系统应该检索到 `04_deployment_guide.md`，因为这个问题属于部署场景。
>
> 我会记录 expected source 和 retrieved source，并判断结果是否合理。这样可以评估系统是否真的找到了正确的知识来源，而不是只看最终回答是否流畅。

---

## 10. 一句话总结

Retrieval 是 RAG 中负责找依据的步骤，Top-K 控制返回多少个相关 chunks，source citation 让回答可追溯，retrieval relevance 用来判断检索结果是否真的匹配用户问题。

---

# 6.4 回答生成模块

## 今日目标

今天要理解：

```text
Answer Generation 是什么？
Mock LLM 为什么合理？
回答模板为什么要包含 question、context、answer、sources？
```

今日对应文件：

```text
rag_app/generate_answer_chroma.py
```

今日产出文件：

```text
docs/answer_generation_notes.md
```

---

## 第一步：阅读 `generate_answer_chroma.py`

重点看：

```text
1. 输入是否包含 question？
2. 输入是否包含 retrieved context？
3. 输出是否包含 answer？
4. 输出是否包含 sources？
```

---

## 第二步：新建文档

在 `docs/` 中新建：

```text
answer_generation_notes.md
```

粘贴以下内容。

---

# Answer Generation Notes：RAG 回答生成模块理解

## 1. Answer Generation 是什么？

Answer Generation 是 RAG 流程中负责“生成最终回答”的步骤。

它不是直接凭空回答，而是基于前一步 retrieval 返回的 context 生成回答。

流程如下：

```text
User Question
↓
Retrieved Context
↓
Answer Generation
↓
Answer + Sources
```

---

## 2. 在我的项目中，回答生成对应哪里？

当前项目中，回答生成模块主要对应：

```text
rag_app/generate_answer_chroma.py
```

它的作用可以理解为：

```text
输入 question
输入 retrieved context
生成 answer
返回 sources
```

---

## 3. 为什么回答模板要包含 question？

`question` 是用户真正想问的问题。

如果没有 question，系统不知道应该围绕哪个目标组织答案。

在售前场景中，问题非常重要，因为不同客户问题背后的意图不同。

例如：

```text
Does the product support private deployment?
```

背后可能关心：

```text
部署灵活性
企业版能力
数据控制权
合规要求
```

---

## 4. 为什么回答模板要包含 context？

`context` 是 retrieval 模块找回来的相关知识片段。

RAG 的核心就是：

> 让模型基于 context 回答，而不是凭空回答。

如果没有 context，模型可能生成流畅但不可靠的内容。

---

## 5. 为什么回答模板要包含 answer？

`answer` 是系统最终给用户的回答。

在 B2B 售前场景中，answer 应该满足：

```text
准确
简洁
专业
有依据
能回应客户真实问题
```

---

## 6. 为什么回答模板要包含 sources？

`sources` 是答案的来源引用。

它可以告诉用户：

```text
这个回答来自哪份知识库文档
```

这对于售前非常重要，因为价格、部署、安全、合同相关内容都不能随便编造。

---

## 7. 当前用 Mock LLM 为什么合理？

当前项目使用 Mock LLM 或模板化回答是合理的，因为当前阶段的重点是验证 RAG pipeline 是否完整。

也就是说，先确认以下流程能跑通：

```text
文档读取
↓
文档切分
↓
embedding
↓
Chroma 检索
↓
基于 context 生成 answer
↓
返回 sources
```

Mock LLM 的价值是：

1. 保证项目可以本地运行。
2. 不依赖 API key。
3. 降低调用成本。
4. 方便面试官复现。
5. 先展示完整工程流程。

未来可以接入：

```text
OpenAI API
Qwen API
DeepSeek API
```

---

## 8. 一个好的售前 RAG Prompt 应该包含什么？

一个好的售前 RAG Prompt 应该包含：

```text
Role: 你是一个 B2B SaaS 售前知识助手
Context: 检索到的知识库片段
Question: 用户问题
Rules: 只能基于 context 回答
Output Format: answer + sources
Fallback: 如果资料不足，说明无法确认
```

---

## 9. 面试表达

如果面试官问：

> 你的项目为什么还没有接真实 LLM API？

我可以这样回答：

> 当前版本主要关注 RAG pipeline 的完整性和可复现性，所以我先使用 Mock LLM 或模板化生成。
>
> 这样可以保证项目在本地没有 API key 的情况下也能运行，并且可以清楚展示文档读取、chunking、embedding、Chroma 检索、answer generation 和 source citation 的完整流程。
>
> 后续如果要升级成真实应用，可以很自然地把回答生成模块替换为 OpenAI、Qwen 或 DeepSeek API。

---

## 10. 一句话总结

回答生成模块负责基于 retrieved context 生成 answer，并返回 sources；当前使用 Mock LLM 是为了保证本地可复现，未来可以替换成真实 LLM API。

---

# 6.5 项目工程化

## 今日目标

今天要理解：

```text
requirements.txt 是什么？
.gitignore 是什么？
为什么不能上传 .venv？
别人 clone 项目后怎么运行？
```

今日对应文件：

```text
requirements.txt
.gitignore
README.md
```

今日产出文件：

```text
docs/engineering_notes.md
```

---

## 第一步：检查 `requirements.txt`

打开：

```text
requirements.txt
```

检查里面是否包含项目运行需要的依赖，例如：

```text
chromadb
sentence-transformers
pandas
numpy
```

以你项目实际内容为准，不要乱加。

---

## 第二步：检查 `.gitignore`

打开：

```text
.gitignore
```

确认是否排除了：

```text
.venv/
__pycache__/
*.pyc
.env
vector_store/
```

注意：

是否提交 `vector_store/` 要看你的项目策略。

如果希望别人 clone 后自己重建向量库，可以不上传 `vector_store/`。

如果希望别人直接运行 demo，可以考虑保留必要的 sample output，但不建议上传过大的本地索引。

---

## 第三步：新建文档

在 `docs/` 中新建：

```text
engineering_notes.md
```

粘贴以下内容。

---

# Engineering Notes：RAG 项目工程化理解

## 1. 为什么项目需要工程化？

一个项目不能只是“我本地能跑”。

如果要放到 GitHub 或给面试官看，需要让别人也能理解和运行。

工程化的目标是：

```text
结构清晰
依赖明确
运行步骤明确
敏感文件不泄露
不上传无用缓存
方便后续扩展
```

---

## 2. requirements.txt 是什么？

`requirements.txt` 用于记录 Python 项目需要安装的依赖。

别人 clone 项目后，可以通过：

```bash
pip install -r requirements.txt
```

安装项目需要的包。

这比让别人手动猜依赖更专业。

---

## 3. .gitignore 是什么？

`.gitignore` 用于告诉 Git 哪些文件不应该上传到 GitHub。

常见不应该上传的内容包括：

```text
.venv/
__pycache__/
*.pyc
.env
临时文件
大文件
缓存文件
```

---

## 4. 为什么不能上传 .venv？

`.venv/` 是本地虚拟环境，通常很大，而且和个人电脑环境有关。

如果上传到 GitHub，会有几个问题：

1. 仓库体积变大。
2. 不同系统可能不兼容。
3. 没有必要。
4. 不符合 Python 项目规范。

正确做法是：

```text
上传 requirements.txt
忽略 .venv/
让别人自己创建虚拟环境并安装依赖
```

---

## 5. 为什么 API key 不能写进代码？

如果未来接入真实 LLM API，例如 OpenAI、Qwen 或 DeepSeek，API key 不能直接写在代码里。

原因是：

1. 会泄露账号权限。
2. 可能产生费用风险。
3. 不符合安全规范。

正确做法是：

```text
把 API key 放进 .env
把 .env 加入 .gitignore
代码从环境变量读取 API key
```

---

## 6. 别人 clone 项目后应该怎么运行？

理想情况下，README 中应该写清：

```bash
git clone <repo-url>
cd RAG-based-AI-Presales-Knowledge-Assistant
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python rag_app/build_vector_store.py
python rag_app/main_chroma.py
```

如果模块运行方式更稳定，也可以写：

```bash
python -m rag_app.build_vector_store
python -m rag_app.main_chroma
```

---

## 7. 面试表达

如果面试官问：

> 你的项目怎么保证别人可以运行？

我可以这样回答：

> 我会通过 `requirements.txt` 管理依赖，通过 `.gitignore` 排除虚拟环境、缓存和敏感文件，并在 README 中写清安装和运行步骤。
>
> 对于 RAG 项目，别人 clone 后需要先安装依赖，然后运行向量库构建脚本，再运行主程序进行问答。
>
> 如果未来接入真实 LLM API，我会把 API key 放在 `.env` 中，并确保 `.env` 不上传到 GitHub。

---

## 8. 一句话总结

工程化的目标是让项目不仅在我本地能跑，也能被别人理解、复现和扩展。

---

# 6.6 Evaluation v1

## 今日目标

今天要扩展评估问题集：

```text
eval/sample_eval_questions.csv
```

至少 20 条问题。

覆盖：

```text
pricing
security
deployment
API
case studies
objection handling
```

---

## 第一步：确定 CSV 字段

建议使用以下字段：

```text
question,expected_source,category,notes
```

---

## 第二步：补充 20 条测试问题

打开：

```text
eval/sample_eval_questions.csv
```

补充以下内容。

```csv
question,expected_source,category,notes
What are the core features of InsightFlow AI?,01_product_overview.md,product,Product overview question
Who are the target users of InsightFlow AI?,01_product_overview.md,product,Target user question
What does the AI Customer Segmentation Dashboard do?,01_product_overview.md,product,Module question
What does the AI Pre-sales Knowledge Assistant do?,01_product_overview.md,product,RAG module question
What are the most common questions customers ask?,02_faq.md,faq,General FAQ question
Which pricing plan is suitable for enterprise customers?,03_pricing_and_packaging.md,pricing,Enterprise pricing question
What is the difference between standard and enterprise plans?,03_pricing_and_packaging.md,pricing,Plan comparison
Does the product support private deployment?,04_deployment_guide.md,deployment,Private deployment question
How long does deployment usually take?,04_deployment_guide.md,deployment,Deployment timeline
Can the product be deployed in a customer's own cloud environment?,04_deployment_guide.md,deployment,Cloud deployment question
How does the system protect customer data?,05_security_and_governance.md,security,Data protection
Does the product support role-based access control?,05_security_and_governance.md,security,RBAC question
Does the system provide audit logs?,05_security_and_governance.md,security,Audit log question
Can this product integrate with our CRM system?,06_integrations_and_api.md,api,CRM integration
Does the product provide APIs for integration?,06_integrations_and_api.md,api,API support
Can InsightFlow AI connect with BI tools?,06_integrations_and_api.md,api,BI integration
Do you have customer case studies in similar industries?,07_customer_case_studies.md,case_study,Customer case question
What business outcomes have customers achieved?,07_customer_case_studies.md,case_study,Outcome question
What should we say if the customer thinks the price is too high?,08_objection_handling.md,objection,Price objection
How should we respond if the customer worries about migration risk?,08_objection_handling.md,objection,Migration objection
Can you draft a follow-up email after a pre-sales meeting?,09_presales_email_templates.md,email,Email template
Can you write an email summarizing the proposed solution?,09_presales_email_templates.md,email,Solution summary email
```

---

## 第三步：理解 Evaluation 的意义

Evaluation 不是为了证明系统完美，而是为了发现系统哪里不稳定。

当前阶段主要评估：

```text
1. 是否检索到正确来源
2. 回答是否相关
3. 引用是否正确
4. 是否存在失败案例
```

---

## 第四步：面试表达

如果面试官问：

> 你怎么评估你的 RAG 项目？

我可以这样回答：

> 我设计了一个 evaluation question set，覆盖产品、价格、部署、安全、API、客户案例和异议处理等典型售前问题。
>
> 每个问题都标注了 expected source，例如 private deployment 问题应该命中 `04_deployment_guide.md`。
>
> 然后我会运行这些问题，记录系统实际 retrieved source、answer quality 和 citation correctness。这样可以判断系统是否真正检索到了正确文档，而不是只生成了看起来合理的回答。

---

# 6.7 Evaluation Report

## 今日目标

今天要把 6.6 的测试问题跑一遍，并产出：

```text
docs/evaluation_report.md
```

需要记录：

```text
retrieved_source
answer_quality
citation_correct
success cases
failure cases
next improvements
```

---

## 第一步：运行测试问题

你可以先手动跑 5-10 条，不一定当天完全自动化。

优先跑这些问题：

```text
Does the product support private deployment?
Can this product integrate with our CRM system?
How does the system protect customer data?
Which pricing plan is suitable for enterprise customers?
Do you have customer case studies in similar industries?
What should we say if the customer thinks the price is too high?
```

---

## 第二步：新建文档

在 `docs/` 中新建：

```text
evaluation_report.md
```

粘贴以下内容。

---

# Evaluation Report：RAG 项目评估报告

## 1. 评估目标

本评估报告用于记录当前 RAG 项目的初步评估结果。

评估目标不是证明系统完美，而是检查：

```text
1. 系统是否能检索到正确文档
2. 回答是否和问题相关
3. 来源引用是否正确
4. 哪些问题容易失败
5. 后续应该如何优化
```

---

## 2. 评估问题集

本次评估问题集位于：

```text
eval/sample_eval_questions.csv
```

问题覆盖以下类别：

```text
product
faq
pricing
deployment
security
api
case_study
objection
email
```

每个问题包含：

```text
question
expected_source
category
notes
```

---

## 3. 评估指标

当前阶段采用人工评估方式，主要看以下指标：

| 指标                   | 含义                      |
| -------------------- | ----------------------- |
| Retrieval Hit        | 系统是否检索到 expected_source |
| Citation Correctness | answer 中的 source 是否正确   |
| Answer Relevance     | 回答是否针对用户问题              |
| Faithfulness         | 回答是否忠于检索到的 context      |
| Failure Type         | 如果失败，属于哪类失败             |

---

## 4. 测试结果记录表

| 问题                                                               | Expected Source                 | Retrieved Source | Answer Quality | Citation Correct | 备注     |
| ---------------------------------------------------------------- | ------------------------------- | ---------------- | -------------- | ---------------- | ------ |
| Does the product support private deployment?                     | `04_deployment_guide.md`        | 待填写              | 待填写            | 待填写              | 部署问题   |
| Can this product integrate with our CRM system?                  | `06_integrations_and_api.md`    | 待填写              | 待填写            | 待填写              | API 集成 |
| How does the system protect customer data?                       | `05_security_and_governance.md` | 待填写              | 待填写            | 待填写              | 安全问题   |
| Which pricing plan is suitable for enterprise customers?         | `03_pricing_and_packaging.md`   | 待填写              | 待填写            | 待填写              | 价格问题   |
| Do you have customer case studies in similar industries?         | `07_customer_case_studies.md`   | 待填写              | 待填写            | 待填写              | 客户案例   |
| What should we say if the customer thinks the price is too high? | `08_objection_handling.md`      | 待填写              | 待填写            | 待填写              | 异议处理   |

---

## 5. 成功案例

### Case 1：Private Deployment

```text
Question:
Does the product support private deployment?

Expected Source:
04_deployment_guide.md

Retrieved Source:
待填写

Result:
待填写
```

分析：

```text
如果 retrieved source 是 04_deployment_guide.md，说明系统能够根据 deployment 相关语义找到正确知识来源。
```

---

## 6. 失败案例

### Case 1：待填写

```text
Question:
待填写

Expected Source:
待填写

Retrieved Source:
待填写

Failure Type:
待填写

Possible Reason:
待填写

Improvement:
待填写
```

常见失败类型包括：

```text
1. Retrieved source 不正确
2. Answer 太泛
3. Source citation 缺失
4. Context 不足
5. 问题表达和知识库表达差距太大
```

---

## 7. 当前评估结论

当前项目已经具备基础 RAG 问答能力：

```text
文档读取
↓
chunking
↓
embedding
↓
Chroma retrieval
↓
answer generation
↓
source citation
```

但从评估角度看，后续仍需要重点优化：

1. 检索结果是否稳定命中正确 source。
2. chunking 是否保留足够上下文。
3. answer 是否严格基于 retrieved context。
4. source citation 是否准确。
5. 对资料不足的问题是否能 fallback，而不是硬编。

---

## 8. 后续优化方向

后续可以从以下方向优化：

1. 增加更多 evaluation questions。
2. 对比不同 chunk size 的检索效果。
3. 增加 chunk overlap。
4. 保留 Markdown section title。
5. 调整 Top-K 参数。
6. 增加 reranking。
7. 增加 fallback prompt。
8. 增加 human-in-the-loop 审核机制。
9. 接入真实 LLM API。
10. 用 Streamlit 做可视化 demo。

---

## 9. 面试表达

如果面试官问：

> 你怎么证明你的 RAG 项目不是只会生成答案？

我可以这样回答：

> 我没有只看最终回答是否流畅，而是设计了 evaluation question set 来测试 retrieval 和 answer quality。
>
> 每个问题都标注 expected source，例如 private deployment 问题应该命中 `04_deployment_guide.md`。
>
> 我会记录实际 retrieved source、answer quality、citation correctness 和 failure cases。
>
> 这样可以判断系统是否真正基于正确资料回答，而不是生成一个看起来合理但没有依据的答案。

---

## 10. 一句话总结

Evaluation 的意义不是证明系统完美，而是用测试问题系统性发现 RAG 项目在 retrieval、citation、answer relevance 和 faithfulness 上的优缺点。

---

# 本周最终 Git 提交

本周完成后，运行：

```bash
git status
```

确认新增或修改的文件包括：

```text
docs/embedding_notes.md
docs/vector_store_notes.md
docs/retrieval_test_notes.md
docs/answer_generation_notes.md
docs/engineering_notes.md
docs/evaluation_report.md
eval/sample_eval_questions.csv
```

然后提交：

```bash
git add docs/embedding_notes.md docs/vector_store_notes.md docs/retrieval_test_notes.md docs/answer_generation_notes.md docs/engineering_notes.md docs/evaluation_report.md eval/sample_eval_questions.csv
git commit -m "docs: add RAG module notes and evaluation report"
git push origin main
```

---

# 本周验收标准

完成本周任务后，我应该能回答以下问题：

1. Embedding 是什么，为什么比关键词搜索强？
2. Chroma 是什么，`vector_store/` 保存了什么？
3. 什么时候需要重建向量库？
4. Retrieval 是什么，Top-K 是什么？
5. 为什么 source citation 对 B2B 售前很重要？
6. Mock LLM 为什么合理？
7. `requirements.txt` 和 `.gitignore` 有什么作用？
8. 为什么不能上传 `.venv/`？
9. 如何设计 RAG evaluation questions？
10. 如何判断 retrieved source 是否正确？
11. 如何记录成功案例和失败案例？
12. 后续如何优化 RAG 项目？

---

# 本周一句话总结

这一周的目标不是继续堆新功能，而是把 RAG 项目的核心模块逐个讲清楚：Embedding 负责语义表示，Chroma 负责向量存储，Retrieval 负责找依据，Answer Generation 负责基于 context 生成回答，Engineering 让项目可复现，Evaluation 让项目质量可验证。
