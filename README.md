# RAG-based AI Pre-sales Knowledge Assistant

## Project Overview

This project is a local prototype of a **RAG-based AI Pre-sales Knowledge Assistant**.

It transforms static pre-sales materials, such as product FAQs, deployment guides, pricing documents, security notes, integration documents, customer case studies, and email templates, into a searchable knowledge base.

When a user asks a natural-language pre-sales question, the system retrieves relevant knowledge chunks, generates a structured pre-sales response, and provides source citations for human review.

This project is designed for AI Solutions, AI Pre-sales, Technical Consultant, and LLM Application roles.

---

## Business Pain Point

In many B2B software companies, pre-sales knowledge is scattered across static documents:

- Product overview documents
- FAQ pages
- Deployment guides
- Pricing notes
- API integration documents
- Security and governance materials
- Customer case studies
- Objection handling scripts
- Email templates

Traditional workflow:

```text
Sales or pre-sales consultant
→ Manually search documents
→ Copy relevant information
→ Rewrite customer-facing response
→ Ask technical team for confirmation
```

This creates several problems:

- Slow response time
- Inconsistent answers
- High dependency on experienced consultants
- Risk of over-promising to clients
- Difficulty tracking answer sources

This project upgrades the workflow into a lightweight AI-assisted pre-sales knowledge assistant.

---

## Solution Design

The assistant follows a local RAG-style workflow:

```text
Markdown knowledge documents
        ↓
Document loading
        ↓
Chunk generation
        ↓
TF-IDF local retrieval
        ↓
Template-based pre-sales answer generation
        ↓
Source citation
        ↓
Human review
```

Current version:

```text
RAG v1: Local free prototype
```

It does not require an API key, external LLM, embedding model, or vector database.

The goal of this version is to demonstrate the core RAG workflow clearly and reliably before upgrading to a production LLM-based version.

### RAG v1: Local TF-IDF Prototype

The first version of this project implements a fully local and free RAG-style workflow:

```text
Markdown knowledge documents
        ↓
Document loading
        ↓
Chunk generation
        ↓
TF-IDF local retrieval
        ↓
Template-based pre-sales answer generation
        ↓
Source citation
        ↓
Human review
```

This version is useful for validating the core RAG workflow without requiring API keys, external LLMs, embedding models, or vector databases.

---

### RAG v2: Embedding + Chroma Semantic Retrieval

The second version upgrades the retrieval layer from keyword-based TF-IDF search to embedding-based semantic retrieval.

```text
Markdown knowledge documents
        ↓
Document loading
        ↓
Chunk generation
        ↓
Sentence-transformers embeddings
        ↓
Chroma local vector store
        ↓
Semantic retrieval
        ↓
Template-based pre-sales answer generation
        ↓
Source citation
        ↓
Human review
```

In this version, each document chunk is converted into an embedding vector and stored in a local Chroma vector database. When a user asks a question, the question is also converted into an embedding, and Chroma retrieves the most semantically similar chunks.

This allows the assistant to retrieve relevant knowledge even when the user does not use the exact same keywords as the source documents.

For example:

```text
User question:
Can InsightFlow AI work with our reporting dashboard and database?

Possible retrieved knowledge:
- Power BI integration
- MySQL integration
- BI dashboard workflow
- API-based system integration
```

This makes the assistant closer to a real-world RAG application.

---

## Repository Structure

```text
RAG-based-AI-Presales-Knowledge-Assistant/
│
├── knowledge_base/
│   ├── 01_product_overview.md
│   ├── 02_faq.md
│   ├── 03_pricing_and_packaging.md
│   ├── 04_deployment_guide.md
│   ├── 05_security_and_governance.md
│   ├── 06_integrations_and_api.md
│   ├── 07_customer_case_studies.md
│   ├── 08_objection_handling.md
│   └── 09_presales_email_templates.md
│
├── eval/
│   └── sample_eval_questions.csv
│
├── rag_app/
│   ├── load_documents.py
│   ├── chunk_documents.py
│   ├── retrieve_context.py
│   ├── generate_answer.py
│   ├── main.py
│   ├── embedding_client.py
│   ├── build_vector_store.py
│   ├── retrieve_context_chroma.py
│   ├── generate_answer_chroma.py
│   └── main_chroma.py
│
├── outputs/
│   └── generated runtime files
│
├── vector_store/
│   └── reserved for future embedding/vector DB version
│
├── docs/
│   └── project documentation and interview notes
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Core Workflow

### 1. Document Loading

Implemented in:

```text
rag_app/load_documents.py
```

This script reads all Markdown files from:

```text
knowledge_base/
```

Each document is loaded with metadata:

- source file name
- full document content

---

### 2. Chunk Generation

Implemented in:

```text
rag_app/chunk_documents.py
```

Long Markdown documents are split into smaller overlapping chunks.

Each chunk contains:

- `chunk_id`
- `source_file`
- `chunk_index`
- `text`

This makes the knowledge base searchable at a granular level.

---

### 3. Local Retrieval

Implemented in:

```text
rag_app/retrieve_context.py
```

The current version uses **TF-IDF retrieval** through `scikit-learn`.

When the user asks a question, the system compares the question against all document chunks and returns the most relevant chunks.

This local retrieval design is:

- Free
- Stable
- Easy to debug
- Suitable for understanding the RAG workflow
- Upgradeable to embedding-based vector search later

---

### 4. Template-based Answer Generation

Implemented in:

```text
rag_app/generate_answer.py
```

The current version generates structured pre-sales responses using rule-based templates.

The answer includes:

- User question
- Detected intent
- Direct answer
- Supporting evidence from retrieved chunks
- Suggested pre-sales response
- Human review reminder
- Source citations

This simulates how an LLM-based system should organize grounded answers.

---

### 5. Command-line Interface

Implemented in:

```text
rag_app/main.py
```

Run the assistant locally:

```powershell
python rag_app\main.py
```

Example questions:

```text
Can InsightFlow AI connect to MySQL and Power BI?
How does InsightFlow AI reduce hallucination risk?
What pricing plans are available?
Can the product be deployed in a private environment?
Do you have any retail customer case studies?
```

---

## How to Run Locally

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Generate document chunks

```powershell
python rag_app\chunk_documents.py
```

### 4. Test retrieval

```powershell
python rag_app\retrieve_context.py
```

### 5. Run the assistant

```powershell
python rag_app\main.py
```

---

## Example Output

Example user question:

```text
Can InsightFlow AI connect to MySQL and Power BI?
```

The assistant returns:

```text
Detected Intent:
integration

