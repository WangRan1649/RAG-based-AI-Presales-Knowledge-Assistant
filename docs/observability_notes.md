# Observability Notes 中文版：AI Pre-sales Copilot 的轻量 Tracing 设计

## 1. 为什么需要 Observability

AI Pre-sales Copilot 不只是一个“能回答问题”的 RAG Demo。
它更像一个小型但真实的 LLM 应用系统：每一次回答都应该是可追踪、可调试、可复盘、可改进的。

在 RAG 系统里，一个回答效果不好，可能不是单一原因造成的，而可能来自多个环节：

* 用户问题本身不清楚
* 检索阶段没有找到正确文档
* 相似度分数太低
* Prompt 约束不够明确
* LLM 生成了没有依据的内容
* 最终回答需要人工审核后才能发给客户

所以这个项目加入了轻量级 tracing 和 feedback logging。
它不是一开始就接复杂平台，而是先用本地 JSONL / CSV 记录关键链路，方便理解和调试。

---

## 2. Tracing 模块做了什么

项目中新增了一个自建 tracing 模块：

```text
rag_app/trace_logger.py
```

它会把每次问答的链路记录到：

```text
logs/query_logs.jsonl
```

同时也支持用户反馈记录：

```text
logs/user_feedback.csv
```

这些日志文件属于运行时数据，可能包含用户问题、生成回答、客户相关内容，所以不会提交到 GitHub。
项目通过 `.gitignore` 忽略了这些日志文件。

---

## 3. Query Log 记录哪些字段

每一次 query event 会记录以下字段：

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

### 字段解释

| 字段                | 含义                                                         |
| ----------------- | ---------------------------------------------------------- |
| timestamp         | 本次问题处理的时间                                                  |
| user_query        | 用户输入的原始问题                                                  |
| retrieved_sources | RAG 检索到的来源文档                                               |
| top_k_chunks      | Top-K 检索结果，包括 rank、chunk_id、chunk_index 和 similarity_score |
| similarity_scores | 每个 chunk 的相似度分数                                            |
| prompt_version    | 当前使用的 prompt 版本                                            |
| llm_mode          | 当前使用 mock、api，还是 rule_based_refusal                        |
| answer            | 生成回答的预览内容                                                  |
| confidence        | 当前回答的置信度                                                   |
| latency_ms        | 本次问答总耗时，单位是毫秒                                              |
| error_message     | 错误信息或拒答原因                                                  |

---

## 4. 为什么使用 JSONL

项目使用 JSONL 记录 query logs，原因是：

* 适合追加写入
* 每一行就是一条完整日志
* 可以直接用文本方式查看
* 后续可以用 Python / pandas 分析
* 比数据库或外部 tracing 平台更轻量

对于求职作品集来说，JSONL 足够清晰，也方便面试时解释。

---

## 5. Tracing 如何帮助调试 RAG

Tracing 的价值不是“多存一些日志”，而是帮助回答这些关键问题。

### 1. 检索有没有命中正确来源？

通过查看：

```text
retrieved_sources
top_k_chunks
```

可以判断系统是否检索到了正确的 FAQ、部署文档、安全文档、定价文档、集成文档或客户案例。

如果回答不准确，可以先看是不是检索阶段就错了。

---

### 2. 相似度分数是否足够高？

通过查看：

```text
similarity_scores
```

可以判断当前回答是否有足够强的文档依据。

如果相似度太低，就应该触发低置信度拒答，而不是强行生成回答。

---

### 3. 当前回答来自哪种模式？

通过查看：

```text
llm_mode
```

可以知道回答来自：

```text
mock
api
rule_based_refusal
```

其中：

* `mock`：本地模拟模式，不消耗 API
* `api`：真实 LLM API 模式
* `rule_based_refusal`：规则拒答模式

这有助于区分问题到底出在模型生成，还是出在拒答规则。

---

### 4. 系统有没有正确拒答？

当问题超出知识库范围时，比如：

```text
Can InsightFlow AI guarantee stock trading profits?
```

系统应该拒答，并记录：

```text
llm_mode = rule_based_refusal
error_message = 拒答原因
```

这样可以验证 hallucination control 是否真的生效。

---

### 5. 每次问答耗时多久？

通过：

```text
latency_ms
```

可以看到一次问答从检索到生成的整体耗时。

后续如果接入 Streamlit 或 FastAPI，这个字段可以帮助判断：

* 检索是否太慢
* LLM API 是否太慢
* 是否需要缓存
* 是否需要优化 embedding / vector store

