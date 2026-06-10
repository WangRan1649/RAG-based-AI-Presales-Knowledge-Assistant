# AI Pre-sales Agent Workbench 升级计划

> 项目名称：RAG-based AI Pre-sales Knowledge Assistant
> 升级目标：AI Pre-sales Agent Workbench
> 中文名称：基于 RAG + Multi-Agent Harness 的 B2B SaaS 售前智能工作台
> 当前版本：V2 升级规划文档
> 时间：2026 年 6 月
> 作者：Ran Wang

---

## 1. 项目新定位

### 1.1 原项目定位

原项目是一个面向 B2B SaaS 售前场景的 RAG 知识库助手。

它已经完成了以下能力：

* 使用 Chroma 进行向量检索
* 使用 sentence-transformers 生成 embedding
* 基于 retrieved sources 生成回答
* 支持 source-grounded answer
* 支持 Retrieval Evaluation
* 支持 Answer Evaluation
* 支持 Guardrails
* 支持 Trace Logging
* 支持 Streamlit Demo 展示

这一版本证明了系统可以基于产品文档回答客户问题，并通过检索、引用来源和评估机制降低幻觉风险。

### 1.2 新项目定位

升级后的项目定位为：

**AI Pre-sales Agent Workbench｜基于 RAG + Multi-Agent Harness 的 B2B SaaS 售前智能工作台**

本次升级的目标不是盲目堆技术栈，而是把项目从一个“可靠 RAG Demo”升级为一个：

* 可运行
* 可解释
* 可追踪
* 可评估
* 可截图展示
* 可被面试官深入追问

的 AI 应用层 Agent 项目。

升级后的系统不仅要能回答问题，还要展示：

* 如何理解客户问题意图
* 如何判断问题风险等级
* 如何选择工具
* 如何调用 RAG 检索
* 如何审查 pricing、SLA、HIPAA、deployment 等售前风险
* 如何检查回答中的 claim 是否真的被 source 支撑
* 如何生成客户 follow-up email draft
* 如何压缩客户对话记忆
* 如何记录完整 Agent Trace
* 如何对 Agent workflow 做评估

### 1.3 面试价值

该项目服务于以下目标岗位：

* AI Solutions Intern
* AI Pre-sales Intern
* LLM Application Intern
* Technical Consultant Intern
* AI 应用层相关岗位

项目核心面试表达：

> 我不是只做了一个普通 RAG 问答助手，而是把它升级成了一个面向 B2B SaaS 售前场景的 AI Agent 工作台。系统可以完成任务规划、工具调用、文档检索、风险审查、grounding 检查、邮件草稿生成、客户记忆压缩和 Agent Eval，更接近真实 AI Solutions / AI Pre-sales 工作流。

---

## 2. Agent Workflow 总流程

### 2.1 高层流程

升级后的 Agent workflow 如下：

```text
用户输入客户问题
    ↓
加载客户记忆
    ↓
Planner Agent 进行任务规划
    ↓
Tool Registry 检查工具权限
    ↓
Safe Executor 安全执行工具
    ↓
Retrieval Agent 调用 RAG 检索
    ↓
生成 Raw Answer
    ↓
Risk Review Agent 审查售前风险
    ↓
Critic Agent 检查 claim grounding
    ↓
生成 Final Answer
    ↓
Email Agent 生成客户跟进邮件草稿
    ↓
Memory Manager 压缩客户记忆
    ↓
Agent Trace Logger 记录完整执行链路
    ↓
必要时触发 Human Review
```

### 2.2 详细流程说明

1. 用户输入一个客户售前问题。
2. Memory Manager 加载当前会话记忆和客户画像记忆。
3. Planner Agent 判断：

   * 客户问题 intent
   * 风险等级 risk level
   * 是否需要检索
   * 需要调用哪些 tools
   * 是否需要生成 email draft
   * 是否需要人工复核
4. Tool Registry 检查 Planner 选择的工具是否已注册、是否允许调用。
5. Safe Executor 负责安全执行工具，包括 schema 检查、异常捕获、timeout 和 fallback。
6. Retrieval Agent 调用现有 Chroma RAG 检索相关文档。
7. 系统基于 retrieved sources 生成 raw answer。
8. Risk Review Agent 检查问题和回答中是否包含售前高风险内容。
9. Critic Agent 检查回答中的关键 claim 是否被 retrieved sources 支撑。
10. 系统生成 final answer，包括必要的风险提示和谨慎表达。
11. Email Agent 生成客户 follow-up email draft。
12. Memory Manager 将多轮对话压缩为结构化客户记忆。
13. Trace Logger 记录完整运行过程。
14. 如果涉及 pricing、SLA、HIPAA、legal、customer case 等高风险内容，则触发 Human Review。

---

## 3. Agents 分工设计

## 3.1 Planner Agent

### 职责

Planner Agent 是整个 Agent workflow 的第一个决策节点。

