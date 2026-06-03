import csv
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAG_APP_DIR = PROJECT_ROOT / "rag_app"

sys.path.append(str(RAG_APP_DIR))

from generate_answer_chroma import generate_chroma_answer
from retrieve_context_chroma import retrieve_relevant_chunks_chroma


EVAL_DATASET = PROJECT_ROOT / "eval" / "eval_dataset.csv"
EVAL_RESULTS = PROJECT_ROOT / "eval" / "eval_results.csv"
EVALUATION_REPORT = PROJECT_ROOT / "docs" / "evaluation_report.md"


def split_semicolon_items(value: str) -> list[str]:
    """
    Split semicolon-separated values and remove empty spaces.
    """

    if not value:
        return []

    return [item.strip() for item in value.split(";") if item.strip()]


def calculate_keyword_coverage(answer: str, expected_keywords: list[str]) -> float:
    """
    Calculate how many expected keywords appear in the generated answer.
    """

    if not expected_keywords:
        return 0.0

    answer_lower = answer.lower()

    matched = 0
    for keyword in expected_keywords:
        if keyword.lower() in answer_lower:
            matched += 1

    return round(matched / len(expected_keywords), 4)


def evaluate_one_question(row: dict) -> dict:
    """
    Evaluate one RAG question using retrieval and generated answer.
    """

    question_id = row["question_id"]
    question = row["question"]
    expected_sources = split_semicolon_items(row["expected_sources"])
    expected_keywords = split_semicolon_items(row["expected_answer_keywords"])
    should_refuse = row["should_refuse"].strip().lower() == "yes"

    retrieved_chunks = retrieve_relevant_chunks_chroma(question=question, top_k=5)
    retrieved_sources = [item["source_file"] for item in retrieved_chunks]

    retrieval_hit = any(source in retrieved_sources for source in expected_sources)

    if expected_sources:
        matched_sources = [source for source in expected_sources if source in retrieved_sources]
        source_accuracy = round(len(matched_sources) / len(expected_sources), 4)
    else:
        source_accuracy = 0.0

    answer = generate_chroma_answer(question=question, top_k=5)
    keyword_coverage = calculate_keyword_coverage(answer, expected_keywords)

    answer_lower = answer.lower()
    refused = any(
        phrase in answer_lower
        for phrase in [
            "insufficient evidence",
            "not enough information",
            "cannot determine",
            "cannot guarantee",
            "do not have enough",
            "unable to answer",
        ]
    )

    return {
        "question_id": question_id,
        "question": question,
        "expected_sources": ";".join(expected_sources),
        "retrieved_sources": ";".join(retrieved_sources),
        "retrieval_hit": retrieval_hit,
        "source_accuracy": source_accuracy,
        "answer_keyword_coverage": keyword_coverage,
        "should_refuse": should_refuse,
        "refused": refused,
    }


def write_results_csv(results: list[dict]) -> None:
    """
    Save detailed evaluation results to CSV.
    """

    EVAL_RESULTS.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "question_id",
        "question",
        "expected_sources",
        "retrieved_sources",
        "retrieval_hit",
        "source_accuracy",
        "answer_keyword_coverage",
        "should_refuse",
        "refused",
    ]

    with EVAL_RESULTS.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def write_markdown_report(results: list[dict]) -> None:
    """
    Generate a Markdown evaluation report for portfolio documentation.
    """

    total = len(results)

    retrieval_hit_count = sum(1 for item in results if item["retrieval_hit"])
    retrieval_hit_rate = round(retrieval_hit_count / total, 4) if total else 0.0

    avg_source_accuracy = round(
        sum(float(item["source_accuracy"]) for item in results) / total,
        4,
    ) if total else 0.0

    avg_keyword_coverage = round(
        sum(float(item["answer_keyword_coverage"]) for item in results) / total,
        4,
    ) if total else 0.0

    refusal_cases = [item for item in results if item["should_refuse"]]
    low_confidence_refusal_count = sum(1 for item in refusal_cases if item["refused"])

    lines = [
        "# RAG Evaluation Report",
        "",
        "## Overview",
        "",
        "This report evaluates the AI Pre-sales Copilot on a small portfolio evaluation dataset.",
        "",
        "## Metrics",
        "",
        f"- Total questions: {total}",
        f"- Retrieval hit rate: {retrieval_hit_rate}",
        f"- Average source accuracy: {avg_source_accuracy}",
        f"- Average answer keyword coverage: {avg_keyword_coverage}",
        f"- Low-confidence refusal count: {low_confidence_refusal_count}",
        "",
        "## Detailed Results",
        "",
        "| Question ID | Retrieval Hit | Source Accuracy | Keyword Coverage | Should Refuse | Refused |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for item in results:
        lines.append(
            f"| {item['question_id']} "
            f"| {item['retrieval_hit']} "
            f"| {item['source_accuracy']} "
            f"| {item['answer_keyword_coverage']} "
            f"| {item['should_refuse']} "
            f"| {item['refused']} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Retrieval hit checks whether at least one expected source appears in the top-k retrieved chunks.",
            "- Source accuracy measures how many expected source files were retrieved.",
            "- Keyword coverage is a lightweight proxy for answer completeness.",
            "- Refusal behavior is currently rule-based and should be improved with similarity thresholds and grounded refusal logic.",
        ]
    )

    EVALUATION_REPORT.parent.mkdir(parents=True, exist_ok=True)
    EVALUATION_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """
    Run the full RAG evaluation.
    """

    with EVAL_DATASET.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    results = []

    for row in rows:
        print(f"Evaluating {row['question_id']}: {row['question']}")
        result = evaluate_one_question(row)
        results.append(result)

    write_results_csv(results)
    write_markdown_report(results)

    print("\nEvaluation complete.")
    print(f"Results saved to: {EVAL_RESULTS}")
    print(f"Report saved to: {EVALUATION_REPORT}")


if __name__ == "__main__":
    main()