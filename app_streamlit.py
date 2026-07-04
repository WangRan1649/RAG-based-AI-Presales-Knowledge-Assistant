import html
import json
import re
import sys
from pathlib import Path
from typing import Any

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
RAG_APP_DIR = PROJECT_ROOT / "rag_app"
TRACE_FILE = PROJECT_ROOT / "agent_workbench" / "traces" / "agent_traces.jsonl"

sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(RAG_APP_DIR))

from generate_answer_chroma import generate_chroma_answer
from trace_logger import log_user_feedback


st.set_page_config(
    page_title="AI Pre-sales Copilot",
    page_icon="馃",
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

    if "last_agent_run" not in st.session_state:
        st.session_state.last_agent_run = None


def get_agent_session_context():
    """
    Return a browser-session-scoped Agent Workbench SessionContext.

    Streamlit keeps session_state isolated per browser session, so this avoids
    cross-user memory sharing while preserving memory across clicks in one demo.
    """

    from agent_workbench.agents.session_context import SessionContext

    if "agent_session_context" not in st.session_state:
        st.session_state.agent_session_context = SessionContext()
    return st.session_state.agent_session_context


def get_agent_customer_profile() -> dict:
    """
    Read the current customer profile from the session-scoped SessionContext.
    """

    session_context = get_agent_session_context()
    state = getattr(session_context, "state", None)
    profile = getattr(state, "customer_profile", {}) if state is not None else {}
    return dict(profile or {})


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


def read_latest_trace() -> dict[str, Any] | None:
    """
    Read the latest Agent Workbench JSONL trace.
    """

    if not TRACE_FILE.exists():
        return None

    try:
        lines = [line.strip() for line in TRACE_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError:
        return None

    if not lines:
        return None

    try:
        return json.loads(lines[-1])
    except json.JSONDecodeError:
        return {"errors": ["Latest trace line is not valid JSON."], "raw_trace_preview": lines[-1][:2000]}


def compact_json(value: Any) -> str:
    """
    Convert dict/list values into readable JSON for Streamlit code blocks.
    """

    if value in (None, "", [], {}):
        return "None"
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def render_key_value_json(title: str, value: Any, expanded: bool = True) -> None:
    with st.expander(title, expanded=expanded):
        st.code(compact_json(value), language="json")


def append_email_trace_event(to: str, status: str, error: str = "") -> None:
    """
    Append a minimal email send event to the existing Agent Workbench trace log.
    """

    try:
        TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "event": "email_sent",
            "to": to,
            "status": status,
            "error": error,
        }
        with TRACE_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        return


def clear_gmail_send_state() -> None:
    """Clear Streamlit widget state for the manual Gmail send area."""

    st.session_state.gmail_recipient = ""
    st.session_state.gmail_subject = "Re: Your Inquiry"
    st.session_state.gmail_body_preview = ""
    st.session_state.gmail_body_draft_id = ""


def source_display_name(source: dict[str, Any]) -> str:
    raw_name = str(source.get("title") or source.get("source_file") or "Product Documentation")
    stem = Path(raw_name).stem
    parts = [part for part in re.split(r"[_\-\s]+", stem) if part and not part.isdigit()]
    if not parts:
        return "Product Documentation"

    labels = []
    for part in parts:
        upper = part.upper()
        if upper in {"FAQ", "API", "SLA", "HIPAA", "GDPR", "SOC2", "SOC"}:
            labels.append(upper)
        else:
            labels.append(part.capitalize())
    return " ".join(labels)


def should_show_review_warning(state: dict[str, Any]) -> bool:
    risk_decision = state.get("risk_decision", {}) or {}
    critic_decision = state.get("critic_decision", {}) or {}
    risk_level = str(risk_decision.get("risk_level", "")).lower()
    grounding_status = str(critic_decision.get("grounding_status", "")).lower()
    return bool(
        risk_decision.get("requires_human_review")
        or critic_decision.get("revision_required")
        or grounding_status in {"uncertain", "unsupported", "failed"}
        or risk_level == "high"
        or state.get("human_review_required")
    )


def customer_answer_from_email_body(email_body: str, fallback_answer: str) -> str:
    """Extract a customer-readable answer from the email body for Sales View."""

    if not email_body.strip():
        return fallback_answer

    body = email_body
    if "Source note:" in body:
        body = body.split("Source note:", 1)[0]
    if "Best regards," in body:
        body = body.split("Best regards,", 1)[0]

    lines = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line == "Hi,":
            continue
        if line.lower().startswith("thank you for your question"):
            continue
        lines.append(line)

    return "\n\n".join(lines).strip() or fallback_answer


def render_sources_table(sources: list[dict[str, Any]], show_engineering_details: bool = True) -> None:
    if not sources:
        st.info("No retrieved sources were returned for this run.")
        return

    rows = []
    if show_engineering_details:
        for source in sources:
            rows.append(
                {
                    "source_file": source.get("source_file", ""),
                    "chunk_id": source.get("chunk_id", ""),
                    "chunk_index": source.get("chunk_index", ""),
                    "similarity_score": source.get("similarity_score", ""),
                    "content_preview": source.get("content_preview", ""),
                }
            )
    else:
        seen = set()
        for source in sources:
            display_name = source_display_name(source)
            if display_name in seen:
                continue
            seen.add(display_name)
            rows.append({"Source": display_name})
            if len(rows) >= 5:
                break
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_fallback_notes(trace_data: dict[str, Any]) -> None:
    retrieval_metadata = trace_data.get("retrieval_metadata", {}) or {}
    errors = trace_data.get("errors", []) or []
    retrieval_mode = str(retrieval_metadata.get("retrieval_mode", "unknown"))
    joined_errors = " | ".join(str(error) for error in errors)

    if "markdown" in retrieval_mode or "Chroma retrieval unavailable" in joined_errors:
        st.info(
            "Chroma unavailable / Markdown fallback: this run could not use Chroma, "
            "so Retrieval Agent searched local Markdown files under knowledge_base/*.md. "
            "This is expected in lightweight portfolio environments without chromadb."
        )

    if errors:
        st.warning("Errors / fallback notes are present in this run. Review the details below before using the answer.")


def render_agent_workbench_state(state: dict[str, Any]) -> None:
    st.markdown('<div class="section-title">Agent Workbench V3.0 Portfolio View</div>', unsafe_allow_html=True)

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    risk_decision = state.get("risk_decision", {}) or {}
    critic_decision = state.get("critic_decision", {}) or {}

    with metric_col1:
        render_metric_card("Intent", str((state.get("planner_output", {}) or {}).get("intent", "unknown")))
    with metric_col2:
        render_metric_card("Risk", str(risk_decision.get("risk_level", "unknown")))
    with metric_col3:
        render_metric_card("Grounding", str(critic_decision.get("grounding_status", "unknown")))
    with metric_col4:
        render_metric_card("Human Review", str(state.get("human_review_required", False)))

    render_fallback_notes(state)

    render_card("User Question", str(state.get("user_question", "")), "card source-card")
    render_card("Final Answer", str(state.get("final_answer", "")), "card answer-card")

    left_col, right_col = st.columns(2)
    with left_col:
        render_key_value_json("Planner Output", state.get("planner_output", {}))
        render_key_value_json("Risk Decision", state.get("risk_decision", {}))
        render_key_value_json("Email Draft", state.get("email_draft", {}), expanded=False)
        render_key_value_json("Tools Called", state.get("tools_called", []), expanded=False)

    with right_col:
        render_key_value_json("Critic Decision", state.get("critic_decision", {}))
        render_key_value_json("Memory Summary", state.get("memory_summary", {}), expanded=False)
        render_key_value_json("Errors / Fallback Notes", state.get("errors", []), expanded=False)
        render_key_value_json(
            "Trace Preview",
            {
                "run_id": state.get("run_id"),
                "timestamp": state.get("timestamp"),
                "latency_ms": state.get("latency_ms"),
                "retrieval_metadata": state.get("retrieval_metadata", {}),
                "human_review_required": state.get("human_review_required", False),
            },
            expanded=False,
        )

    st.markdown('<div class="section-title">Retrieved Sources</div>', unsafe_allow_html=True)
    render_sources_table(state.get("retrieved_sources", []) or [])


def render_sales_agent_workbench_state(state: dict[str, Any]) -> None:
    """Render a customer-facing sales view without raw workflow internals."""

    st.markdown('<div class="section-title">Customer-ready Answer</div>', unsafe_allow_html=True)

    if should_show_review_warning(state):
        st.warning(
            "This answer involves sensitive information or limited source support. "
            "Please have the pre-sales or solutions owner review it before sending it to the customer."
        )
    else:
        st.success("Review status: ready for sales review.")

    email_draft = state.get("email_draft", {}) or {}
    draft_body = str(email_draft.get("body", "") or "")
    customer_answer = customer_answer_from_email_body(
        email_body=draft_body,
        fallback_answer=str(state.get("final_answer", "")),
    )

    render_card("Customer Question", str(state.get("user_question", "")), "card source-card")
    render_card("Customer-ready Answer", customer_answer, "card answer-card")

    sources = state.get("retrieved_sources", []) or []
    st.markdown('<div class="section-title">Source Summary</div>', unsafe_allow_html=True)
    render_sources_table(sources, show_engineering_details=False)

    if draft_body:
        st.markdown('<div class="section-title">Email Draft to Customer</div>', unsafe_allow_html=True)
        st.text_area(
            "Customer-facing draft",
            value=draft_body,
            height=260,
            disabled=True,
            key=f"sales_email_draft_preview_{state.get('run_id', 'latest')}",
        )


def render_gmail_send_section(state: dict[str, Any]) -> None:
    """
    Render manual Gmail send controls under the generated email draft.
    """

    email_draft = state.get("email_draft", {}) or {}
    draft_body = str(email_draft.get("body", "") or "")
    draft_subject = str(email_draft.get("subject", "") or "Re: Your Inquiry")
    internal_review_note = str(email_draft.get("internal_review_note", "") or "")

    if not draft_body.strip():
        return

    st.markdown('<div class="section-title">Manual Gmail Send</div>', unsafe_allow_html=True)

    if internal_review_note:
        st.warning(internal_review_note)

    draft_id = str(state.get("run_id") or state.get("timestamp") or "latest")
    if st.session_state.get("gmail_body_draft_id") != draft_id:
        st.session_state.gmail_body_preview = draft_body
        st.session_state.gmail_body_draft_id = draft_id

    if "gmail_subject" not in st.session_state:
        st.session_state.gmail_subject = draft_subject or "Re: Your Inquiry"
    if "gmail_recipient" not in st.session_state:
        st.session_state.gmail_recipient = ""

    recipient = st.text_input("收件人邮箱", key="gmail_recipient")
    subject = st.text_input("邮件主题", key="gmail_subject")
    edited_body = st.text_area(
        "邮件正文（可在发送前编辑）",
        key="gmail_body_preview",
        height=320,
    )

    try:
        from agent_workbench.tools import gmail_sender
    except Exception as exc:
        st.info(f"Gmail sender unavailable, draft only. {type(exc).__name__}: {exc}")
        return

    if not gmail_sender.is_gmail_configured():
        st.info("Gmail未配置，仅展示草稿")
        return

    send_col, cancel_col = st.columns([1, 1])
    with send_col:
        send_clicked = st.button("确认发送", key="gmail_confirm_send", use_container_width=True)
    with cancel_col:
        st.button("取消", key="gmail_cancel_send", use_container_width=True, on_click=clear_gmail_send_state)

    if not send_clicked:
        return

    if not recipient.strip():
        st.error("收件人邮箱不能为空。")
        return

    try:
        result = gmail_sender.send_email(
            to=recipient,
            subject=subject or draft_subject or "Re: Your Inquiry",
            body=edited_body,
            token_path="token.json",
        )
        append_email_trace_event(to=recipient, status="success", error="")
        st.success(f"邮件已发送至 {recipient}")
        with st.expander("Gmail API Result", expanded=False):
            st.json(result)
    except Exception as exc:
        error = str(exc)
        append_email_trace_event(to=recipient, status="failed", error=error)
        st.error(error)


def render_agent_workbench_tab(show_engineering_details: bool) -> None:
    if show_engineering_details:
        st.markdown(
            """
            Run the full Agent Workbench workflow: IntentClassifier, DocumentRetriever,
            RiskFilter, GroundingChecker, AnswerGenerator, EmailComposer, SessionContext.
            """
        )
    else:
        st.markdown("Generate a source-grounded answer and a customer-ready follow-up email draft.")

    session_context = get_agent_session_context()
    profile = get_agent_customer_profile()

    if show_engineering_details:
        memory_col1, memory_col2 = st.columns([3, 1])
        with memory_col1:
            with st.expander("Session Customer Profile", expanded=True):
                if profile:
                    st.json(profile)
                else:
                    st.info("No customer profile stored in this session yet.")
        with memory_col2:
            if st.button("Clear Memory", use_container_width=True):
                from agent_workbench.agents.session_context import SessionContext

                st.session_state.agent_session_context = SessionContext()
                st.session_state.last_agent_run = None
                st.success("Memory cleared for this browser session.")
                session_context = st.session_state.agent_session_context

    question = st.text_area(
        "Customer Question",
        value="Can InsightFlow support private deployment and SLA?",
        height=100,
        placeholder="Ask about product features, pricing, SLA, HIPAA, security, integration, roadmap, or customer cases.",
        key="agent_workbench_question",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        run_clicked = st.button("Run Workflow", type="primary", use_container_width=True)
    with col2:
        if show_engineering_details:
            st.caption("Each run writes a JSONL trace to agent_workbench/traces/agent_traces.jsonl.")
        else:
            st.caption("The workflow drafts a customer-ready answer and follow-up email for human review.")

    if run_clicked:
        try:
            from agent_workbench.harness.agent_orchestrator import run_agent

            with st.spinner("Running Agent Workbench workflow..."):
                state = run_agent(
                    user_question=question.strip() or "Can InsightFlow support private deployment and SLA?",
                    session_context=session_context,
                )
            st.session_state.last_agent_run = state.to_dict()
        except Exception as exc:
            st.error(f"Agent Workbench failed safely: {type(exc).__name__}: {exc}")
            st.session_state.last_agent_run = {
                "user_question": question,
                "final_answer": "Agent workflow could not complete in the current environment.",
                "errors": [f"{type(exc).__name__}: {exc}"],
                "human_review_required": True,
            }

    if run_clicked and show_engineering_details:
        updated_profile = get_agent_customer_profile()
        with st.expander("Updated Session Customer Profile", expanded=True):
            if updated_profile:
                st.json(updated_profile)
            else:
                st.info("No customer profile stored in this session yet.")

    if st.session_state.last_agent_run:
        if show_engineering_details:
            render_agent_workbench_state(st.session_state.last_agent_run)
        else:
            render_sales_agent_workbench_state(st.session_state.last_agent_run)
        render_gmail_send_section(st.session_state.last_agent_run)
    else:
        latest = read_latest_trace() if show_engineering_details else None
        if latest:
            st.info("Showing latest saved trace. Click Run Agent to generate a fresh run.")
            render_agent_workbench_state(latest)
            render_gmail_send_section(latest)


def render_trace_viewer_tab(show_engineering_details: bool) -> None:
    if not show_engineering_details:
        st.info(
            "Trace Viewer is available in Developer View. "
            "Enable engineering details in the sidebar to inspect traces."
        )
        return

    st.markdown(
        """
        Trace Viewer reads the most recent run from
        `agent_workbench/traces/agent_traces.jsonl`.
        """
    )

    latest = read_latest_trace()
    if not latest:
        st.warning("No trace found yet. Run Agent Workbench once to create agent_traces.jsonl.")
        return

    render_agent_workbench_state(latest)


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


def render_sidebar() -> bool:
    """
    Render project explanation in the sidebar.
    """

    with st.sidebar:
        st.title("AI Pre-sales Copilot")

        st.markdown(
            "AI workbench for B2B SaaS pre-sales teams to generate "
            "source-grounded answers and customer-ready email drafts."
        )

        show_engineering_details = st.toggle("显示工程技术细节", value=False)

        with st.expander("About this project", expanded=False):
            st.markdown(
                """
                **Core Capabilities**

                - Semantic retrieval with Chroma / Markdown fallback
                - Source-grounded answers
                - Risk filtering and grounding checks
                - Customer-ready email drafts
                - Manual Gmail send after human confirmation
                - Lightweight tracing and eval
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

    return show_engineering_details


def render_header() -> None:
    """
    Render page header.
    """

    st.markdown(
        """
        <div class="main-title">馃 AI Pre-sales Copilot</div>
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
        thumbs_up = st.button("馃憤 Helpful", use_container_width=True)

    with col2:
        thumbs_down = st.button("馃憥 Not helpful", use_container_width=True)

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
    show_engineering_details = render_sidebar()
    render_header()

    rag_tab, agent_tab, trace_tab = st.tabs(
        ["RAG Copilot", "Agent Workbench V3", "Trace Viewer"]
    )

    with rag_tab:
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

    with agent_tab:
        render_agent_workbench_tab(show_engineering_details=show_engineering_details)

    with trace_tab:
        render_trace_viewer_tab(show_engineering_details=show_engineering_details)


if __name__ == "__main__":
    main()

