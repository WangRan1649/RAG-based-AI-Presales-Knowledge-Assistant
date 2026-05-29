# Query Walkthrough：手动追踪一次 RAG 问答流程

## 1. 测试问题

本次测试问题是：

```text
Does the product support private deployment?
```

这个问题属于 B2B SaaS 售前场景中的部署问题。

客户真正关心的是：

* 产品是否支持私有化部署？
* 是否可以部署在客户自己的服务器或云环境中？
* 企业客户是否有更灵活的部署选项？

---

## 2. 预期知识来源

这个问题最可能命中的知识库文件是：

```text
knowledge_base/04_deployment_guide.md
```

原因是：

这个文件主要说明产品的部署方式、上线流程、云部署或私有化部署等内容。

---

## 3. RAG 调用链

这个问题在系统中的完整流程如下：

```text
User Question
↓
Embedding
↓
Chroma Vector Store Retrieval
↓
Top-K Relevant Chunks
↓
Answer Generation
↓
Answer + Sources
```

更具体地说：

1. 用户输入问题：

```text
Does the product support private deployment?
```

2. 系统将这个问题转成 embedding。

3. `retrieve_context_chroma.py` 使用这个 embedding 到 Chroma 向量库中检索相关 chunks。

4. 系统返回与 `private deployment` 最相关的 Top-K chunks。

5. 这些 chunks 通常应该来自：

```text
04_deployment_guide.md
```

6. `generate_answer_chroma.py` 基于检索到的 context 生成回答。

7. 最终输出 answer，并附带 source citation。

---

## 4. 为什么这个问题适合测试 RAG？

这个问题适合测试 RAG，因为它不是简单关键词问答。

用户可能会用不同表达方式提问，例如：

```text
Can we host the product ourselves?
```

或者：

```text
Do you support on-premise deployment?
```

这些问题和 `private deployment` 语义接近，但关键词不一定完全一样。

如果系统能把这些问题都检索到：

```text
04_deployment_guide.md
```

说明 embedding-based semantic retrieval 起到了作用。

---

## 5. 本次运行观察

本次运行命令：

```powershell
python rag_app/main_chroma.py
```

本次观察重点如下：

| 检查项                                               | 结果  |
| ------------------------------------------------- | --- |
| 是否成功运行 `main_chroma.py`                           | 待填写 |
| 是否返回 answer                                       | 待填写 |
| 是否返回 source                                       | 待填写 |
| source 是否来自 deployment guide                      | 待填写 |
| 回答是否提到 private deployment / on-premise deployment | 待填写 |

---

## 6. 本次测试结论

本次测试用于验证系统是否能基于用户问题检索到正确的部署相关文档，并生成带来源引用的回答。

如果 source 指向：

```text
04_deployment_guide.md
```

说明系统能够根据语义匹配找到相关知识来源。

如果 source 没有指向部署文档，说明后续需要优化：

* chunk 内容
* embedding 模型
* Top-K 参数
* 文档表达方式
* retrieval 逻辑

---

## 7. 面试表达

我手动追踪过一次完整的 RAG 查询流程。

例如，当用户输入：

```text
Does the product support private deployment?
```

时，系统会先将问题转成 embedding，然后在 Chroma 向量数据库中检索最相关的 chunks。

由于这个问题和部署方式相关，理想情况下系统应该检索到：

```text
04_deployment_guide.md
```

中关于 private deployment 或 on-premise deployment 的内容。

随后，回答生成模块会基于这些 retrieved chunks 生成回答，并附带来源引用。

这个过程体现了 RAG 的核心价值：

> 不是让模型凭空回答，而是先检索企业知识库中的依据，再生成可追溯的回答。

---


# 今天的验收标准

你今天完成后，只要能说清下面这段，就算过关：

> 这个项目的知识库不是随便写的，而是模拟 B2B SaaS 售前资料，包括产品、价格、部署、安全、API、案例和异议处理。
> RAG 系统先通过 `load_documents.py` 读取这些 Markdown 文档，再通过 `chunk_documents.py` 切成 chunks。
> 当用户提出问题时，系统会把问题转成 embedding，在 Chroma 中检索相关 chunks，再基于这些 chunks 生成带来源引用的回答。
> 例如用户问是否支持 private deployment，系统理想情况下应该检索到 `04_deployment_guide.md`，然后生成有依据的回答。

---

# 一句话总结

今天的目标不是继续加功能，而是通过 `query_walkthrough.md` 手动追踪一次完整 RAG 查询流程，真正理解问题是如何从用户输入，经过 embedding、retrieval、generation，最后变成 answer + source 的。