它负责在正式回答前判断：

* 客户问题是什么类型
* 风险等级是多少
* 是否需要检索文档
* 需要调用哪些工具
* 是否需要生成邮件草稿
* 是否需要人工复核

### 输入

* 用户问题
* short-term memory
* session memory
* customer profile memory

### 输出示例

```json
{
  "intent": "deployment_question",
  "risk_level": "medium",
  "required_tools": ["search_docs", "review_risk", "critic_check"],
  "requires_retrieval": true,
  "requires_email_draft": true,
  "requires_human_review": false,
  "planning_reason": "客户问题涉及部署方式，因此需要检索相关文档，并进行风险审查和 grounding 检查。"
}
```

### 面试表达

> Planner Agent 体现了系统不是简单 chatbot，而是在回答前先进行任务规划和风险判断。

---

## 3.2 Retrieval Agent

### 职责

Retrieval Agent 负责复用现有 Chroma RAG 能力，并将其封装为 Agent skill。

核心 skill：

```text
search_docs(query, top_k, risk_level)
```

### 行为设计

低风险问题：

* 使用默认 top_k
* 正常检索产品文档

中风险问题：

* 增加 top_k
* 优先检索 deployment、security、integration、SLA 相关文档

高风险问题：

* 增加 top_k
* 加强 evidence requirement
* 必要时进行 query rewrite
* 如果证据不足，要求人工复核

### 输出示例

```json
{
  "query": "private deployment SLA",
  "top_k": 6,
  "sources": [
    {
      "source_file": "04_deployment_guide.md",
      "chunk_id": "chunk_001",
      "similarity_score": 0.87,
      "content_preview": "InsightFlow AI supports cloud deployment and selected private deployment scenarios..."
    }
  ]
}
```

### 面试表达

> Retrieval Agent 体现了系统不会对所有问题使用同一种检索策略，而是会根据售前风险动态调整 retrieval behavior。

---

## 3.3 Risk Review Agent

### 职责

Risk Review Agent 负责识别售前场景中的高风险内容。

它需要判断：

* 用户问题是否高风险
* raw answer 是否包含高风险承诺
* final answer 是否需要谨慎表达
* 是否需要人工复核

### 风险类别

V1 至少覆盖以下风险：

* pricing commitment
* SLA guarantee
* HIPAA / compliance claim
* customer case / named customer reference
* private deployment
* data security
* integration promise
* roadmap / future feature commitment
* legal or contractual wording

### 输出示例

```json
{
  "risk_level": "high",
  "risk_categories": ["SLA", "private_deployment"],
  "requires_human_review": true,
  "safe_response_guidance": "不要承诺 SLA 或具体私有化部署条款。应基于文档谨慎回答，并建议销售、交付或法务团队复核。"
}
```

### 面试表达

> Risk Review Agent 体现了 AI 售前助手不能只追求回答完整，还必须知道哪些话不能随便承诺。

---

## 3.4 Critic Agent

### 职责

Critic Agent 负责检查 final answer 中的重要 claim 是否真的被 retrieved sources 支撑。

它解决的问题是：

> 有 source citation 不等于回答真的 grounded。

### 检查内容

Critic Agent 至少需要检查：

* 回答是否出现未被 source 支撑的产品功能
* 回答是否做出未被 source 支撑的 pricing 承诺
* 回答是否做出未被 source 支撑的 SLA 承诺
* 回答是否做出未被 source 支撑的 HIPAA / compliance 承诺
* 回答是否引用了和结论关系很弱的来源
* 是否需要删除 unsupported claims
* 是否需要触发人工复核

### 输出示例

```json
{
  "grounding_status": "partially_supported",
  "unsupported_claims": [
    "回答中提到 HIPAA-ready，但 retrieved sources 中没有明确支持。"
  ],
  "revision_required": true,
  "critic_note": "删除未被支持的 HIPAA claim，并改为建议客户确认合规需求。"
}
```

### 面试表达

> Critic Agent 体现了我不只是做 RAG 引用来源，而是进一步做 claim-level grounding check。

---

## 3.5 Email Agent

### 职责

Email Agent 负责根据最终回答生成客户 follow-up email draft。

输入包括：

* final answer
* retrieved sources
* risk decision
* open questions
* next actions

### 边界

Email Agent 只能生成草稿，不能自动发送邮件。

### 输出示例

```json
{
  "subject": "Follow-up on your InsightFlow AI deployment questions",
  "body": "Hi, thanks for your questions about deployment options..."
}
```

### 邮件草稿应包含

* 简短感谢
* 客户问题总结
* 基于文档的回答
* 风险或限制说明
* 需要客户补充确认的问题
* 下一步行动建议

### 面试表达

> Email Agent 体现了这个系统不只停留在问答，而是能生成真实售前工作流中的交付物。

---

## 3.6 Memory Manager

### 职责

