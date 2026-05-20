# InsightFlow AI — Deployment Guide

## Local Portfolio Demo

```text
Markdown / CSV files
        ↓
Python ingestion
        ↓
Local vector store
        ↓
Mock LLM or API-based LLM
        ↓
Generated answers with sources
        ↓
Human review
```

Recommended stack:
- Python
- Markdown knowledge files
- Chroma or FAISS
- Mock LLM mode or cloud LLM API
- Streamlit or command-line interface

## Internal Business Prototype

```text
Internal documents + database tables
        ↓
Scheduled Python pipeline
        ↓
Vector database
        ↓
LLM API
        ↓
Answer generation and review table
        ↓
BI dashboard or web interface
```

Recommended stack:
- Python
- FastAPI or Streamlit
- MySQL or PostgreSQL
- Chroma, FAISS, Milvus, or Pinecone
- Power BI or internal dashboard

## Enterprise Deployment
Enterprise deployment should include role-based access control, document-level permissions, audit logs, API key management, cost monitoring, and human approval workflows.

## Integration With Power BI
For a demo, the system can export CSV files that Power BI reads. For production, the system should write processed results to a database table and let Power BI connect to that table.

## Human Review Workflow
Every generated answer should include:
- Direct answer
- Supporting source
- Suggested response
- Review status
- Risk note
