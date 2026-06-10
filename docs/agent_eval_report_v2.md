# Agent Workbench V2 Eval Report

## 总览

- 测试用例数：22
- overall_pass：22/22
- pass rate：100.0%
- average_latency_ms：3.09
- max_latency_ms：5

## 风险案例表现

- 高风险/敏感场景数量：13
- 高风险场景通过数：13/13
- 覆盖场景：pricing、SLA、HIPAA、GDPR、SOC2、private deployment、customer case、roadmap。

## 失败案例

- 暂无失败案例。

## 说明

本评估运行完整 Agent workflow，包括 Planner、Safe Executor、Retrieval、Risk Review、Critic、Answer、Email、Memory。当前环境如果没有 chromadb，Retrieval Agent 会优先记录 Chroma 不可用，然后自动 fallback 到 Markdown 检索；这属于预期行为，不会导致 workflow 崩溃。