Memory Manager 负责管理和压缩客户对话记忆。

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
  "use_case": "Customer segmentation and pre-sales analytics",
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
* 重要业务约束
* 待确认问题
* 下一步行动

系统不应该记住：

* 未被确认的猜测
* 被 Critic Agent 判定为 unsupported 的 claim
* 与售前无关的私人信息
* 临时措辞
* 幻觉内容

---

## 4. Tools / Skills 设计

## 4.1 Tool Registry

Tool Registry 负责定义 Agent 可以调用哪些工具。

V1 初始工具如下：

| Tool Name       | 用途                         |   风险等级 | 阶段 |
| --------------- | -------------------------- | -----: | -- |
| search_docs     | 使用 Chroma RAG 检索产品和售前知识库文档 | Medium | V1 |
| generate_answer | 基于 retrieved sources 生成回答  | Medium | V1 |
| review_risk     | 审查业务和合规风险                  |   High | V1 |
| critic_check    | 检查回答是否 grounded            |   High | V1 |
| draft_email     | 生成客户 follow-up email draft | Medium | V1 |
| compress_memory | 压缩多轮客户对话记忆                 | Medium | V1 |

### Tool Schema 示例

每个工具需要定义：

```json
{
  "tool_name": "search_docs",
  "description": "使用 Chroma 检索产品和售前知识库文档。",
  "input_schema": {},
  "output_schema": {},
  "timeout_seconds": 10,
  "fallback_strategy": "return_empty_sources_with_warning"
}
```

### 设计原则

> Agent 不应该直接调用任意函数，而是只能通过 Tool Registry 调用已注册、可控、可追踪的工具。

---

## 4.2 Safe Executor

Safe Executor 负责安全执行工具。

它需要处理：

* 工具是否存在
* 工具是否启用
* 输入是否符合 schema
* 是否超时
* 是否执行失败
* 失败后如何 fallback
* 工具调用结果如何写入 trace

### V1 边界

V1 不需要重型 sandbox。

V1 只需要一个 lightweight safe executor，用于：

* 限定工具调用范围
* 捕获异常
* 返回 fallback output
* 记录 tools_called

### 面试表达

> 我没有让 Agent 直接调用任意函数，而是通过 Tool Registry 和 Safe Executor 控制工具边界，从而提高系统的可解释性和稳定性。

---

## 5. Memory Compression 设计

## 5.1 目标

Memory compression 的目标是把长对话压缩成结构化、可复用的客户记忆。

它不是保存所有聊天内容，而是保留对售前工作有价值的信息。

## 5.2 压缩输出结构

```json
{
  "customer_profile": {
    "customer_name": "Unknown",
    "industry": "Unknown",
    "company_size": "Unknown",
    "use_case": "Unknown"
  },
  "confirmed_facts": [],
  "risk_concerns": [],
  "open_questions": [],
  "next_actions": [],
  "summary": "客户正在评估 InsightFlow AI，并重点关注部署方式、SLA、系统集成和安全边界。"
}
```

## 5.3 应该保留的信息

系统应该保留：

* 客户已确认的需求
* 客户行业和 use case
* 部署偏好
* 系统集成需求
* 风险关注点
* 待确认问题
* 下一步行动

## 5.4 不应该保留的信息

系统不应该保留：

* 未确认假设
* 幻觉内容
* unsupported claims
* 与售前无关的私人信息
* 被 Critic Agent 判定为不可信的信息

## 5.5 人工复核规则

如果压缩后的 memory 中包含高风险业务假设，例如 pricing、SLA、HIPAA、legal、customer case 等内容，应标记为：

```json
{
  "requires_human_review": true
}
```

---

## 6. Agent Harness 设计

## 6.1 目标

Agent Harness 负责控制完整 Agent workflow。

它让系统变得：

* 模块化
* 可追踪
* 可测试
* 更安全
* 更容易解释
* 更容易被面试官理解

## 6.2 核心模块

V1 建议文件结构：

```text
agent_workbench/
    agents/
        planner_agent.py
        retrieval_agent.py
        risk_review_agent.py
        critic_agent.py
        email_agent.py
        memory_manager.py

    harness/
        tool_registry.py
        safe_executor.py
        output_validator.py
        agent_orchestrator.py

    schemas/
        agent_schemas.py

    traces/
        agent_traces.jsonl
```

## 6.3 Harness 职责

Agent Harness 需要完成：

1. 接收用户问题
2. 初始化 AgentRunState
3. 调用 Memory Manager
4. 调用 Planner Agent
5. 校验 planner output
6. 通过 Safe Executor 执行工具
7. 调用 Retrieval Agent
8. 生成 raw answer
9. 调用 Risk Review Agent
10. 调用 Critic Agent
11. 生成 final answer
12. 调用 Email Agent
13. 调用 Memory Manager 压缩记忆
14. 写入 Agent Trace
15. 返回结构化结果

## 6.4 Fallback 策略

