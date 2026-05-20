# InsightFlow AI — Frequently Asked Questions

## What is InsightFlow AI?
InsightFlow AI is a fictional AI-assisted business decision platform. It helps teams transform customer data, product documents, FAQs, and business reports into searchable knowledge and AI-generated recommendations.

## Is it a model training platform?
No. It does not train large language models from scratch. It focuses on LLM application workflows such as RAG, data pipeline automation, business insight generation, and human review.

## Can InsightFlow AI connect to MySQL?
Yes. In a production deployment, MySQL can serve as the operational data source. The pipeline can read business data from MySQL, transform it into processed analytical tables, and make it available for AI insights or BI dashboards.

## Can InsightFlow AI connect to Power BI?
Yes. In a local demo, the system can export CSV files that Power BI reads and refreshes. In a production setup, Power BI can connect to database tables or scheduled dataflows.

## What is RAG?
RAG stands for Retrieval-Augmented Generation. It allows a language model to answer questions based on retrieved context from a knowledge base rather than relying only on the model's internal knowledge.

## Why is RAG useful for pre-sales?
Pre-sales teams need to answer product, pricing, integration, security, and deployment questions quickly. RAG retrieves the relevant source documents and helps generate customer-ready answers with evidence.

## Does the assistant provide source references?
Yes. The recommended design shows source documents, matched chunks, and review status. This reduces hallucination risk and helps reviewers verify the answer.

## Can AI recommendations be sent automatically?
No. AI-generated answers are drafts. Customer-facing responses and business recommendations should be reviewed by a human before use.
