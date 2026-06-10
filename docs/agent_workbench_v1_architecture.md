# AI Pre-sales Agent Workbench V1 架构设计文档

> 项目名称：AI Pre-sales Agent Workbench
> 原项目基础：RAG-based AI Pre-sales Knowledge Assistant
> 当前版本：V1 架构设计草案
> 时间：2026 年 6 月
> 作者：Ran Wang

---

## 1. 文档目的

本文档用于定义 **AI Pre-sales Agent Workbench V1** 的最小可运行架构。

V1 的目标不是构建一个复杂的生产级系统，而是在现有 RAG 售前知识库助手基础上，升级出一个：

* 能运行
* 能截图
* 能解释
* 能评估
* 能被面试官追问
* 能体现 AI 应用层工程能力

的轻量级 Agent 工作流。

V1 需要证明系统不仅能基于文档回答客户问题，还能完成以下动作：

1. 理解客户问题意图
2. 规划任务执行路径
3. 选择合适工具
4. 调用 RAG 检索文档
5. 生成 source-grounded answer
6. 审查售前业务风险
7. 检查回答中的 claim 是否有来源支撑
8. 生成客户 follow-up email draft
9. 压缩客户对话记忆
10. 记录完整 Agent Trace
11. 支持基础 Agent Eval

---

## 2. V1 设计原则

V1 遵循以下原则：

1. **先可运行，再复杂化**

   * 不追求一开始就做生产级架构。
   * 先做一个能跑通、能展示、能讲清楚的 Agent workflow。

2. **复用现有 RAG 能力**

   * 不重写已有 Chroma 检索逻辑。
   * Retrieval Agent 只是把已有 RAG 能力封装成 Agent skill。

3. **避免盲目堆技术栈**

   * 暂时不引入 PostgreSQL、Redis、OpenSearch、Airflow、Docker Compose、MCP、LangGraph 等复杂组件。
   * 当前重点是应用层 Agent 设计，而不是基础设施堆叠。

4. **每个 Agent 节点都要可解释**

   * Planner 为什么这么判断？
   * Retrieval 为什么检索这些 source？
   * Risk Review 为什么认为有风险？
   * Critic 为什么认为回答不够 grounded？
   * Memory Manager 为什么保留这些信息？

5. **所有关键步骤都要可追踪**

   * 每次运行都生成 Agent Trace。
   * Trace 可用于 Debug、Eval、Streamlit 展示和面试讲解。

6. **面试价值优先**

   * 项目要能体现 AI Solutions / AI Pre-sales / LLM Application / Technical Consultant 相关岗位能力。
   * 重点展示业务场景理解、风险边界、工具调用、评估体系和可解释性。

---

## 3. V1 文件结构设计

新增一个独立的 Agent Workbench 包：

```text
agent_workbench/
    __init__.py

    agents/
        __init__.py
        planner_agent.py
        retrieval_agent.py
        risk_review_agent.py
        critic_agent.py
        email_agent.py
        memory_manager.py

    harness/
        __init__.py
        tool_registry.py
        safe_executor.py
        output_validator.py
        agent_orchestrator.py

    schemas/
        __init__.py
        agent_schemas.py

    traces/
        agent_traces.jsonl

eval/
    agent_eval_dataset.csv
    run_agent_eval.py
    agent_eval_results.csv

docs/
    agent_workbench_upgrade_plan.md
    agent_workbench_v1_architecture.md
```

---

## 4. 与现有项目的关系

Agent Workbench 不是推翻原项目，而是在原来的 RAG 售前知识库助手之上做应用层升级。

现有模块与新模块的关系如下：

| 现有能力                            | 在 Agent Workbench 中的作用     |
| ------------------------------- | -------------------------- |
| Chroma 向量库                      | 被 Retrieval Agent 调用       |
| sentence-transformers embedding | 支撑语义检索                     |
| LLM Client                      | 支撑回答生成、邮件草稿生成              |
| Guardrails                      | 升级为 Risk Review Agent 的一部分 |
| Trace Logger                    | 扩展为 Agent Trace            |
| Eval 脚本                         | 扩展为 Agent Eval Harness     |
| Streamlit Demo                  | 扩展为 Agent Workbench 展示界面   |

