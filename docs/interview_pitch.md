# Interview Pitch — RAG-based AI Pre-sales Knowledge Assistant

## 90-second English Pitch

One of my recent projects is a RAG-based AI Pre-sales Knowledge Assistant.

The business problem behind this project is that in many B2B software companies, pre-sales knowledge is scattered across product documents, FAQ files, deployment guides, pricing notes, security policies, integration documents, customer case studies, and email templates.

Traditionally, when a customer asks a question, a sales or pre-sales consultant has to manually search through these documents, copy relevant information, rewrite the answer, and sometimes confirm details with the technical team. This process is slow, inconsistent, and may create the risk of over-promising.

So I built a local RAG-style assistant to improve this workflow.

In the current version, I first prepared a structured pre-sales knowledge base in Markdown format. Then I used Python to load the documents and split them into smaller overlapping chunks. Each chunk keeps metadata such as source file, chunk ID, and chunk index.

For retrieval, I implemented a local TF-IDF based search module using scikit-learn. When a user asks a question, the system compares the question with all document chunks and retrieves the most relevant context. Then the answer generation module creates a structured pre-sales response, including a direct answer, supporting evidence, suggested customer-facing response, human review reminder, and source citations.

The current version does not rely on external LLM APIs, which makes it stable, free, and easy to demonstrate. But the architecture is modular. The retrieval layer can be upgraded to embeddings plus FAISS or Chroma, and the template-based answer generation layer can be replaced by OpenAI, Gemini, Claude, or a local LLM.

This project shows my understanding of practical AI application development: not just using a chatbot, but designing a grounded, source-traceable, human-reviewable workflow for a real pre-sales business scenario.

## Common Interview Questions

### Q1: Why did you use TF-IDF instead of embeddings?

I used TF-IDF in the first version because I wanted to build a stable local prototype that can run without API keys, cost, or network dependency.

The goal of this version is to demonstrate the core RAG workflow clearly: document loading, chunking, retrieval, answer generation, source citation, and human review.

The project is designed modularly, so the TF-IDF retrieval layer can be upgraded to embedding-based retrieval with FAISS, Chroma, or a cloud vector database later.

### Q2: Is this a real RAG system if it does not use an LLM yet?

It is a local RAG-style prototype rather than a full production RAG system.

The core RAG structure is already there: the system retrieves relevant context from an external knowledge base before generating an answer. The current answer generation is template-based, but the generation layer is separated and can be replaced by a real LLM API.

So this version demonstrates the workflow and architecture, while leaving a clear path for production upgrade.

### Q3: How do you reduce hallucination risk?

I reduce hallucination risk in three ways.

First, the assistant retrieves relevant context from a controlled knowledge base instead of answering from model memory only.

Second, every answer includes supporting evidence and source citations, such as the source file and chunk ID.

Third, the system includes a human review reminder. A pre-sales or solution consultant must verify technical feasibility, pricing details, deployment constraints, and client-specific assumptions before sending the answer externally.

### Q4: How is this project relevant to AI pre-sales or AI solutions roles?

This project is relevant because AI pre-sales and solution roles often need to translate scattered product knowledge into accurate client-facing answers.

The project demonstrates my ability to understand business pain points, build a lightweight AI workflow, organize knowledge documents, implement retrieval logic, generate structured answers, and design human review mechanisms.

It is not just a chatbot demo. It is a practical knowledge assistant workflow for pre-sales scenarios.

### Q5: How would you upgrade this project?

I would upgrade it in four steps.

First, replace TF-IDF with embedding-based retrieval using FAISS or Chroma.

Second, replace template-based answer generation with an LLM API such as OpenAI, Gemini, Claude, or a local LLM.

Third, add an evaluation dataset to measure answer relevance, source grounding, and business usability.

Fourth, build a simple Streamlit or FastAPI interface so business users can interact with the assistant more easily.