| 失败情况                  | Fallback               |
| --------------------- | ---------------------- |
| Planner 输出无效          | 使用默认 safe plan         |
| Retrieval 失败          | 返回 evidence 不足提示       |
| Risk Review 失败        | 默认 medium risk，并要求人工复核 |
| Critic 失败             | 标记 grounding uncertain |
| Email Draft 失败        | 只返回 final answer       |
| Memory Compression 失败 | 保留 short-term memory   |

---

## 7. Agent Eval Harness 设计

## 7.1 目标

Agent Eval Harness 用于评估整个 Agent workflow 是否按预期工作。

它不只评估答案质量，还评估：

* intent 是否正确
* tool selection 是否正确
* risk classification 是否正确
* retrieval 是否命中 source
* 高风险问题是否拒绝或降级表达
* email draft 是否完整
* memory 是否保留重要信息

## 7.2 Dataset 文件

新增文件：

```text
eval/agent_eval_dataset.csv
```

建议字段：

| 字段                       | 含义          |
| ------------------------ | ----------- |
| case_id                  | 测试用例 ID     |
| user_question            | 客户问题        |
| expected_intent          | 预期 intent   |
| expected_tools           | 预期工具        |
| expected_risk_level      | 预期风险等级      |
| expected_refusal         | 是否预期拒绝或谨慎回答 |
| expected_source_keywords | 预期检索命中的关键词  |
| expected_email_points    | 邮件草稿应包含的要点  |
| expected_memory_points   | 记忆压缩应保留的要点  |

## 7.3 V1 指标

| 指标                           | 含义                          |
| ---------------------------- | --------------------------- |
| intent_accuracy              | Planner 是否识别正确 intent       |
| tool_selection_accuracy      | 是否选择正确 tools                |
| source_hit_rate              | retrieved sources 是否包含预期关键词 |
| refusal_accuracy             | 高风险 unsupported 问题是否正确拒绝或降级 |
| risk_classification_accuracy | 风险等级是否正确                    |
| email_draft_completeness     | 邮件草稿是否覆盖关键点                 |
| memory_retention_accuracy    | 记忆是否保留重要事实                  |

## 7.4 Eval 输出文件

新增文件：

```text
eval/agent_eval_results.csv
```

建议字段：

```text
case_id,
intent_pass,
tool_selection_pass,
source_hit_pass,
refusal_pass,
risk_classification_pass,
email_draft_pass,
memory_retention_pass,
overall_pass,
notes
```

---

## 8. Agent Trace 字段设计

Trace 文件：

```text
agent_workbench/traces/agent_traces.jsonl
```

每一行代表一次完整 Agent run。

## 8.1 必需字段