核心原则：

> 原来的 RAG 项目证明“能基于知识库可靠回答”，新的 Agent Workbench 证明“能围绕售前场景进行规划、审查、记忆、评估和交付”。

---

## 5. V1 运行总流程

V1 的运行流程如下：

```text
用户输入客户问题
    ↓
Memory Manager 加载记忆
    ↓
Planner Agent 判断 intent / risk / required tools
    ↓
Tool Registry 检查工具是否允许
    ↓
Safe Executor 安全执行工具
    ↓
Retrieval Agent 调用 search_docs
    ↓
生成 raw answer
    ↓
Risk Review Agent 审查售前风险
    ↓
Critic Agent 检查 claim grounding
    ↓
生成 final answer
    ↓
Email Agent 生成 follow-up email draft
    ↓
Memory Manager 压缩客户记忆
    ↓
Agent Trace Logger 写入完整运行记录
```

---

## 6. 核心数据对象：AgentRunState

V1 使用一个统一的数据对象在各模块之间传递状态。

建议命名：

```text
AgentRunState
```

它的作用是保存一次 Agent 运行中的所有关键信息。

建议字段：

```json
{
  "run_id": "",
  "user_question": "",
  "memory_loaded": {},
  "planner_output": {},
  "tools_called": [],
  "retrieved_sources": [],
  "raw_answer": "",
  "risk_decision": {},
  "critic_decision": {},
  "final_answer": "",
  "email_draft": {},
  "memory_summary": {},
  "human_review_required": false,
  "latency_ms": 0,
  "errors": []
}
```

为什么需要它：

1. 避免模块之间参数传递混乱
2. 方便写 trace
3. 方便做 eval
4. 方便 Streamlit 展示
5. 方便面试时解释系统链路
6. 方便后续升级成更复杂的 Agent graph

---

## 7. Agents 模块职责设计

---

## 7.1 Planner Agent

文件路径：

```text
agent_workbench/agents/planner_agent.py
```

### 职责

Planner Agent 负责在回答前进行任务规划。

它需要判断：

* 客户问题的 intent
* 问题风险等级
* 是否需要检索
* 需要调用哪些 tools
* 是否需要生成邮件草稿
* 是否可能需要人工复核

### V1 实现方式

V1 先使用 rule-based 规则实现，不急着上复杂 LLM planning。

原因：

1. 更稳定
2. 更容易测试
3. 更容易解释
4. 面试中能清楚说明每个 intent 判断逻辑
5. 后续可以再升级为 LLM planner

### 示例输出

```json
{
  "intent": "deployment_question",
  "risk_level": "medium",
  "required_tools": ["search_docs"],
  "requires_retrieval": true,
  "requires_email_draft": true,
  "requires_human_review": false,
  "planning_reason": "客户问题涉及部署方式，因此需要检索文档并进行风险审查。"
}
```

---

## 7.2 Retrieval Agent

文件路径：

```text
agent_workbench/agents/retrieval_agent.py
```

### 职责

Retrieval Agent 负责把现有 Chroma RAG 检索能力封装成 Agent skill。

核心 skill：

```text
search_docs(query, top_k, risk_level)
```

### V1 行为

| 风险等级   | 检索策略                     |
| ------ | ------------------------ |
| low    | 使用默认 top_k               |
| medium | 增加 top_k，提升召回            |
| high   | 增加 top_k，并要求更强 source 支撑 |

### 输出格式

```json
{
  "query": "",
  "top_k": 5,
  "sources": [
    {
      "source_file": "",
      "chunk_id": "",
      "similarity_score": 0.0,
      "content_preview": ""
    }
  ]
}
```

### 面试价值

Retrieval Agent 体现的是：

> 系统不会对所有问题使用同一种检索策略，而是根据售前风险动态调整 retrieval behavior。

---

## 7.3 Risk Review Agent

文件路径：

```text
agent_workbench/agents/risk_review_agent.py
```

### 职责

Risk Review Agent 负责识别售前场景中的高风险内容。

它需要判断：

