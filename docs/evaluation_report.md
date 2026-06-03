# RAG Evaluation Report

## Overview

This report evaluates the AI Pre-sales Copilot on a small portfolio evaluation dataset.

## Metrics

- Total questions: 11
- Retrieval hit rate: 0.7273
- Average source accuracy: 0.6818
- Average answer keyword coverage: 0.7273
- Low-confidence refusal count: 0

## Detailed Results

| Question ID | Retrieval Hit | Source Accuracy | Keyword Coverage | Should Refuse | Refused |
|---|---:|---:|---:|---:|---:|
| Q001 | True | 0.5 | 1.0 | False | False |
| Q002 | True | 1.0 | 1.0 | False | False |
| Q003 | True | 1.0 | 1.0 | False | False |
| Q004 | True | 1.0 | 1.0 | False | False |
| Q005 | True | 1.0 | 1.0 | False | False |
| Q006 | True | 1.0 | 0.3333 | False | False |
| Q007 | True | 1.0 | 0.3333 | False | False |
| Q008 | False | 0.0 | 0.0 | False | False |
| Q009 | True | 1.0 | 1.0 | False | False |
| Q010 | False | 0.0 | 1.0 | False | False |
| Q011 | False | 0.0 | 0.3333 | True | False |

## Notes

- Retrieval hit checks whether at least one expected source appears in the top-k retrieved chunks.
- Source accuracy measures how many expected source files were retrieved.
- Keyword coverage is a lightweight proxy for answer completeness.
- Refusal behavior is currently rule-based and should be improved with similarity thresholds and grounded refusal logic.