```json
{
  "run_id": "run_202606_xxx",
  "timestamp": "2026-06-xxTxx:xx:xx",
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

## 8.2 Trace 的价值

Trace 可以展示：

* Agent 如何做决策
* Planner 判断了什么
* 调用了哪些工具
* 检索到了哪些 sources
* 是否发现风险
* Critic 是否发现 unsupported claims
* 是否需要人工复核
* 整个 workflow 耗时多少

Trace 可用于：

* Debug
* Streamlit Demo
* GitHub README
* 飞书 Case Study
* 面试讲解
* Agent Eval

---

## 9. Human Review 边界

## 9.1 必须人工复核的情况

以下情况需要 human review：

* 回答涉及 pricing commitment
* 回答涉及 SLA guarantee
* 回答涉及 HIPAA / legal compliance
* 回答引用 named customer case
* 回答涉及 private deployment 承诺
* 回答涉及 contract / legal wording
* retrieved evidence 不足
* Critic Agent 发现 unsupported claims
* 客户要求明确保证、承诺、报价或合同条款
* memory compression 中包含高风险假设

## 9.2 通常不需要人工复核的情况

以下情况通常不需要 human review：

* 解释一般产品功能
* 总结已检索到的文档内容
* 提出澄清问题
* 对 unsupported claim 做谨慎拒绝
* 邮件草稿只总结已确认信息

## 9.3 系统能力边界

系统可以：

* 基于 source-grounded 信息回答
* 提出澄清问题
* 生成安全的 follow-up email draft
* 标记风险
* 建议人工复核
* 记录 trace
* 进行 Agent Eval

系统不能：

* 签合同
* 承诺价格
* 保证 SLA
* 在没有来源时确认 HIPAA / compliance
* 自动发送邮件
* 编造客户案例
* 将 unsupported claims 存为 confirmed facts

---

## 10. V1 / V2 开发路线

## 10.1 V1 目标

V1 目标：

> 基于现有 RAG 项目，构建一个可运行的单会话 Agent Workbench workflow。

V1 应包含：

1. Planner Agent
2. Retrieval Agent
3. Risk Review Agent
4. Critic Agent
5. Email Agent
6. Memory Manager 基础版
7. Tool Registry
8. Safe Executor
9. Output Validator
10. Agent Orchestrator
11. Agent Trace JSONL
12. 小规模 Agent Eval Dataset
13. Agent Eval Runner
14. Streamlit 基础展示区

V1 不做：

* PostgreSQL
* Redis
* OpenSearch
* Airflow
* Docker Compose
* MCP server
* LangGraph
* 复杂前端重构

## 10.2 V2 目标

V2 目标：

> 提升系统可靠性、评估深度和 demo 展示效果。

V2 可升级：

1. 更强的 query rewrite
2. 更细粒度的 claim-level critic
3. 更完整的 memory compression
4. 更丰富的 agent eval dataset
5. 更好的 Streamlit trace viewer
6. 可下载 email draft
7. customer profile panel
8. 更完整的 architecture diagram
9. 更漂亮的飞书 Case Study 截图
10. 更完善的 README 和面试材料

## 10.3 最终作品集交付物

最终项目应包含：

* GitHub README
* 架构设计文档
* Agent workflow diagram
* Streamlit demo 截图
* Agent trace 示例
* Agent Eval report
* 飞书 Case Study
* 简历 bullet
* 面试讲解稿

---

## 11. 一句话项目定位

中文：

> 我把原来的 RAG 售前知识库助手升级成了一个 AI Pre-sales Agent Workbench。它不只是回答客户问题，而是能够规划任务、调用工具、检索来源、审查风险、检查 grounding、生成邮件草稿、压缩客户记忆，并通过 Agent Eval 评估整个工作流。

英文：

> I upgraded a RAG-based pre-sales knowledge assistant into an AI Pre-sales Agent Workbench that supports planning, tool use, retrieval, risk review, grounding checks, email drafting, memory compression, tracing, and agent evaluation.

# AI Pre-sales Agent Workbench Upgrade Plan

> Project: RAG-based AI Pre-sales Knowledge Assistant
> Upgrade Target: AI Pre-sales Agent Workbench
> Version: V2 Planning Draft
> Date: June 2026
> Author: Ran Wang

---

## 1. Project New Positioning｜项目新定位

### 1.1 Original Project Positioning

The original project is a reliable RAG-based B2B SaaS pre-sales knowledge assistant.

It focuses on:

* Semantic retrieval with Chroma
* Source-grounded answer generation
* Retrieval evaluation
* Answer evaluation
* Guardrails
* Trace logging
* Streamlit demo

This version proves that the system can answer customer questions based on product documents and reduce hallucination risk through retrieval, source citation, and evaluation.

### 1.2 New Project Positioning

The upgraded project will become:

**AI Pre-sales Agent Workbench｜基于 RAG + Multi-Agent Harness 的 B2B SaaS 售前智能工作台**

The goal is not to simply add more technologies. The goal is to upgrade the project from a reliable RAG demo into an explainable, evaluable, and interview-ready Agent workflow.

The new system should demonstrate:

* How an AI pre-sales assistant understands customer intent
* How it selects tools safely
* How it retrieves and verifies sources
* How it handles high-risk business questions
* How it drafts customer-facing follow-up emails
* How it maintains compressed customer memory
* How every agent step can be traced and evaluated

### 1.3 Interview Value

This project is designed for the following target roles:

* AI Solutions Intern
* AI Pre-sales Intern
* LLM Application Intern
* Technical Consultant Intern
* AI Application Layer Intern

The key interview message is:

> I built an AI pre-sales workbench that does not only answer questions with RAG, but also plans the task, selects tools, reviews risk, checks source grounding, drafts follow-up emails, compresses customer memory, and evaluates the whole agent workflow.

---

## 2. Agent Workflow｜Agent 总流程

### 2.1 High-level Workflow

The upgraded workflow is:

```text
User Question
    ↓
Load Memory
    ↓
Planner Agent
    ↓
Tool Registry / Safe Executor
    ↓
Retrieval Agent
    ↓
Raw Answer Generation
    ↓
Risk Review Agent
    ↓
Critic Agent
    ↓
Final Answer
    ↓
Email Agent
    ↓
Memory Manager
    ↓
Trace Logger
    ↓
