# RAG v2 Interview Pitch

One of my recent projects is a RAG-based AI Pre-sales Knowledge Assistant.

The business problem is that in many B2B software companies, pre-sales knowledge is scattered across product documents, FAQs, pricing notes, deployment guides, integration documents, security materials, case studies, and email templates. When a customer asks a question, a sales or pre-sales consultant often needs to manually search these documents, rewrite the answer, and confirm details with technical teams. This is slow, inconsistent, and may create the risk of over-promising.

To solve this problem, I built a RAG-style knowledge assistant for pre-sales scenarios.

In the first version, I implemented a fully local prototype. I used Python to load Markdown documents, split them into overlapping chunks, and apply TF-IDF retrieval to find relevant knowledge snippets. The system then generated a structured pre-sales response with direct answer, supporting evidence, suggested customer-facing response, human review reminder, and source citations.

After validating the workflow, I upgraded the retrieval layer to a semantic search version. I used sentence-transformers to convert document chunks into embeddings and stored them in a local Chroma vector database. When a user asks a question, the question is also converted into an embedding, and Chroma retrieves the most semantically similar chunks.

This upgrade allows the assistant to retrieve relevant information even when the customer does not use the exact same keywords as the source documents. For example, a question about a “reporting dashboard and database” can still retrieve knowledge related to Power BI and MySQL integration.

The current version still uses template-based answer generation, but the architecture is modular. The retrieval layer, answer generation layer, and interface layer are separated, so the next step is to replace the template generation with an LLM API such as OpenAI, Gemini, Claude, or a local LLM.

This project demonstrates my understanding of practical AI application development: knowledge base construction, chunking, embedding-based retrieval, vector database integration, source grounding, and human-in-the-loop review for real pre-sales business scenarios.