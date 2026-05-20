# InsightFlow AI — Integrations and API

## Supported Data Sources
Local demo:
- Markdown
- TXT
- CSV

Business prototype:
- MySQL
- PostgreSQL
- Google Sheets exports
- Power BI exported CSV
- Internal document folders

## MySQL Integration
MySQL can be used as an operational data source. Example input tables:
- users
- orders
- products
- customers
- support_tickets
- sales_questions
- document_metadata

Example output tables:
- rag_answers
- retrieved_contexts
- review_logs
- ai_recommendations

## Power BI Integration
Power BI can consume AI outputs through CSV export or database table connection.

Recommended output fields:
- answer_id
- question
- direct_answer
- suggested_response
- source_document
- review_status
- created_at

## API Design

### POST /ask
Input:
```json
{
  "question": "Can the product connect to MySQL and Power BI?",
  "user_role": "pre_sales",
  "language": "English"
}
```

Output:
```json
{
  "direct_answer": "Yes, the product can connect to MySQL and Power BI.",
  "suggested_response": "The recommended setup is to use MySQL as the operational data source and Power BI as the visualization layer.",
  "sources": ["04_deployment_guide.md", "06_integrations_and_api.md"],
  "review_status": "Pending human review"
}
```