* 用户问题本身是否高风险
* raw answer 是否包含高风险承诺
* 是否需要人工复核
* final answer 是否需要更谨慎表达

### 风险类别

V1 至少覆盖以下风险：

1. pricing commitment
2. SLA guarantee
3. HIPAA / compliance claim
4. customer case / named customer reference
5. private deployment
6. data security
7. integration promise
8. roadmap / future feature commitment
9. legal or contractual wording

### 示例输出

```json
{
  "risk_level": "high",
  "risk_categories": ["SLA", "private_deployment"],
  "requires_human_review": true,
  "safe_response_guidance": "不要承诺 SLA 或具体部署条款。应基于文档谨慎回答，并建议销售或法务复核。"
}
```

### 面试价值

Risk Review Agent 体现的是：

> AI 售前助手不能只追求回答完整，还必须知道哪些话不能随便承诺。

---

## 7.4 Critic Agent

文件路径：

```text
agent_workbench/agents/critic_agent.py
```

### 职责

Critic Agent 负责检查 final answer 中的重要 claim 是否真的被 retrieved sources 支撑。

它解决的问题是：

> 有 source citation 不等于回答真的 grounded。

### V1 检查内容

Critic Agent 至少检查：

1. 回答是否出现未被 source 支撑的产品功能
2. 回答是否做出未被 source 支撑的 SLA 承诺
3. 回答是否做出未被 source 支撑的价格承诺
4. 回答是否做出未被 source 支撑的合规承诺
5. 回答是否引用了与结论关系很弱的来源
6. 回答是否需要降级为谨慎表达
7. 回答是否需要触发人工复核

### 示例输出

```json
{
  "grounding_status": "partially_supported",
  "unsupported_claims": [
    "回答中提到 HIPAA-ready，但检索来源中没有明确支持。"
  ],
  "revision_required": true,
  "critic_note": "删除未被支持的 HIPAA claim，并改为建议客户确认合规要求。"
}
```

### 面试价值

Critic Agent 体现的是：

> 我不只是做 RAG 引用来源，而是进一步检查 claim-level grounding。

---

## 7.5 Email Agent

文件路径：

```text
agent_workbench/agents/email_agent.py
```

### 职责

Email Agent 负责根据最终回答生成客户 follow-up email draft。

输入包括：

* final answer
* retrieved sources
* risk note
* open questions
* next actions

### 边界

Email Agent 只能生成草稿，不能自动发送邮件。

### 示例输出

```json
{
  "subject": "Follow-up on your InsightFlow AI deployment questions",
  "body": "Hi, thanks for your questions about deployment..."
}
```

### 邮件草稿应包含

1. 简短感谢
2. 客户问题总结
3. 基于文档的回答
4. 风险或限制说明
5. 需要客户补充确认的问题
6. 下一步行动建议

### 面试价值

Email Agent 体现的是：

> Agent 不只停留在问答，而是能生成真实售前工作流中的交付物。

---

## 7.6 Memory Manager

文件路径：

```text
agent_workbench/agents/memory_manager.py
```

### 职责

Memory Manager 负责管理客户对话记忆。

V1 设计三层记忆：

```text
short_term_memory
session_memory
customer_profile_memory
```

### Short-term Memory

保存最近几轮对话，用于当前回答。

示例：

```json
{
  "recent_user_questions": [],
  "recent_agent_answers": [],
  "temporary_constraints": []
}
```

### Session Memory

保存当前会话中的重要事实。

示例：

```json
{
  "session_id": "session_001",
  "confirmed_requirements": [],
  "risk_concerns": [],
  "open_questions": [],
  "next_actions": []
}
```

### Customer Profile Memory

保存压缩后的客户画像。

示例：

```json
{
  "customer_name": "Unknown",
  "industry": "Unknown",
  "company_size": "Unknown",
  "use_case": "Unknown",
  "confirmed_facts": [],
  "risk_concerns": [],
  "preferred_deployment": "Unknown",
  "open_questions": [],
  "next_actions": []
}
```

### 记忆压缩原则

系统应该记住：

* 已确认的客户需求
* 部署偏好
* 集成需求
* 风险关注点
* 待确认问题
* 下一步行动

系统不应该记住：