Direct Answer:
Based on the retrieved knowledge base, InsightFlow AI can support integration with external business systems such as databases, BI tools, and API-based workflows.

Supporting Evidence:
Retrieved chunks from integration and deployment documents.

Suggested Pre-sales Response:
Thank you for your question. Based on the available product knowledge base, InsightFlow AI can be positioned as a practical AI solution that connects business data, knowledge resources, and AI-generated recommendations into a reviewable workflow.

Human Review Reminder:
Please verify technical feasibility, pricing details, deployment constraints, and any client-specific commitments.

Sources:
- 06_integrations_and_api.md
- 04_deployment_guide.md
```

---

## How to Run RAG v2 with Chroma

### 1. Generate document chunks

```powershell
python rag_app\chunk_documents.py
```

### 2. Build the local Chroma vector store

```powershell
python rag_app\build_vector_store.py
```

This step converts document chunks into embeddings and stores them in:

```text
vector_store/chroma_db/
```

The `vector_store/` folder is ignored by Git because it is a local runtime artifact.

### 3. Test Chroma semantic retrieval

```powershell
python rag_app\retrieve_context_chroma.py
```

This verifies that the system can retrieve relevant chunks through embedding-based semantic search.

### 4. Generate a Chroma-based pre-sales answer

```powershell
python rag_app\generate_answer_chroma.py
```

### 5. Run the interactive Chroma assistant

```powershell
python rag_app\main_chroma.py
```

Example questions:

```text
Can InsightFlow AI work with our reporting dashboard and database?
How does InsightFlow AI reduce hallucination risk?
Can the product be deployed in a private environment?
What pricing plans are available?
Do you have any retail customer case studies?
```

---

## Human-in-the-loop Design

This assistant does not directly send answers to clients.

All generated responses should be reviewed by a human pre-sales or solution consultant before external communication.

Human reviewers should verify:

1. Technical feasibility
2. Pricing details
3. Deployment constraints
4. Security and compliance commitments
5. Client-specific assumptions
6. Whether the answer is fully supported by retrieved sources

This design reduces hallucination risk and prevents over-promising.

---

## Current Version vs. Future LLM Version

### RAG v1 — Local TF-IDF Version

```text
Markdown documents
→ chunks
→ TF-IDF retrieval
→ template-based answer
→ source citation
```

### RAG v2 — Embedding + Chroma Version

```text
Markdown documents
→ chunks
→ sentence-transformers embeddings
→ Chroma vector store
→ semantic retrieval
→ template-based answer
→ source citation
```

### Future RAG v3 — LLM-powered AI Pre-sales Agent

```text
Markdown / PDF / HTML documents
→ chunks
→ embeddings
→ vector database
→ LLM-generated answer
→ customer-facing email draft
→ follow-up recommendation
→ evaluation
→ human review
```

Future upgrades may include:

- OpenAI / Gemini / Claude API integration
- Local LLM integration through Ollama
- FAISS or Chroma vector store optimization
- Streamlit web interface
- Evaluation dataset and scoring
- API service with FastAPI
- Intent classification through LLM
- Automatic pre-sales email generation
- Follow-up action recommendation

---

## Role Relevance

This project demonstrates capabilities relevant to:

- AI Solutions Intern
- AI Pre-sales Intern
- LLM Application Intern
- Technical Consultant Intern
- AI Product Operations
- Customer Success Engineer

It shows understanding of:

- RAG workflow
- Knowledge base construction
- Retrieval-based answering
- Source citation
- Human-in-the-loop risk control
- Pre-sales business communication
- AI application prototyping

---

## Key Takeaway

This is not a static FAQ page.

It is a local RAG-style AI pre-sales assistant prototype that transforms scattered pre-sales documents into a searchable, reviewable, and business-oriented knowledge assistant.