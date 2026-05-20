# InsightFlow AI — Security and Governance

## Governance Principle
AI-generated content should be treated as a draft. Final customer communication and business decisions must be reviewed by a human.

## Sensitive Data Handling
Before ingestion, teams should mask or remove:
- Customer names
- Emails and phone numbers
- Payment information
- API keys and credentials
- Private contract terms
- Internal financial projections

## Hallucination Control
Recommended controls:
1. Retrieve relevant source chunks before generation.
2. Instruct the LLM to answer only from retrieved context.
3. Include source references.
4. Add a human review status.
5. Build an evaluation set with expected answers.
6. Track unsupported or incorrect answers.

## Review Status
- Pending human review
- Approved
- Needs revision
- Rejected

## Prompt Safety Rules
The assistant should not invent product features, pricing, security guarantees, or legal commitments. If information is missing, it should say that the knowledge base does not contain enough evidence.