Human Review Boundary
```

### 2.2 Detailed Workflow

1. User submits a pre-sales question.
2. Memory Manager loads short-term memory, session memory, and customer profile memory.
3. Planner Agent analyzes:

   * customer intent
   * risk level
   * required tools
   * whether retrieval is required
   * whether email draft is needed
4. Tool Registry checks whether the selected tool is allowed.
5. Safe Executor runs the tool with timeout, schema validation, and fallback.
6. Retrieval Agent calls `search_docs` based on the user question and planner output.
7. The system generates a raw answer using retrieved context.
8. Risk Review Agent checks whether the question or answer involves high-risk topics.
9. Critic Agent verifies whether important claims are supported by retrieved sources.
10. Final answer is generated with risk notes and source grounding.
11. Email Agent generates a customer follow-up email draft.
12. Memory Manager compresses the conversation into structured memory.
13. Trace Logger records the full execution process.
14. Human Review is required for sensitive or high-risk outputs.

---

## 3. Agents Responsibility Design｜Agents 分工

## 3.1 Planner Agent

### Responsibility

Planner Agent is responsible for understanding the user question and deciding the execution plan.

### Inputs

* user question
* short-term memory
* session memory
* customer profile memory

### Outputs

```json
{
  "intent": "pricing_question | technical_question | deployment_question | security_question | case_study_question | general_product_question | unknown",
  "risk_level": "low | medium | high",
  "required_tools": ["search_docs"],
  "requires_retrieval": true,
  "requires_email_draft": true,
  "requires_human_review": false,
  "planning_reason": "The question asks about deployment and SLA, so retrieval and risk review are required."
}
```

### Interview Talking Point

Planner Agent shows that the system is not a simple chatbot. It first plans the task before answering.

---

## 3.2 Retrieval Agent

### Responsibility

Retrieval Agent reuses the existing Chroma RAG pipeline and wraps it as a skill.

### Main Skill

```text
search_docs(query, top_k, risk_level)
```

### Behavior

For low-risk questions:

* use normal top-k retrieval

For medium-risk questions:

* increase top-k
* prefer policy, SLA, security, and deployment documents if available

For high-risk questions:

* perform stricter retrieval
* optionally rewrite the query
* require stronger source support
* trigger human review if evidence is weak

### Interview Talking Point

Retrieval Agent shows that retrieval strategy can change based on business risk instead of using the same top-k setting for every question.

---

## 3.3 Risk Review Agent

### Responsibility

Risk Review Agent checks whether the question or answer contains sensitive pre-sales risk.

### Risk Categories

* pricing commitment
* SLA guarantee
* HIPAA / compliance claim
* customer case or named customer reference
* private deployment
* data security
* integration promise
* roadmap or future feature commitment
* legal or contractual wording

### Outputs

```json
{
  "risk_level": "low | medium | high",
  "risk_categories": ["SLA", "deployment"],
  "requires_human_review": true,
  "safe_response_guidance": "Avoid making a guaranteed SLA commitment. Ask the customer to confirm requirements and suggest sales/legal review."
}
```

### Interview Talking Point

Risk Review Agent shows that the system understands pre-sales risk and does not blindly generate confident business promises.

---

## 3.4 Critic Agent

### Responsibility

Critic Agent checks whether final answer claims are supported by retrieved sources.

### Problem Solved

A common RAG weakness is:

> Having sources does not always mean the answer is truly grounded.

Critic Agent addresses this by checking whether key claims are supported.

### Checks

* Does the answer mention a product feature not found in retrieved sources?
* Does the answer make pricing, SLA, compliance, or deployment claims without evidence?
* Does the answer overstate uncertain information?
* Does the answer cite sources that are only loosely related?
* Should the answer be revised or refused?

### Outputs

```json
{
  "grounding_status": "supported | partially_supported | unsupported",
  "unsupported_claims": [
    "The answer says HIPAA-ready, but no retrieved source supports this claim."
  ],
  "revision_required": true,
  "critic_note": "Remove unsupported HIPAA claim and provide a safer answer."
}
```

### Interview Talking Point

Critic Agent demonstrates deeper AI application thinking: source citation alone is not enough; claim-level support matters.

---

## 3.5 Email Agent

### Responsibility

Email Agent creates a customer follow-up email draft based on:

* final answer
* retrieved sources
* risk note
* open questions
* next actions

### Boundary

Email Agent only generates drafts. It never sends emails automatically.

### Output

```json
{
  "subject": "Follow-up on your InsightFlow AI deployment questions",
  "email_draft": "Hi ..., Thanks for your questions about deployment..."
}
```

### Interview Talking Point

Email Agent turns the RAG answer into a realistic pre-sales workflow artifact.

---

## 3.6 Memory Manager

### Responsibility

Memory Manager maintains structured memory across the conversation.

### Memory Layers

1. Short-term memory
2. Session memory
3. Customer profile memory

### Short-term Memory

Stores recent turns in the current interaction.

Example:

```json
{
  "recent_user_questions": [],
  "recent_agent_answers": [],
  "temporary_constraints": []
}
```

### Session Memory

Stores important facts from the current session.

Example:

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

Stores compressed customer information.

Example:

```json
{
  "customer_name": "Unknown",
  "industry": "B2B SaaS",
  "company_size": "Unknown",
  "use_case": "Customer segmentation and pre-sales analytics",
  "confirmed_facts": [],
  "risk_concerns": [],
  "preferred_deployment": "Unknown",
  "open_questions": [],
  "next_actions": []
}
```

---

## 4. Tools / Skills Design｜Tools 与 Skills 设计

## 4.1 Tool Registry

Tool Registry defines which tools are available to agents.

Initial tools:

| Tool Name       | Purpose                                             | Risk Level | Status |
| --------------- | --------------------------------------------------- | ---------: | ------ |
| search_docs     | Search product and sales documents using Chroma RAG |     Medium | V1     |
| generate_answer | Generate source-grounded answer                     |     Medium | V1     |
| review_risk     | Review business and compliance risk                 |       High | V1     |
| critic_check    | Check answer grounding                              |       High | V1     |
| draft_email     | Generate customer follow-up email draft             |     Medium | V1     |
| compress_memory | Compress multi-turn conversation into memory        |     Medium | V1     |

## 4.2 Tool Schema

Every tool should have:

```json
{
  "tool_name": "search_docs",
  "description": "Search source documents using Chroma retrieval.",
  "input_schema": {},
  "output_schema": {},
  "timeout_seconds": 10,
  "fallback_strategy": "return_empty_result_with_warning"
}
```

## 4.3 Safe Executor

Safe Executor is responsible for:

* checking whether the tool exists
* validating input schema
* setting timeout
* catching errors
* returning fallback output
* writing tool trace logs

### Safe Executor Principle

The agent should not directly run arbitrary logic. It should only call registered tools through the safe executor.

---

## 5. Memory Compression Design｜记忆压缩设计

## 5.1 Goal

Memory compression turns a long conversation into a structured and reusable customer memory object.

The goal is not to store everything, but to keep only information useful for future pre-sales work.

## 5.2 Compression Output

```json
{
  "customer_profile": {
    "customer_name": "Unknown",
    "industry": "Unknown",
    "company_size": "Unknown",
    "use_case": "Unknown"
  },
  "confirmed_facts": [],
  "risk_concerns": [],
  "open_questions": [],
  "next_actions": [],
  "summary": "The customer is exploring InsightFlow AI and asked about deployment, SLA, and integration requirements."
}
```

## 5.3 What Should Be Remembered

The system should remember:

* confirmed customer requirements
* deployment preference
* integration needs
* risk concerns
* important constraints
* follow-up tasks
* unresolved questions

## 5.4 What Should Not Be Remembered

The system should not remember:

* unsupported assumptions
* private personal information unrelated to pre-sales
* temporary wording
* hallucinated facts
* claims rejected by Critic Agent

## 5.5 Human Review Rule

If memory contains high-risk business assumptions, it should be marked as requiring human review.

---

## 6. Agent Harness Design｜Agent Harness 设计

## 6.1 Goal

Agent Harness controls the full workflow execution.

It makes the agent system:

* modular
* traceable
* testable
* safer
* easier to explain in interviews

## 6.2 Core Modules

Initial modules:

```text
agent_workbench/
    agents/
        planner_agent.py
        retrieval_agent.py
        risk_review_agent.py
        critic_agent.py
        email_agent.py
        memory_manager.py

    harness/
        tool_registry.py
        safe_executor.py
        output_validator.py
        agent_orchestrator.py

    schemas/
        planner_schema.py
        trace_schema.py
        memory_schema.py

    eval/
        run_agent_eval.py
        agent_eval_dataset.csv

    traces/
        agent_traces.jsonl
