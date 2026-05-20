# RAG v2 Project Summary

## Project Name

RAG-based AI Pre-sales Knowledge Assistant

## Project Positioning

This project is a RAG-based AI pre-sales assistant designed for B2B software solution scenarios.

It transforms static pre-sales materials into a searchable knowledge base and supports semantic retrieval, structured answer generation, source citation, and human review.

---

## Business Problem

In B2B software companies, product and solution knowledge is often scattered across:

- Product overview documents
- FAQ files
- Pricing notes
- Deployment guides
- Security and governance materials
- Integration documents
- Customer case studies
- Email templates

Traditional pre-sales teams need to manually search documents, copy information, rewrite customer-facing answers, and confirm details with technical teams.

This creates problems such as:

- Slow response speed
- Inconsistent answers
- Over-reliance on senior consultants
- Risk of over-promising to customers
- Difficulty tracing answer sources

---

## RAG v1

The first version uses a fully local workflow:

```text
Markdown documents
→ chunks
→ TF-IDF retrieval
→ template-based answer
→ source citation
```

The purpose of v1 is to validate the core RAG workflow without relying on external APIs, LLMs, embeddings, or vector databases.

---

## RAG v2

The second version upgrades the retrieval layer to semantic retrieval:

```text
Markdown documents
→ chunks
→ sentence-transformers embeddings
→ Chroma vector store
→ semantic retrieval
→ template-based answer
→ source citation
```

In v2, each document chunk is converted into a dense embedding vector and stored in a local Chroma vector database.

When the user asks a question, the question is also converted into an embedding. Chroma then retrieves the most semantically similar chunks.

This allows the system to retrieve relevant information even when the user does not use the exact same keywords as the original documents.

For example, a user may ask:

```text
Can InsightFlow AI work with our reporting dashboard and database?
```

Even if the original documents use terms such as:

```text
Power BI integration
MySQL integration
BI dashboard workflow
API-based system integration
```

the embedding-based retrieval layer can still retrieve semantically relevant knowledge chunks.

---

## Key Technical Components

| Module | Function |
|---|---|
| `load_documents.py` | Loads Markdown knowledge documents |
| `chunk_documents.py` | Splits long documents into overlapping chunks |
| `embedding_client.py` | Converts texts into embeddings using sentence-transformers |
| `build_vector_store.py` | Builds the Chroma local vector store |
| `retrieve_context.py` | Performs TF-IDF retrieval for RAG v1 |
| `retrieve_context_chroma.py` | Performs Chroma semantic retrieval for RAG v2 |
| `generate_answer.py` | Generates template-based answers using TF-IDF retrieval |
| `generate_answer_chroma.py` | Generates template-based answers using Chroma retrieval |
| `main.py` | Interactive CLI for RAG v1 |
| `main_chroma.py` | Interactive CLI for RAG v2 |

---

## Why This Project Matters

This project demonstrates more than basic chatbot usage.

It shows the ability to design an AI application workflow with:

- Knowledge base construction
- Text chunking
- Embedding-based semantic retrieval
- Local vector database integration
- Source citation
- Human-in-the-loop review
- Business-oriented pre-sales response generation
- Modular upgrade path from prototype to production

The project is designed around a practical AI solution principle:

```text
Do not let the model answer from memory only.
Retrieve grounded context first, then generate a reviewable answer.
```

---

## Current Limitation

The current v2 version still uses template-based answer generation.

It does not yet call a real LLM API.

This is intentional because the project first focuses on building a reliable RAG retrieval backbone. The answer generation layer can later be upgraded to OpenAI, Gemini, Claude, or a local LLM.

Current version:

```text
Embedding-based retrieval is implemented.
LLM-based generation is reserved for the next upgrade.
```

---

## Future Upgrade

Future RAG v3 can include:

```text
RAG retrieval
→ LLM-generated answer
→ intent detection
→ customer-facing email draft
→ follow-up recommendation
→ evaluation
→ human review
```

Potential upgrades include:

- OpenAI / Gemini / Claude API integration
- Local LLM through Ollama
- Streamlit web interface
- FastAPI backend
- Evaluation dataset and scoring
- LLM-based intent classification
- Automatic pre-sales email generation
- Follow-up action recommendation

---

## Interview Talking Point

This project is not a static FAQ chatbot.

It is a RAG-based pre-sales knowledge assistant that transforms scattered product documents into a searchable knowledge base, retrieves semantically relevant context through embeddings and Chroma, and generates structured, source-grounded, human-reviewable pre-sales responses.

The key technical evolution is:

```text
RAG v1:
TF-IDF keyword retrieval

RAG v2:
Embedding-based semantic retrieval with Chroma

RAG v3:
LLM-powered pre-sales agent with email drafting and follow-up recommendations
```