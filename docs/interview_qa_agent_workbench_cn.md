# Agent Workbench Interview Q&A

## 1. 这个项目一句话怎么介绍？

这是一个面向 B2B SaaS 售前场景的 RAG + Multi-Agent Workflow 作品集项目。它把原来的知识库问答升级成 Agent Workbench，支持 intent planning、retrieval fallback、risk review、critic grounding check、email draft、memory compression、trace 和 eval。

## 2. 为什么 RAG 还不够？

RAG 主要解决“找资料并回答”的问题，但售前场景还需要判断风险、避免承诺、检查 grounding、生成 follow-up draft、记录可确认记忆，并且需要 trace 和 eval 来复盘。这些不是单次 RAG QA 自然具备的能力。

## 3. 为什么升级成 Agent Workbench？

因为 Agent Workbench 更适合展示完整 AI application engineering：每一步有明确职责、输入输出和 trace。它能说明我不仅会做 RAG，也理解 tool governance、fallback、review、eval 和可演示交付。

## 4. Planner Agent 做什么？

Planner Agent 负责识别用户问题的 intent、risk_level、required_tools，并判断是否需要 retrieval、email draft 和 human review。它相当于 workflow 的路由和任务规划层。

## 5. Retrieval Agent 如何 fallback？

Retrieval Agent 优先调用 Chroma retrieval。如果 `chromadb` 不可用或检索失败，会记录错误并 fallback 到 `knowledge_base/*.md` 的 Markdown retrieval。低分或无结果时还会做 query rewrite fallback。

## 6. Chroma unavailable 是失败吗？

不是。作品集环境经常没有完整向量库依赖，所以系统明确把 Chroma unavailable 记录到 errors，然后继续使用 Markdown fallback。这体现 graceful degradation。

## 7. Answer Agent 和普通 LLM 回答有什么区别？

Answer Agent 不只是让 LLM 自由回答，而是基于 retrieved sources、risk_decision 和 critic_decision 生成 final answer。高风险问题会用谨慎措辞，并避免 unsupported commitment。

## 8. Risk Review Agent 做什么？

Risk Review Agent 判断售前风险，例如 pricing、SLA、HIPAA、GDPR、SOC2、private deployment、customer case、roadmap、legal wording。高风险问题会触发 human review。

## 9. Critic Agent 和 Risk Review 的区别？

Risk Review 看的是业务风险和承诺风险；Critic 看的是回答是否被 retrieved sources 支撑。一个偏 business/compliance，一个偏 grounding/faithfulness。

## 10. 为什么需要 Critic Agent？

因为 RAG 检索到资料不代表最终回答一定忠实。Critic Agent 会检查关键 claim，发现 unsupported claims 时标记 revision_required 或 human review。

## 11. Email Agent 为什么只生成 draft？

售前邮件可能涉及价格、合同、合规和客户承诺，不能自动外发。Email Agent 只生成 draft，让人类 review 后再发送，降低误发和过度承诺风险。

## 12. Memory Manager 如何避免保存幻觉？

Memory Manager 只保存 confirmed facts、risk concerns、open questions 和 next actions。它不会把 unsupported claims、用户命令、非售前内容或模型生成的未证实承诺写入 confirmed facts。

## 13. Tool Registry 为什么重要？

Tool Registry 明确 workflow 中允许调用哪些工具，以及工具的输入输出边界。它避免 Agent 随意调用函数，也方便 trace 和 eval 检查 tool selection。

## 14. Safe Executor 是不是 sandbox？

不是完整 sandbox。Safe Executor 是 workflow-level guardrail，用于统一执行工具、捕获异常、记录 latency、status 和 error。它不执行任意系统命令，也不替代 OS sandbox。

## 15. Output Validator 解决什么问题？

Output Validator 负责把 Agent 输出校验成稳定 schema。即使输出缺字段、类型不对或 JSON parse 出错，也会转成安全 fallback，避免 workflow 崩溃。

## 16. Trace 记录什么？

Trace 记录 run_id、timestamp、user_question、planner_output、tools_called、retrieved_sources、risk_decision、critic_decision、final_answer、email_draft、memory_summary、human_review_required、latency_ms 和 errors。

## 17. 为什么用 JSONL 做 trace？

JSONL 简单、可追加、可读、易于 eval 脚本处理。对作品集项目来说，它比引入数据库更轻量，也更容易在 GitHub 上展示。

## 18. Agent Eval 怎么设计？

Agent Eval 运行完整 orchestrator，而不是只测单个函数。每条 case 检查 intent、tool selection、risk classification、安全回答、email draft、memory retention，并计算 overall_pass。

## 19. Eval 覆盖哪些场景？

覆盖 product feature、pricing、SLA、HIPAA、GDPR、SOC2、private deployment、customer case、roadmap、security、integration、memory 和 invalid / non-sales question。

## 20. 22/22 eval pass 说明什么？

说明当前规则化 workflow 能稳定通过这 22 条作品集评估样例。它不代表生产级鲁棒性，但可以证明 intent、risk、fallback、email draft、memory 和 trace 的主路径是可运行的。

## 21. 为什么不用 LangGraph？

这个项目的目标是展示轻量、可解释、可本地运行的 Agent workflow。当前流程规模不大，用自定义 orchestrator 更容易让面试官看清每一步，也避免引入框架复杂度。

## 22. 为什么不用 MCP？

当前没有真实外部 tool ecosystem 需求，也不需要跨应用工具协议。为了保持作品集可运行和易讲解，使用本地 Tool Registry 和 Safe Executor 就够了。

## 23. 为什么不用 Docker Compose？

项目刻意避免复杂部署依赖，方便在本地、GitHub 和面试环境中直接运行。Docker Compose 更适合多服务生产化演示，但当前不是目标。

## 24. 为什么不用 PostgreSQL、Redis、OpenSearch？

这些组件会让架构更像生产系统，但也增加环境成本。当前作品集重点是 RAG、Agent workflow、trace 和 eval，所以保留 Markdown、JSONL 和本地文件更合适。

## 25. 项目最大的工程亮点是什么？

最大亮点是把 RAG demo 升级成可复盘的 Agent Workbench：有 Planner、Risk Review、Critic、Memory、Tool Trace 和 Agent Eval，同时保持代码轻量、可运行、可解释。

## 26. 项目局限性是什么？

它不是生产级系统，没有租户隔离、复杂权限、审计、真实邮件发送、外部网络调用和大规模 eval。检索 fallback 也只是轻量 Markdown retrieval。

## 27. 如果继续升级，你会做什么？

我会扩展 eval dataset，加入人工标注 UI、source citation quality score、trace diff、risk taxonomy、更多 retrieval backend，并让 Streamlit 支持高风险回答的人类复核流程。

## 28. 面试官问“这是不是过度设计”怎么回答？

我会说这是有边界的工程升级。项目没有引入重型中间件和编排框架，只把售前问答中真实需要的 planning、risk、grounding、draft、memory、trace、eval 拆成清晰模块。

## 29. 这个项目适合什么岗位？

适合 AI Solutions Intern、AI Pre-sales Intern、LLM Application Intern、Technical Consultant Intern，因为它结合了业务场景、RAG、Agent workflow、风险控制和可演示交付。

## 30. 如何现场演示？

先运行 private deployment + SLA 问题，展示 final answer、retrieved sources、risk decision、critic decision、email draft、memory summary 和 trace preview。然后运行 eval，展示 `22/22 overall_pass`。