```

## 6.3 Harness Responsibilities

The harness should:

1. receive the user question
2. call Planner Agent
3. validate planner output
4. execute required tools
5. call Retrieval Agent
6. generate raw answer
7. call Risk Review Agent
8. call Critic Agent
9. generate final answer
10. call Email Agent
11. compress memory
12. write trace logs
13. return structured output

## 6.4 Fallback Strategy

Fallback behavior:

| Failure Case             | Fallback                                         |
| ------------------------ | ------------------------------------------------ |
| Planner output invalid   | use default safe plan                            |
| Retrieval fails          | return answer with insufficient evidence warning |
| Risk review fails        | mark risk as medium and require review           |
| Critic fails             | mark grounding as uncertain                      |
| Email draft fails        | return final answer only                         |
| Memory compression fails | keep raw short-term memory only                  |

---

## 7. Agent Eval Harness Design｜Agent Eval Harness 设计

## 7.1 Goal

Agent Eval Harness evaluates whether the whole agent workflow behaves correctly.

It should go beyond simple answer quality evaluation.

## 7.2 Dataset

New file:

```text
eval/agent_eval_dataset.csv
```

Suggested columns:

| Column                   | Meaning                                    |
| ------------------------ | ------------------------------------------ |
| case_id                  | test case id                               |
| user_question            | customer question                          |
| expected_intent          | expected intent classification             |
| expected_tools           | expected tools                             |
| expected_risk_level      | expected risk level                        |
| expected_refusal         | whether refusal or safe answer is expected |
| expected_source_keywords | expected source hit keywords               |
| expected_email_points    | key points required in email draft         |
| expected_memory_points   | facts that should be retained in memory    |

## 7.3 Metrics

Initial metrics:

| Metric                       | Meaning                                                     |
| ---------------------------- | ----------------------------------------------------------- |
| intent_accuracy              | whether Planner Agent identifies correct intent             |
| tool_selection_accuracy      | whether selected tools are correct                          |
| source_hit_rate              | whether retrieved sources contain expected keywords         |
| refusal_accuracy             | whether risky unsupported questions are refused or softened |
| risk_classification_accuracy | whether risk level is correct                               |
| email_draft_completeness     | whether email draft covers required points                  |
| memory_retention_accuracy    | whether compressed memory keeps important facts             |

## 7.4 Eval Output

New file:

```text
eval/agent_eval_results.csv
```

Suggested columns:

```text
case_id,
intent_pass,
tool_selection_pass,
source_hit_pass,
refusal_pass,
risk_classification_pass,
email_draft_pass,
memory_retention_pass,
overall_pass,
notes
```

---

## 8. Agent Trace Fields Design｜Agent Trace 字段设计

Trace file:

```text
traces/agent_traces.jsonl
```

Each line represents one full agent run.

## 8.1 Required Trace Fields

```json
{
  "run_id": "run_202606_xxx",
  "timestamp": "2026-06-xxTxx:xx:xx",
  "user_question": "",
  "memory_loaded": {},
  "planner_output": {},
  "tools_called": [],
  "retrieved_sources": [],
  "raw_answer": "",
  "risk_decision": {},
  "critic_decision": {},
  "final_answer": "",
  "email_draft": "",
  "memory_summary": {},
  "human_review_required": false,
  "latency_ms": 0,
  "errors": []
}
```

## 8.2 Why Trace Matters

Trace is important because it shows:

* how the agent made decisions
* which tools were used
* which sources were retrieved
* whether risk was detected
* whether the final answer was grounded
* whether human review was required
* how long the workflow took

This makes the project more credible for interviews and demos.

---

## 9. Human Review Boundary｜人工复核边界

## 9.1 Human Review Is Required When

Human review should be required when:

* the answer contains pricing commitment
* the answer mentions SLA guarantee
* the answer discusses HIPAA or legal compliance
* the answer references named customer cases
* the answer makes deployment promises
* retrieved evidence is weak
* Critic Agent finds unsupported claims
* customer asks for contract, legal, or security guarantee
* memory compression contains high-risk assumptions

## 9.2 Human Review Is Not Required When

Human review is usually not required when:

* the answer explains general product features
* the answer summarizes clearly retrieved documentation
* the answer asks clarifying questions
* the answer refuses unsupported claims safely
* the email draft only summarizes confirmed information

## 9.3 System Boundary

The system can:

* answer with source-grounded information
* ask clarifying questions
* generate safe follow-up drafts
* flag risks
* recommend human review

The system cannot:

* sign contracts
* promise pricing
* guarantee SLA
* confirm legal compliance without evidence
* send emails automatically
* invent customer cases
* store unsupported customer facts as confirmed memory

---

## 10. V1 / V2 Development Roadmap｜开发路线

## 10.1 V1 Goal

V1 goal:

> Build a runnable single-session Agent Workbench workflow based on the existing RAG project.

V1 should include:

1. Planner Agent
2. Retrieval Agent using existing Chroma RAG
3. Risk Review Agent
4. Critic Agent
5. Email Agent
6. Memory Manager basic version
7. Tool Registry
8. Safe Executor
9. Agent Trace JSONL
10. Small Agent Eval Dataset
11. Basic Streamlit display update

V1 should not include:

* PostgreSQL
* Redis
* OpenSearch
* Airflow
* Docker Compose
* MCP server
* LangGraph
* complex frontend rewrite

## 10.2 V2 Goal

V2 goal:

> Improve reliability, evaluation depth, and demo quality.

V2 may include:

1. better query rewrite for high-risk retrieval
2. stronger claim-level critic
3. more complete memory compression
4. richer agent eval dataset
5. better Streamlit trace viewer
6. downloadable email draft
7. customer profile panel
8. more polished case study screenshots
9. interview-ready architecture diagram
10. updated README and Feishu case study

## 10.3 Final Portfolio Output

Final project deliverables should include:

* GitHub README
* architecture document
* agent workflow diagram
* Streamlit demo screenshots
* agent trace example
* eval report
* Feishu case study
* resume bullet
* interview pitch

---

## 11. One-sentence Portfolio Pitch｜一句话作品集定位

English:

> Built an AI Pre-sales Agent Workbench that combines RAG, multi-agent planning, risk review, claim-level grounding check, email draft generation, memory compression, and agent evaluation for B2B SaaS pre-sales scenarios.

Chinese:

> 我构建了一个面向 B2B SaaS 售前场景的 AI Agent 工作台，不只是做 RAG 问答，而是实现了任务规划、工具调用、风险审查、声明级 grounding 检查、客户邮件草稿、记忆压缩和 Agent Eval。
