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