* 未被确认的猜测
* 被 Critic Agent 判定为 unsupported 的 claim
* 与售前无关的私人信息
* 临时措辞
* 幻觉内容

---

## 8. Harness 模块职责设计

---

## 8.1 Tool Registry

文件路径：

```text
agent_workbench/harness/tool_registry.py
```

### 职责

Tool Registry 负责定义系统中允许被 Agent 调用的工具。

V1 初始工具：

```text
search_docs
review_risk
critic_check
draft_email
compress_memory
```

### 每个工具需要定义

```json
{
  "tool_name": "search_docs",
  "description": "使用 Chroma 检索产品和售前知识库文档。",
  "timeout_seconds": 10,
  "risk_level": "medium",
  "fallback_strategy": "return_empty_result_with_warning"
}
```

### 设计价值

Tool Registry 的意义是：

> Agent 不能随便调用任意函数，只能调用被注册、被允许、可追踪的工具。

---

## 8.2 Safe Executor

文件路径：

```text
agent_workbench/harness/safe_executor.py
```

### 职责

Safe Executor 负责安全执行工具。

它需要处理：

1. 工具是否存在
2. 输入是否符合 schema
3. 是否超时
4. 是否执行失败
5. 失败后如何 fallback
6. 工具调用是否被记录进 trace

### V1 边界

V1 不需要真正的重型 sandbox。

只需要一个轻量级 Safe Executor，用于：

* 限定工具调用范围
* 捕获异常
* 返回 fallback output
* 写入 tools_called 记录

---

## 8.3 Output Validator

文件路径：

```text
agent_workbench/harness/output_validator.py
```

### 职责

Output Validator 负责检查各个 Agent 输出是否符合预期结构。

需要验证：

* planner_output
* risk_decision
* critic_decision
* email_draft
* memory_summary
* final response object

如果输出无效，需要给出默认 fallback。

---

## 8.4 Agent Orchestrator

文件路径：

```text
agent_workbench/harness/agent_orchestrator.py
```

### 职责

Agent Orchestrator 是 V1 的核心调度器。

它负责：

1. 接收用户问题
2. 初始化 AgentRunState
3. 调用 Memory Manager
4. 调用 Planner Agent
5. 调用 Tool Registry / Safe Executor
6. 调用 Retrieval Agent
7. 生成 raw answer
8. 调用 Risk Review Agent
9. 调用 Critic Agent
10. 生成 final answer
11. 调用 Email Agent
12. 调用 Memory Manager 压缩记忆
13. 写入 Agent Trace
14. 返回最终结构化结果

---

## 9. Agent Trace 设计

Trace 文件路径：

```text
agent_workbench/traces/agent_traces.jsonl
```

每一次 Agent run 写入一行 JSON。

必需字段：

```json
{
  "run_id": "",
  "timestamp": "",
  "user_question": "",
  "memory_loaded": {},
  "planner_output": {},
  "tools_called": [],
  "retrieved_sources": [],
  "raw_answer": "",
  "risk_decision": {},
  "critic_decision": {},
  "final_answer": "",
  "email_draft": {},
  "memory_summary": {},
  "human_review_required": false,
  "latency_ms": 0,
  "errors": []
}
```

### Trace 的价值

Trace 可以用于：

1. Debug
2. Eval
3. Streamlit 展示
4. 飞书作品集截图
5. GitHub README 展示
6. 面试中解释 Agent 决策链路

面试表达：

> 我没有只做一个黑盒 Agent，而是记录了每一步的 planner output、tool calls、retrieved sources、risk decision、critic decision 和 final answer，因此这个系统是可解释、可追踪、可评估的。

---

## 10. Agent Eval Harness 设计

V1 新增：

```text
eval/agent_eval_dataset.csv
eval/run_agent_eval.py
eval/agent_eval_results.csv
```

### Eval Dataset 字段

```text
case_id
user_question
expected_intent
expected_tools
expected_risk_level
expected_refusal
expected_source_keywords
expected_email_points
expected_memory_points
```

### V1 建议测试用例

