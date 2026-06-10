# Agent Workbench V2 Eval Report

## 总览

- 测试用例数：22
- overall_pass：22/22
- pass rate：100.0%
- average_latency_ms：3.18
- max_latency_ms：5

## 风险案例表现

- 高风险/敏感场景数量：13
- 高风险场景通过数：13/13
- 覆盖场景：pricing、SLA、HIPAA、GDPR、SOC2、private deployment、customer case、roadmap。
- 高风险问题会触发 human review，并避免 exact pricing、contractual SLA、HIPAA guarantee、roadmap commitment 等 unsupported commitment。

## Fallback 行为

- fallback case count：20
- 当前轻量环境如果没有 `chromadb`，Retrieval Agent 会记录 `Chroma retrieval unavailable`，然后自动 fallback 到 `knowledge_base/*.md` 的 Markdown retrieval。
- Markdown fallback 是预期降级路径，不代表 Agent workflow 失败；它会继续保留 retrieved_sources、risk_decision、critic_decision、email_draft、memory_summary 和 errors。

## 失败案例

- 暂无失败案例。

## 面试解释话术

- 这个 eval 不是宣称生产级鲁棒性，而是验证作品集核心 workflow：Planner、Safe Executor、Retrieval fallback、Risk Review、Critic、Answer、Email Draft、Memory 和 Trace。
- `22/22 overall_pass` 表示当前 22 条售前样例都通过预设检查，覆盖 intent、tool selection、risk classification、safe answer、email draft 和 memory retention。
- Chroma unavailable 时仍能通过，是因为项目刻意设计了 Markdown fallback，保证本地 demo 和面试环境不会因为缺少可选依赖而崩溃。

## 说明

本评估运行完整 Agent workflow，包括 Planner、Safe Executor、Retrieval、Risk Review、Critic、Answer、Email、Memory。当前环境如果没有 chromadb，Retrieval Agent 会优先记录 Chroma 不可用，然后自动 fallback 到 Markdown 检索；这属于预期行为，不会导致 workflow 崩溃。
