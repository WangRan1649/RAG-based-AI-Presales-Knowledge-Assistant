import html
import re
import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
RAG_APP_DIR = PROJECT_ROOT / "rag_app"

sys.path.append(str(RAG_APP_DIR))

from generate_answer_chroma import generate_chroma_answer
from trace_logger import log_user_feedback


st.set_page_config(
    page_title="AI Pre-sales Copilot",
    page_icon="🤖",
    layout="wide",
)


def inject_custom_css() -> None:
    """
    Add custom CSS to make the Streamlit demo visually consistent.
    """

    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            font-family: "Segoe UI", "Inter", "Arial", sans-serif;
        }

        .main-title {
            font-size: 34px;
            font-weight: 750;
            line-height: 1.2;
            margin-bottom: 6px;
        }

        .subtitle {
            font-size: 16px;
            color: #5f6b7a;
            margin-bottom: 22px;
        }

        .section-title {
            font-size: 21px;
            font-weight: 700;
            margin-top: 24px;
            margin-bottom: 10px;
        }

        .card {
            border: 1px solid #e6eaf0;
            border-radius: 14px;
            padding: 18px 20px;
            margin: 12px 0;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
        }

        .answer-card {
            border-left: 5px solid #2563eb;
        }

        .warning-card {
            border-left: 5px solid #f59e0b;
            background: #fffbeb;
        }

        .source-card {
            border-left: 5px solid #64748b;
            background: #f8fafc;
        }

        .metric-card {
            border: 1px solid #e6eaf0;
            border-radius: 14px;
            padding: 14px 16px;
            background: #f8fafc;
            min-height: 92px;
        }

        .metric-label {
            font-size: 13px;
            color: #64748b;
            margin-bottom: 6px;
        }

        .metric-value {
            font-size: 20px;
            font-weight: 700;
            color: #0f172a;
        }

        .normal-text {
            font-size: 15.5px;
            line-height: 1.65;
            color: #1f2937;
        }

        .small-muted {
            font-size: 13px;
            color: #64748b;
            line-height: 1.5;
        }

        .mono-block {
            font-family: "Consolas", "Courier New", monospace;
            font-size: 13px;
            line-height: 1.5;
            white-space: pre-wrap;
            word-break: break-word;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 14px;
        }

        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li {
            font-size: 15.5px;
            line-height: 1.65;
        }

        div[data-testid="stTextArea"] textarea {
            font-size: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_session_state() -> None:
    """
    Initialize Streamlit session state variables.
    """

    if "last_question" not in st.session_state:
        st.session_state.last_question = ""

    if "last_answer" not in st.session_state:
        st.session_state.last_answer = ""

    if "feedback_submitted" not in st.session_state:
        st.session_state.feedback_submitted = False


def extract_section(markdown_text: str, heading: str) -> str:
    """
    Extract content under a Markdown level-2 heading.

    Example:
    ## Answer
    content...
    ## Sources
    """

    pattern = rf"## {re.escape(heading)}\n\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, markdown_text, flags=re.DOTALL)

    if not match:
        return ""

    return match.group(1).strip()


def clean_markdown_text(text: str) -> str:
    """
    Clean markdown text so nested headings from retrieved source documents
    do not create inconsistent font sizes in the Streamlit UI.
    """

    if not text:
        return ""

    cleaned = text.replace("### ", "")
    cleaned = cleaned.replace("## ", "")
    cleaned = cleaned.replace("# ", "")
    cleaned = cleaned.replace("**", "")
    cleaned = cleaned.strip()

    return cleaned


def render_card(title: str, content: str, card_class: str = "card") -> None:
    """
    Render a consistent card block.
    """

    safe_title = html.escape(title)
    safe_content = html.escape(clean_markdown_text(content)).replace("\n", "<br>")

    st.markdown(
        f"""
        <div class="{card_class}">
            <div class="section-title">{safe_title}</div>
            <div class="normal-text">{safe_content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str) -> None:
    """
    Render a small metric card.
    """

    safe_label = html.escape(label)
    safe_value = html.escape(value)

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{safe_label}</div>
            <div class="metric-value">{safe_value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def parse_confidence(confidence_text: str) -> tuple[str, str]:
    """
    Parse retrieval confidence and LLM confidence from the generated answer.
    """

    retrieval_confidence = "unknown"
    llm_confidence = "unknown"

    retrieval_match = re.search(r"Retrieval confidence:\s*([A-Za-z_]+)", confidence_text)
    llm_match = re.search(r"LLM confidence:\s*([A-Za-z_]+)", confidence_text)

    if retrieval_match:
        retrieval_confidence = retrieval_match.group(1)

    if llm_match:
        llm_confidence = llm_match.group(1)

    return retrieval_confidence, llm_confidence


def parse_sources(sources_text: str) -> list[dict]:
    """
    Parse source lines into structured rows.
    """

    rows = []

    for line in sources_text.splitlines():
        line = line.strip()

        if not line.startswith("- "):
            continue

        line = line[2:]
        parts = [part.strip() for part in line.split("|")]

        source_file = parts[0] if len(parts) > 0 else ""
        chunk_id = parts[1] if len(parts) > 1 else ""
        chunk_index = parts[2] if len(parts) > 2 else ""
        similarity = parts[3] if len(parts) > 3 else ""

        rows.append(
            {
                "source_file": source_file,
                "chunk_id": chunk_id,
                "chunk_index": chunk_index,
                "similarity": similarity,
            }
        )

    return rows


def render_sidebar() -> None:
    """
    Render project explanation in the sidebar.
    """

    with st.sidebar:
        st.title("AI Pre-sales Copilot")

        st.markdown(
            """
            **Project Positioning**

            A RAG-based AI copilot for B2B SaaS pre-sales scenarios.

            **Core Capabilities**

            - Semantic retrieval with Chroma
            - Mock/API LLM client
            - Source-grounded answers
            - Confidence display
            - Hallucination guardrails
            - Lightweight tracing
            - User feedback logging
            """
        )

        st.divider()

        st.markdown(
            """
            **Best Test Questions**

            - Can InsightFlow AI support private deployment?
            - How does the assistant reduce hallucinations?
            - Can InsightFlow AI connect to MySQL and Power BI?
            - What pricing plans are available?
            - Can InsightFlow AI guarantee stock trading profits?
            """
        )


def render_header() -> None:
    """
    Render page header.
    """

    st.markdown(
        """
        <div class="main-title">🤖 AI Pre-sales Copilot</div>
        <div class="subtitle">RAG + LLM Client + Evaluation + Guardrails + Lightweight Tracing</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        This demo helps pre-sales and solution teams answer customer questions
        based on a product knowledge base. The answer includes source grounding,
        confidence information, missing information, and suggested follow-up.
        """
    )


def render_structured_answer(answer: str) -> None:
    """
    Render generated answer with consistent visual hierarchy.
    """

    question = extract_section(answer, "Question")
    intent = extract_section(answer, "Detected Intent")
    llm_mode = extract_section(answer, "LLM Mode")
    confidence = extract_section(answer, "Confidence")
    answer_text = extract_section(answer, "Answer")
    missing_info = extract_section(answer, "Missing Information")
    suggested_follow_up = extract_section(answer, "Suggested Follow-up")
    supporting_evidence = extract_section(answer, "Supporting Evidence from Knowledge Base")
    sources = extract_section(answer, "Sources")
    human_review = extract_section(answer, "Human Review Reminder")

    retrieval_confidence, llm_confidence = parse_confidence(confidence)

    st.markdown('<div class="section-title">AI Answer</div>', unsafe_allow_html=True)

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        render_metric_card("Detected Intent", intent or "unknown")

    with metric_col2:
        render_metric_card("LLM Mode", llm_mode or "unknown")

    with metric_col3:
        render_metric_card("Confidence", f"Retrieval: {retrieval_confidence} / LLM: {llm_confidence}")

    if "rule_based_refusal" in llm_mode:
        render_card("Answer", answer_text, "card warning-card")
    else:
        render_card("Answer", answer_text, "card answer-card")

    if missing_info:
        render_card("Missing Information", missing_info)

    if suggested_follow_up:
        render_card("Suggested Follow-up", suggested_follow_up)

    source_rows = parse_sources(sources)

    if source_rows:
        st.markdown('<div class="section-title">Sources</div>', unsafe_allow_html=True)
        st.dataframe(source_rows, use_container_width=True, hide_index=True)

    if supporting_evidence:
        with st.expander("View Retrieved Chunks / Supporting Evidence", expanded=False):
            st.markdown(
                f"""
                <div class="mono-block">{html.escape(clean_markdown_text(supporting_evidence))}</div>
                """,
                unsafe_allow_html=True,
            )

    if human_review:
        render_card("Human Review Reminder", human_review, "card source-card")

    with st.expander("View Raw Markdown Answer", expanded=False):
        st.code(answer, language="markdown")


def render_answer(question: str) -> None:
    """
    Generate and render an AI answer.
    """

    with st.spinner("Retrieving knowledge base chunks and generating answer..."):
        answer = generate_chroma_answer(question=question, top_k=5)

    st.session_state.last_question = question
    st.session_state.last_answer = answer
    st.session_state.feedback_submitted = False

    render_structured_answer(answer)


def render_feedback_section() -> None:
    """
    Render user feedback controls.
    """

    if not st.session_state.last_answer:
        return

    st.divider()
    st.markdown('<div class="section-title">Feedback</div>', unsafe_allow_html=True)

    st.markdown(
        "Was this answer useful? Your feedback will be saved locally to `logs/user_feedback.csv`."
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        thumbs_up = st.button("👍 Helpful", use_container_width=True)

    with col2:
        thumbs_down = st.button("👎 Not helpful", use_container_width=True)

    comment = st.text_input(
        "Optional comment",
        placeholder="Example: source was relevant, but answer missed pricing details",
    )

    if thumbs_up:
        log_user_feedback(
            user_query=st.session_state.last_question,
            feedback="thumbs_up",
            comment=comment,
            answer_preview=st.session_state.last_answer,
        )
        st.session_state.feedback_submitted = True
        st.success("Feedback saved: thumbs_up")

    if thumbs_down:
        log_user_feedback(
            user_query=st.session_state.last_question,
            feedback="thumbs_down",
            comment=comment,
            answer_preview=st.session_state.last_answer,
        )
        st.session_state.feedback_submitted = True
        st.warning("Feedback saved: thumbs_down")

    if st.session_state.feedback_submitted:
        st.info("Feedback has been recorded locally.")


def main() -> None:
    """
    Streamlit entry point.
    """

    initialize_session_state()
    inject_custom_css()
    render_sidebar()
    render_header()

    question = st.text_area(
        "Customer question",
        value="Can InsightFlow AI support private deployment?",
        height=100,
        placeholder="Enter a customer question about deployment, security, pricing, integrations, or product capabilities.",
    )

    col1, col2 = st.columns([1, 5])

    with col1:
        ask_clicked = st.button("Ask Copilot", type="primary", use_container_width=True)

    with col2:
        st.caption("The system retrieves relevant knowledge base chunks before generating an answer.")

    if ask_clicked:
        cleaned_question = question.strip()

        if not cleaned_question:
            st.error("Please enter a valid question.")
        else:
            render_answer(cleaned_question)

    render_feedback_section()


if __name__ == "__main__":
    main()