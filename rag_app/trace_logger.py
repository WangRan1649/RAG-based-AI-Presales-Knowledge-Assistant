import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
QUERY_LOG_FILE = LOG_DIR / "query_logs.jsonl"
USER_FEEDBACK_FILE = LOG_DIR / "user_feedback.csv"


def utc_now_iso() -> str:
    """
    Return current UTC timestamp in ISO format.
    """

    return datetime.now(timezone.utc).isoformat()


def ensure_log_dir() -> None:
    """
    Ensure logs directory exists.
    """

    LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_query_event(
    user_query: str,
    retrieved_sources: list[str],
    top_k_chunks: list[dict[str, Any]],
    similarity_scores: list[float],
    prompt_version: str,
    llm_mode: str,
    answer: str,
    confidence: str,
    latency_ms: int,
    error_message: str = "",
) -> None:
    """
    Write one query trace event to logs/query_logs.jsonl.

    JSONL is used because it is append-friendly and easy to inspect line by line.
    """

    ensure_log_dir()

    event = {
        "timestamp": utc_now_iso(),
        "user_query": user_query,
        "retrieved_sources": retrieved_sources,
        "top_k_chunks": top_k_chunks,
        "similarity_scores": similarity_scores,
        "prompt_version": prompt_version,
        "llm_mode": llm_mode,
        "answer": answer,
        "confidence": confidence,
        "latency_ms": latency_ms,
        "error_message": error_message,
    }

    with QUERY_LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")


def ensure_feedback_file() -> None:
    """
    Create logs/user_feedback.csv with headers if it does not exist.
    """

    ensure_log_dir()

    if USER_FEEDBACK_FILE.exists():
        return

    with USER_FEEDBACK_FILE.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "user_query",
                "feedback",
                "comment",
                "answer_preview",
            ],
        )
        writer.writeheader()


def log_user_feedback(
    user_query: str,
    feedback: str,
    comment: str = "",
    answer_preview: str = "",
) -> None:
    """
    Append one user feedback record to logs/user_feedback.csv.
    """

    ensure_feedback_file()

    with USER_FEEDBACK_FILE.open("a", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "user_query",
                "feedback",
                "comment",
                "answer_preview",
            ],
        )
        writer.writerow(
            {
                "timestamp": utc_now_iso(),
                "user_query": user_query,
                "feedback": feedback,
                "comment": comment,
                "answer_preview": answer_preview[:300],
            }
        )


if __name__ == "__main__":
    sample_chunks = [
        {
            "rank": 1,
            "source_file": "04_deployment_guide.md",
            "chunk_id": "chunk_0001",
            "chunk_index": 1,
            "similarity_score": 0.52,
        }
    ]

    log_query_event(
        user_query="Can InsightFlow AI support private deployment?",
        retrieved_sources=["04_deployment_guide.md"],
        top_k_chunks=sample_chunks,
        similarity_scores=[0.52],
        prompt_version="v1_grounded_presales_prompt",
        llm_mode="mock",
        answer="Sample answer for tracing test.",
        confidence="medium",
        latency_ms=123,
        error_message="",
    )

    log_user_feedback(
        user_query="Can InsightFlow AI support private deployment?",
        feedback="thumbs_up",
        comment="Sample feedback record.",
        answer_preview="Sample answer for tracing test.",
    )

    print(f"Query log written to: {QUERY_LOG_FILE}")
    print(f"Feedback log written to: {USER_FEEDBACK_FILE}")