---

## 6. 用户反馈日志

项目还支持用户反馈记录：

```text
logs/user_feedback.csv
```

它包含：

```text
timestamp
user_query
feedback
comment
answer_preview
```

未来在 Streamlit 页面里，可以加入：

```text
thumbs_up
thumbs_down
needs_review
```

这些反馈可以用于改进：

* eval dataset
* prompt 设计
* 检索质量
* 拒答阈值
* 知识库覆盖范围

---

## 7. Tracing 和 RAG Evaluation 的关系

Tracing 和 Evaluation 不是一回事，它们分别解决不同问题。

| 模块             | 作用                              |
| -------------- | ------------------------------- |
| RAG Evaluation | 用固定测试集评估检索命中率、来源准确性、关键词覆盖率和拒答表现 |
| Query Tracing  | 记录每一次真实问答的运行链路                  |
| User Feedback  | 收集人类对回答质量的反馈                    |

它们组合起来形成一个轻量质量闭环：

```text
用户提问
→ RAG 检索
→ LLM 生成或拒答
→ 记录 query trace
→ 收集用户反馈
→ 优化知识库 / prompt / 阈值
→ 重新运行 evaluation
```

---

## 8. 为什么没有一开始就用 LangSmith

这个项目没有一开始就接 LangSmith 或复杂 tracing 平台，而是先做了手写轻量 tracing。

原因是：
项目当前的目标是先理解完整 RAG 应用链路，而不是一开始就依赖框架。

这个项目希望先手写并理解：

```text
retrieval
prompt construction
LLM call
source grounding
confidence
refusal logic
logging
evaluation
```

等底层流程清楚之后，后续可以再把 LangSmith / LangChain / OpenTelemetry 作为可选对照版本接入。

这样面试时可以体现两点：

* 我理解 RAG 的底层流程
* 我也知道真实 AI 应用需要 observability 和 debugging

---

## 9. 面试表达

英文表达：

> I added lightweight observability to the RAG pipeline by logging each query, retrieved sources, top-k chunks, similarity scores, prompt version, LLM mode, answer preview, confidence, latency, and error message. This helps debug retrieval failures, inspect hallucination risks, and improve the system through evaluation and user feedback.

中文表达：

> 我给 RAG 项目加了轻量 tracing。每次问答都会记录用户问题、检索到的来源、Top-K chunks、相似度、prompt 版本、LLM 模式、回答预览、置信度、耗时和错误信息。这样如果回答不好，我可以判断问题出在检索、prompt、LLM 生成，还是知识库本身，而不是只看最终答案。

更简洁的中文面试版：

> 我不只是做了一个能回答问题的 RAG Demo，还加入了轻量可观测性。系统会记录每次问答的检索来源、相似度、LLM 模式、置信度、耗时和错误信息，用来排查检索失败、幻觉风险和回答质量问题。

---

## 10. 这部分在项目中的价值

这部分可以对应简历或作品集里的能力点：

```text
Lightweight Observability
Query Tracing
RAG Debugging
Human Feedback Loop
Hallucination Risk Inspection
```

中文理解：

```text
轻量可观测性
问答链路追踪
RAG 调试能力
用户反馈闭环
幻觉风险检查
```

这能说明项目不只是“调用模型”，而是具备 AI 应用工程思维。





# Observability Notes: Lightweight Tracing for AI Pre-sales Copilot

## 1. Why Observability Matters

AI Pre-sales Copilot is not only a question-answering demo.
It is designed as a small but realistic LLM application workflow where each answer should be traceable, debuggable, and reviewable.

In a RAG-based system, a wrong answer may come from different failure points:

* The user question may be ambiguous.
* The retrieval step may return irrelevant chunks.
* The similarity scores may be too low.
* The prompt may not clearly constrain the model.
* The LLM may produce unsupported claims.
* The final answer may need human review before being sent to a customer.

Because of this, the project adds lightweight tracing and feedback logging before introducing heavier observability platforms.

---

## 2. What the Tracing Module Does

The project includes a custom tracing module:

```text
rag_app/trace_logger.py
```

It writes query-level logs to:

```text
logs/query_logs.jsonl
```

It also supports user feedback logging to:

```text
logs/user_feedback.csv
```

These runtime log files are ignored by Git because they may contain user questions, generated answers, or customer-related information.

---

## 3. Query Log Fields

Each query event records the following fields:

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

### Field Explanation

