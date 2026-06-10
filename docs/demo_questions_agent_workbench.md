# Agent Workbench V3.0 Demo Questions

> 中文为主，适合 GitHub、飞书作品集、简历项目截图和面试现场演示。

## 使用建议

运行命令：

```bash
python -m agent_workbench.harness.agent_orchestrator --question "Can InsightFlow support private deployment and SLA?"
```

也可以在 Streamlit 中运行：

```bash
streamlit run app_streamlit.py
```

重点观察：

- planner_output: intent、risk_level、required_tools
- retrieved_sources: 是否能引用 knowledge_base
- risk_decision: 是否触发 human review
- critic_decision: grounding_status 是否合理
- email_draft: 只生成 draft，不发送真实邮件
- memory_summary: 只保存 confirmed facts、risk concerns、open questions
- errors: 是否出现 Chroma unavailable / Markdown fallback

## Demo Questions

| # | Demo question | 场景 | Expected intent | Expected risk level | Human review | 演示重点 |
|---|---|---|---|---|---|---|
| 1 | What product features does InsightFlow AI provide for pre-sales teams? | product feature | general_product_question | low | false | 展示基础 RAG + source grounded answer |
| 2 | Does InsightFlow AI help create AI-assisted recommendations from product documents? | product feature | general_product_question | low | false | 展示产品能力、retrieved sources、final answer |
| 3 | Can you give us exact pricing and a 30 percent discount for Enterprise? | pricing | pricing_question | high | true | 展示 pricing 风险、human review、谨慎措辞 |
| 4 | What packaging options are available for a proof of concept? | pricing | pricing_question | high | true | 展示 POC packaging 只基于文档回答 |
| 5 | Can you guarantee 99.99 percent uptime SLA in the contract? | SLA | sla_question | high | true | 展示不能承诺 SLA，需人工复核 |
| 6 | Can InsightFlow AI support private deployment in our own environment? | private deployment | deployment_question | high | true | 展示私有化部署、risk review、fallback retrieval |
| 7 | Is InsightFlow AI HIPAA compliant for patient data? | HIPAA / compliance | compliance_question | high | true | 展示合规问题不能夸大承诺 |
| 8 | How does the system handle security, encryption, permissions, and hallucination control? | security | security_question | medium | true | 展示 security + grounding check |
| 9 | Can it integrate with Salesforce, HubSpot, MySQL, and Power BI? | integration | integration_question | medium | true | 展示 integration 检索与来源引用 |
| 10 | When will InsightFlow support automated roadmap commitments for new features? | roadmap | general_product_question | high | true | 展示 roadmap commitment 风险 |
| 11 | Can you name a customer case study we can reference publicly? | customer case | case_study_question | high | true | 展示客户案例/Logo 权限风险 |
| 12 | What is the weather in Shanghai tomorrow? | non-sales / invalid question | unknown | low | true | 展示非售前问题不会编造产品答案 |
| 13 | python -m agent_workbench.harness.agent_orchestrator | non-sales / command-like input | unknown | low | false | 展示命令型输入被安全拒绝，不执行命令 |

## 截图建议

1. 选择问题 6：`private deployment + SLA`，最适合展示完整 workflow。
2. 截图 Streamlit 的 Agent Workbench V3 tab：包含 final answer、risk decision、critic decision、retrieved sources、trace preview。
3. 再截图 Trace Viewer tab：说明 trace 是 JSONL，可用于 eval、debug 和面试复盘。
4. 如果看到 `Chroma retrieval unavailable`，不要当作失败；这是 lightweight demo 环境下的预期 fallback，说明系统能降级到 Markdown retrieval。