1. 普通产品功能问题
2. pricing 问题
3. SLA 问题
4. private deployment 问题
5. HIPAA / compliance 问题
6. customer case 问题
7. integration 问题
8. unsupported roadmap 问题
9. 多轮 memory 问题
10. email draft completeness 问题

### Eval 指标

| 指标                           | 说明                        |
| ---------------------------- | ------------------------- |
| intent_accuracy              | Planner 是否正确识别 intent     |
| tool_selection_accuracy      | 是否选择了正确 tools             |
| source_hit_rate              | 检索结果是否命中预期 source keyword |
| refusal_accuracy             | 高风险问题是否正确拒绝或降级表达          |
| risk_classification_accuracy | 风险等级是否正确                  |
| email_draft_completeness     | 邮件草稿是否覆盖关键点               |
| memory_retention_accuracy    | 记忆压缩是否保留重要事实              |

---

## 11. Streamlit V1 展示设计

V1 不需要重做前端，只需要在现有 Streamlit Demo 中增加 Agent Workbench 展示区。

建议展示模块：

1. Customer Question 输入框
2. Final Answer 展示区
3. Retrieved Sources 展示区
4. Planner Output 展示区
5. Risk Review Panel
6. Critic Panel
7. Email Draft Panel
8. Memory Summary Panel
9. Agent Trace Preview

### 截图价值

这些模块可以作为飞书作品集截图，证明项目不是普通 RAG，而是完整 Agent workflow。

---

## 12. V1 开发顺序

推荐开发顺序：

1. 创建 Agent Workbench 文件夹结构
2. 创建 schemas 和 AgentRunState
3. 实现 Planner Agent
4. 实现 Tool Registry
5. 实现 Safe Executor
6. 实现 Retrieval Agent wrapper
7. 实现 Risk Review Agent
8. 实现 Critic Agent
9. 实现 Email Agent
10. 实现 Memory Manager
11. 实现 Agent Orchestrator
12. 实现 Agent Trace 写入
13. 增加 CLI smoke test
14. 增加 agent_eval_dataset.csv
15. 增加 run_agent_eval.py
16. 增加 Streamlit Agent Workbench panel
17. 更新 README
18. 更新飞书 Case Study
19. 更新简历 bullet
20. 准备面试讲解稿

---

## 13. V1 成功标准

V1 成功的最低标准是：

运行：

```cmd
python -m agent_workbench.harness.agent_orchestrator
```

能够输出：

* planner result
* retrieved sources
* risk decision
* critic decision
* final answer
* email draft
* memory summary
* trace record

同时运行：

```cmd
python eval\run_agent_eval.py
```

能够生成：

```text
eval/agent_eval_results.csv
```

并且至少包含以下结果：

* intent 是否正确
* tool selection 是否正确
* source hit 是否正确
* risk classification 是否正确
* refusal / safe answer 是否正确
* email draft 是否完整
* memory retention 是否正确

---

## 14. V1 面试讲解口径

### 中文版

V1 的目标不是堆复杂基础设施，而是把原来的可靠 RAG 助手升级成一个轻量但完整的售前 Agent 工作流。

这个系统可以完成：

* 任务规划
* 工具选择
* 文档检索
* 风险审查
* grounding 检查
* 客户邮件草稿生成
* 记忆压缩
* trace 记录
* agent eval

因此它比普通 RAG Demo 更接近真实 AI Solutions / AI Pre-sales 工作场景。

### 英文简短版

V1 upgrades a reliable RAG assistant into a lightweight AI pre-sales agent workflow. It plans the task, selects tools, retrieves documents, reviews risk, checks grounding, drafts follow-up emails, compresses memory, and records traces for evaluation.

---

## 15. 一句话项目定位

中文：

> 我把原来的 RAG 售前知识库助手升级成了一个 AI Pre-sales Agent Workbench。它不只是回答客户问题，而是能够规划任务、调用工具、检索来源、审查风险、检查 grounding、生成邮件草稿、压缩客户记忆，并通过 Agent Eval 评估整个工作流。

英文：

> I upgraded a RAG-based pre-sales knowledge assistant into an AI Pre-sales Agent Workbench that supports planning, tool use, retrieval, risk review, grounding checks, email drafting, memory compression, tracing, and agent evaluation.