| Field             | Meaning                                                                 |
| ----------------- | ----------------------------------------------------------------------- |
| timestamp         | When the query was processed                                            |
| user_query        | The original customer or pre-sales question                             |
| retrieved_sources | Source files retrieved from the knowledge base                          |
| top_k_chunks      | Retrieved chunk metadata including rank, chunk_id, and similarity score |
| similarity_scores | Similarity scores from semantic retrieval                               |
| prompt_version    | The prompt template version used for answer generation                  |
| llm_mode          | Whether the system used mock mode, API mode, or rule-based refusal      |
| answer            | A preview of the generated answer                                       |
| confidence        | The confidence level used by the system                                 |
| latency_ms        | End-to-end processing time in milliseconds                              |
| error_message     | Any refusal reason or runtime error message                             |

---

## 4. Why JSONL Is Used

The project uses JSONL for query logs because it is:

* Append-friendly
* Easy to inspect line by line
* Simple to process later with Python or pandas
* Suitable for lightweight local debugging

For a portfolio project, JSONL is easier to understand and maintain than a full observability platform.

---

## 5. How Tracing Supports Debugging

Tracing helps answer important debugging questions:

### 1. Did retrieval return the right sources?

By checking `retrieved_sources` and `top_k_chunks`, we can see whether the system retrieved the expected product document, deployment guide, security document, FAQ, or pricing note.

### 2. Were the similarity scores strong enough?

The `similarity_scores` field helps determine whether the answer was supported by strong evidence or whether the system should refuse to answer.

### 3. Which mode generated the answer?

The `llm_mode` field shows whether the answer came from:

```text
mock
api
rule_based_refusal
```

This is useful because mock mode is used for local development, while API mode is used for real LLM calls.

### 4. Did the system refuse safely?

If the question is outside the product pre-sales scope, the system records:

```text
llm_mode = rule_based_refusal
error_message = refusal reason
```

This helps evaluate hallucination control behavior.

### 5. How long did the query take?

The `latency_ms` field records the total processing time, which is useful for later Streamlit, FastAPI, and production-style optimization.

---

## 6. User Feedback Logging

The project also includes a feedback log:

```text
logs/user_feedback.csv
```

It supports records such as:

```text
timestamp
user_query
feedback
comment
answer_preview
```

This allows future UI features such as thumbs up / thumbs down feedback.

Example feedback values:

```text
thumbs_up
thumbs_down
needs_review
```

This feedback can later be used to improve:

* Evaluation datasets
* Prompt design
* Retrieval quality
* Refusal thresholds
* Knowledge base coverage

---

## 7. Relationship with RAG Evaluation

The tracing module and evaluation pipeline serve different purposes.

| Component      | Purpose                                                                                                  |
| -------------- | -------------------------------------------------------------------------------------------------------- |
| RAG Evaluation | Measures retrieval hit rate, source accuracy, keyword coverage, and refusal behavior on a fixed test set |
| Query Tracing  | Records what happened during each actual query                                                           |
| User Feedback  | Captures human judgment after seeing an answer                                                           |

Together, they form a lightweight quality loop:

```text
Run query
→ Retrieve sources
→ Generate or refuse answer
→ Log trace
→ Collect feedback
→ Improve knowledge base / prompt / thresholds
→ Re-run evaluation
```

---

## 8. Why This Is Not LangSmith Yet

This project intentionally starts with a lightweight custom tracing module instead of immediately adopting LangSmith or another external tracing platform.

The reason is that the first goal is to understand the full RAG workflow manually:

```text
retrieval
prompt construction
LLM call
source grounding
confidence
refusal logic
logging
evaluation
```

After this manual pipeline is clear, the project can later add LangSmith or OpenTelemetry as an optional comparison.

This allows the project to demonstrate both:

* Understanding of the underlying RAG architecture
* Awareness of professional observability practices

---

## 9. Interview Explanation

A concise interview explanation:

> I added lightweight observability to the RAG pipeline by logging each query, retrieved sources, top-k chunks, similarity scores, prompt version, LLM mode, answer preview, confidence, latency, and error message. This helps debug retrieval failures, inspect hallucination risks, and improve the system through evaluation and user feedback.

Chinese explanation:

> 我给 RAG 项目加了轻量 tracing。每次问答都会记录用户问题、检索到的来源、Top-K chunks、相似度、prompt 版本、LLM 模式、回答预览、置信度、耗时和错误信息。这样如果回答不好，我可以判断问题出在检索、prompt、LLM 生成，还是知识库本身，而不是只看最终答案。
