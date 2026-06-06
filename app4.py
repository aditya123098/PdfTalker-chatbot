import streamlit as st
from utils import loader, chunker, vectorstore, final_chain
import tempfile
import time
import re
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ponder · PDF Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css">

<style>
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }

/* App background */
.stApp { background: #0f1124 !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #1a1a2e !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.07) !important;
    color: rgba(255,255,255,0.7) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    padding: 0.45rem 1rem !important;
    width: 100% !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 400 !important;
    transition: all 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.12) !important;
    color: #fff !important;
}
[data-testid="stSidebar"] [data-testid="metric-container"] {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 8px !important;
    padding: 10px !important;
    border: none !important;
}
[data-testid="stSidebar"] [data-testid="metric-container"] label {
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: rgba(255,255,255,0.4) !important;
}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 600 !important;
    color: #c9a84c !important;
}

/* ── Main block ── */
.main .block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }

/* ── Cards ── */
.ponder-card {
    background: #1a1d35;
    border: 1px solid #2a2e4a;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
}
.ponder-card.success-card {
    background: #172a1e;
    border: 1.5px solid #2d6a3f;
}
.ponder-card-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.3);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Page heading ── */
.ponder-heading {
    font-family: 'Instrument Serif', serif !important;
    font-size: 26px !important;
    font-weight: 400 !important;
    font-style: italic !important;
    color: #ffffff !important;
    line-height: 1.2 !important;
    margin-bottom: 0.2rem !important;
}
.ponder-sub { font-size: 13px; color: rgba(255,255,255,0.4); margin-bottom: 1.5rem; }

/* ── File info strip ── */
.file-strip {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px;
    background: #232640;
    border: 1px solid #2e3358;
    border-radius: 10px;
    margin-top: 0.75rem;
}
.file-icon-box {
    width: 40px; height: 40px;
    background: #c9a84c;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    color: #1a1a2e; font-size: 20px;
}
.file-name { font-size: 14px; font-weight: 500; color: #fff; }
.file-meta { font-size: 11px; color: rgba(255,255,255,0.4); margin-top: 2px; }
.ready-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(201,168,76,0.15); color: #c9a84c;
    font-size: 11px; font-weight: 500;
    padding: 4px 11px; border-radius: 20px;
    border: 1px solid rgba(201,168,76,0.3);
    margin-left: auto; white-space: nowrap;
}
.ready-dot { width: 7px; height: 7px; border-radius: 50%; background: #c9a84c; display:inline-block; }

/* ── Processing pipeline ── */
.pipeline {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: #2a2e4a;
    border: 1px solid #2a2e4a;
    border-radius: 10px;
    overflow: hidden;
    margin: 1rem 0 0.6rem;
}
.pipe-step { background: #1e2138; padding: 14px 10px; text-align: center; }
.pipe-step.done  { background: #162318; }
.pipe-step.active { background: #231f10; }
.pipe-icon {
    width: 34px; height: 34px; border-radius: 50%;
    margin: 0 auto 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px;
}
.pipe-step.done  .pipe-icon { background: rgba(99,153,34,0.2); color: #8fc94a; }
.pipe-step.active .pipe-icon { background: rgba(201,168,76,0.2); color: #c9a84c; }
.pipe-step.pending .pipe-icon { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.2); }
.pipe-step-name { font-size: 11px; font-weight: 500; margin-bottom: 2px; }
.pipe-step.done  .pipe-step-name { color: #8fc94a; }
.pipe-step.active .pipe-step-name { color: #c9a84c; }
.pipe-step.pending .pipe-step-name { color: rgba(255,255,255,0.2); }
.pipe-step-detail { font-size: 10px; }
.pipe-step.done  .pipe-step-detail { color: rgba(143,201,74,0.7); }
.pipe-step.active .pipe-step-detail { color: rgba(201,168,76,0.7); }
.pipe-step.pending .pipe-step-detail { color: rgba(255,255,255,0.15); }

/* ── Progress bar ── */
.prog-wrap { height: 4px; background: rgba(255,255,255,0.08); border-radius: 2px; overflow: hidden; margin: 0 0 5px; }
.prog-bar  { height: 100%; background: #c9a84c; border-radius: 2px; transition: width 0.4s; }
.prog-row  { display: flex; justify-content: space-between; font-size: 12px; color: rgba(255,255,255,0.35); padding: 0 1px; }
.prog-pct  { color: #c9a84c; font-weight: 500; }

/* ── Spinner ── */
@keyframes spin { to { transform: rotate(360deg); } }
.spinner {
    display: inline-block; width: 11px; height: 11px;
    border: 2px solid #e5e2da; border-top-color: #c9a84c;
    border-radius: 50%; animation: spin 0.8s linear infinite;
    margin-right: 5px; vertical-align: middle;
}

/* ── Success state ── */
.success-banner {
    display: flex; align-items: center; justify-content: space-between;
    gap: 10px;
}
.success-title {
    font-size: 15px; font-weight: 500; color: #8fc94a;
    display: flex; align-items: center; gap: 8px;
}
.success-title i { font-size: 18px; color: #8fc94a; }
.success-meta { font-size: 12px; color: rgba(143,201,74,0.7); margin-top: 3px; margin-left: 26px; }
.success-time { font-size: 11px; color: rgba(255,255,255,0.25); white-space: nowrap; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border: 1.5px dashed #2a2e4a !important;
    border-radius: 10px !important;
    background: #1e2138 !important;
    padding: 1.5rem !important;
}
[data-testid="stFileUploader"]:hover { border-color: #c9a84c !important; }
[data-testid="stFileUploader"] label { font-size: 13px !important; color: rgba(255,255,255,0.45) !important; }
[data-testid="stFileUploader"] small { color: rgba(255,255,255,0.2) !important; }

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: #1a1a2e !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stButton > button[kind="primary"]:hover {
    background: #2a2a4e !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #2a2e4a !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    color: rgba(255,255,255,0.55) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 400 !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #c9a84c !important;
    color: #c9a84c !important;
}

/* ── Textarea ── */
.stTextArea textarea {
    background: #232640 !important;
    border: 1px solid #2a2e4a !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 12px !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: #c9a84c !important;
    background: #1e2138 !important;
    box-shadow: none !important;
}
.stTextArea textarea::placeholder { color: rgba(255,255,255,0.25) !important; }

/* ── Alerts ── */
.stSuccess { background: #e0f0f0 !important; color: #0d6e6e !important; border: 1px solid #b2d8d8 !important; border-radius: 8px !important; font-size: 13px !important; }
.stError   { background: #faeaea !important; color: #b94040 !important; border: 1px solid #e5b8b8 !important; border-radius: 8px !important; font-size: 13px !important; }
.stWarning { background: #f5edd8 !important; color: #8a6120 !important; border: 1px solid #e8d9b0 !important; border-radius: 8px !important; font-size: 13px !important; }
.stInfo    { background: #f0f4ff !important; color: #2a3a8a !important; border-radius: 8px !important; border-left: 3px solid #4a6adc !important; font-size: 13px !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #1e2138 !important;
    border: 1px solid #2a2e4a !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary { font-size: 13px !important; font-weight: 500 !important; color: rgba(255,255,255,0.7) !important; padding: 0.75rem 1rem !important; }
[data-testid="stExpander"] summary:hover { background: #232640 !important; }
[data-testid="stExpander"] > div > div { padding: 0 1rem 1rem !important; font-size: 13px !important; line-height: 1.6 !important; color: rgba(255,255,255,0.6) !important; }

/* ── Checkbox ── */
[data-testid="stCheckbox"] label { font-size: 13px !important; color: rgba(255,255,255,0.7) !important; }

/* ── Answer block ── */
.answer-block {
    background: #232640;
    border: 1px solid #2a2e4a;
    border-left: 3px solid #c9a84c;
    border-radius: 0 8px 8px 0;
    padding: 1.25rem 1.5rem;
    font-size: 14px;
    line-height: 1.7;
    color: rgba(255,255,255,0.85);
    margin-top: 0.75rem;
}
.answer-label {
    font-size: 10px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.1em;
    color: #c9a84c; margin-bottom: 6px;
}

/* ── Streamlit progress (fallback) ── */
.stProgress > div > div > div { background: #c9a84c !important; height: 3px !important; border-radius: 2px !important; }
.stProgress > div > div { background: #efede8 !important; height: 3px !important; border-radius: 2px !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
STEPS = [
    ("ti-file-text", "Load",   "Reading pages"),
    ("ti-scissors",  "Chunk",  "Splitting text"),
    ("ti-vector",    "Embed",  "Creating vectors"),
    ("ti-database",  "Index",  "Building store"),
]

def render_pipeline(current_step: int, details: dict):
    """Render a 4-step processing pipeline. current_step is 0-based (0=loading, 3=done)."""
    steps_html = ""
    for i, (icon, name, sub) in enumerate(STEPS):
        detail = details.get(i, sub)
        if i < current_step:
            cls = "done"
            icon_html = f'<i class="ti ti-check" aria-hidden="true"></i>'
        elif i == current_step:
            cls = "active"
            icon_html = f'<i class="ti {icon}" aria-hidden="true"></i>'
        else:
            cls = "pending"
            icon_html = f'<i class="ti {icon}" aria-hidden="true"></i>'
        steps_html += f"""
        <div class="pipe-step {cls}">
            <div class="pipe-icon">{icon_html}</div>
            <div class="pipe-step-name">{name}</div>
            <div class="pipe-step-detail">{detail}</div>
        </div>"""

    done_all = current_step >= len(STEPS)
    pct = 100 if done_all else int((current_step / len(STEPS)) * 100)
    if done_all:
        label = '<i class="ti ti-circle-check" style="color:#639922;vertical-align:middle;margin-right:5px"></i>All steps complete'
    else:
        label = f'<span class="spinner"></span>Step {current_step + 1} of {len(STEPS)} — {STEPS[current_step][1]}'

    st.markdown(f"""
    <div class="pipeline">{steps_html}</div>
    <div class="prog-wrap"><div class="prog-bar" style="width:{pct}%"></div></div>
    <div class="prog-row">
        <span>{label}</span>
        <span class="prog-pct">{pct}%</span>
    </div>
    """, unsafe_allow_html=True)


def render_success_banner(filename: str, n_chunks: int, elapsed: float):
    st.markdown(f"""
    <div class="ponder-card success-card">
        <div class="success-banner">
            <div>
                <div class="success-title">
                    <i class="ti ti-circle-check" aria-hidden="true"></i>
                    Document indexed and ready
                </div>
                <div class="success-meta">
                    {filename} &nbsp;·&nbsp; {n_chunks} chunks &nbsp;·&nbsp; Ready for questions
                </div>
            </div>
            <div class="success-time">Processed in {elapsed:.1f} s</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "chat_history": [], "pdf_processed": False,
    "current_pdf": None, "retriever": None,
    "total_queries": 0, "show_history": True,
    "n_chunks": 0, "elapsed": 0.0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;
                padding-bottom:1.25rem;border-bottom:1px solid rgba(255,255,255,0.1);
                margin-bottom:1.25rem">
        <div style="width:36px;height:36px;background:#c9a84c;border-radius:8px;
                    display:flex;align-items:center;justify-content:center;
                    font-family:'Instrument Serif',serif;font-size:18px;
                    color:#1a1a2e;font-style:italic;flex-shrink:0">P</div>
        <div>
            <div style="font-size:15px;font-weight:600;color:#fff">Ponder</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.4)">PDF Intelligence</div>
        </div>
    </div>
    <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.1em;
                color:rgba(255,255,255,0.35);margin-bottom:8px">Session</div>
    """, unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        st.metric("Queries", st.session_state.total_queries)
    with cb:
        st.metric("Turns", len(st.session_state.chat_history))

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.1em;
                color:rgba(255,255,255,0.35);margin-bottom:8px">Options</div>
    """, unsafe_allow_html=True)

    show_history = st.checkbox("Show chat history", value=st.session_state.show_history)
    st.session_state.show_history = show_history

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if st.button("🗑  Clear session"):
        st.session_state.chat_history = []
        st.session_state.total_queries = 0
        st.rerun()

    st.markdown("""
    <div style="margin-top:2rem;font-size:11px;color:rgba(255,255,255,0.2);text-align:center">
        Built with LangChain &amp; Streamlit
    </div>
    """, unsafe_allow_html=True)

# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("<p class='ponder-heading'>Ask your documents</p>", unsafe_allow_html=True)
st.markdown("<p class='ponder-sub'>Upload a PDF — Ponder extracts, chunks, and indexes it for instant Q&amp;A.</p>",
            unsafe_allow_html=True)

# ── Upload card ───────────────────────────────────────────────────────────────
st.markdown("<div class='ponder-card'>", unsafe_allow_html=True)
st.markdown("""<div class='ponder-card-label'>
    <i class='ti ti-upload' aria-hidden='true' style='font-size:14px'></i> Upload document
</div>""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drop a PDF here, or click to browse",
    type="pdf",
    label_visibility="collapsed"
)

if uploaded_file:
    size_kb = uploaded_file.size / 1024
    size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb / 1024:.1f} MB"
    already_done = (
        st.session_state.pdf_processed
        and st.session_state.current_pdf == uploaded_file.name
    )

    badge = ('<span class="ready-badge"><span class="ready-dot"></span> Already indexed</span>'
             if already_done else
             '<span class="ready-badge"><span class="ready-dot" style="background:#c9a84c"></span> Ready to process</span>')

    st.markdown(f"""
    <div class="file-strip">
        <div class="file-icon-box"><i class="ti ti-file-type-pdf" aria-hidden="true"></i></div>
        <div style="flex:1">
            <div class="file-name">{uploaded_file.name}</div>
            <div class="file-meta">{size_str} &nbsp;·&nbsp; PDF document</div>
        </div>
        {badge}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    if not already_done:
        if st.button("Process document →", type="primary", use_container_width=True):
            t0 = time.time()

            # ── Step 1: Load ──────────────────────────────────────────────
            pipeline_ph = st.empty()
            with pipeline_ph.container():
                st.markdown("""<div class='ponder-card-label' style='margin-top:1rem'>
                    <i class='ti ti-cpu' aria-hidden='true' style='font-size:14px'></i> Processing pipeline
                </div>""", unsafe_allow_html=True)
                render_pipeline(0, {})

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            docs = loader.load_docs(tmp_path)
            n_pages = len(docs)

            # ── Step 2: Chunk ─────────────────────────────────────────────
            pipeline_ph.empty()
            with pipeline_ph.container():
                st.markdown("""<div class='ponder-card-label' style='margin-top:1rem'>
                    <i class='ti ti-cpu' aria-hidden='true' style='font-size:14px'></i> Processing pipeline
                </div>""", unsafe_allow_html=True)
                render_pipeline(1, {0: f"{n_pages} pages"})

            chunks = chunker.chunk_docs(docs=docs)
            n_chunks = len(chunks)

            # ── Step 3: Embed ─────────────────────────────────────────────
            pipeline_ph.empty()
            with pipeline_ph.container():
                st.markdown("""<div class='ponder-card-label' style='margin-top:1rem'>
                    <i class='ti ti-cpu' aria-hidden='true' style='font-size:14px'></i> Processing pipeline
                </div>""", unsafe_allow_html=True)
                render_pipeline(2, {0: f"{n_pages} pages", 1: f"{n_chunks} chunks"})

            retriever = vectorstore.create_vector_store(chunks)

            # ── Step 4: Index done ────────────────────────────────────────
            pipeline_ph.empty()
            with pipeline_ph.container():
                st.markdown("""<div class='ponder-card-label' style='margin-top:1rem'>
                    <i class='ti ti-cpu' aria-hidden='true' style='font-size:14px'></i> Processing pipeline
                </div>""", unsafe_allow_html=True)
                render_pipeline(4, {0: f"{n_pages} pages", 1: f"{n_chunks} chunks",
                                    2: "Embedded", 3: "Indexed"})

            elapsed = time.time() - t0
            st.session_state.retriever = retriever
            st.session_state.pdf_processed = True
            st.session_state.current_pdf = uploaded_file.name
            st.session_state.n_chunks = n_chunks
            st.session_state.elapsed = elapsed
            time.sleep(0.4)
            st.rerun()
    else:
        # Show success banner when file is already processed
        render_success_banner(
            uploaded_file.name,
            st.session_state.n_chunks,
            st.session_state.elapsed
        )

elif st.session_state.pdf_processed:
    # File was processed in a previous run but uploader is empty
    render_success_banner(
        st.session_state.current_pdf,
        st.session_state.n_chunks,
        st.session_state.elapsed
    )

st.markdown("</div>", unsafe_allow_html=True)   # close .ponder-card

# ── Ask card ──────────────────────────────────────────────────────────────────
st.markdown("<div class='ponder-card'>", unsafe_allow_html=True)
st.markdown("""<div class='ponder-card-label'>
    <i class='ti ti-message-dots' aria-hidden='true' style='font-size:14px'></i> Ask a question
</div>""", unsafe_allow_html=True)

query = st.text_area(
    "Question",
    height=96,
    placeholder="e.g. What are the key findings in section 3?",
    label_visibility="collapsed"
)

btn_col, hint_col = st.columns([1, 2])
with btn_col:
    ask = st.button("Get answer →", type="primary", use_container_width=True)
with hint_col:
    if st.button("Show example questions", type="secondary"):
        st.info("Summarise the main points · What methodology was used? · List all figures · Compare Q2 and Q3")

if ask:
    if not st.session_state.pdf_processed:
        st.error("Upload and process a PDF first.")
    elif not query.strip():
        st.warning("Enter a question to continue.")
    else:
        with st.spinner("Reading document…"):
            try:
                chain = final_chain.output(st.session_state.retriever)
                response = chain.invoke(query)

                st.markdown(f"""
                <div class="answer-block">
                    <div class="answer-label">Answer</div>
                    {response}
                </div>
                """, unsafe_allow_html=True)

                st.session_state.chat_history.append({
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "question": query,
                    "answer": response,
                })
                st.session_state.total_queries += 1

            except Exception as e:
                err_str = str(e)
                # ── Groq / HuggingFace rate-limit (429) ──────────────────
                if "429" in err_str or "rate_limit_exceeded" in err_str or "Too Many Requests" in err_str:
                    # Try to extract the suggested wait time from the message
                    wait_sec = 60  # safe default
                    match = re.search(r'try again in\s+([\d.]+)(ms|s)', err_str, re.IGNORECASE)
                    if match:
                        val, unit = float(match.group(1)), match.group(2).lower()
                        wait_sec = max(2, int(val / 1000) if unit == "ms" else int(val) + 1)

                    st.markdown(f"""
                    <div style="background:#231f10;border:1px solid #3d3010;border-left:3px solid #c9a84c;
                                border-radius:0 8px 8px 0;padding:1rem 1.25rem;margin-top:0.75rem">
                        <div style="font-size:10px;font-weight:600;text-transform:uppercase;
                                    letter-spacing:0.1em;color:#c9a84c;margin-bottom:6px">
                            Rate limit reached
                        </div>
                        <div style="font-size:14px;color:rgba(255,255,255,0.8);line-height:1.6">
                            The Groq free tier has hit its token-per-minute limit.
                            Retrying automatically in <strong style="color:#c9a84c">{wait_sec}s</strong>…
                        </div>
                        <div style="font-size:12px;color:rgba(255,255,255,0.35);margin-top:6px">
                            Tip: space out your queries or upgrade to a paid Groq plan to raise the limit.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Live countdown then auto-retry once
                    countdown_ph = st.empty()
                    for remaining in range(wait_sec, 0, -1):
                        countdown_ph.markdown(
                            f"<div style='font-size:12px;color:rgba(255,255,255,0.35);margin-top:4px'>"
                            f"Retrying in {remaining}s…</div>",
                            unsafe_allow_html=True
                        )
                        time.sleep(1)
                    countdown_ph.empty()

                    try:
                        chain = final_chain.output(st.session_state.retriever)
                        response = chain.invoke(query)
                        st.markdown(f"""
                        <div class="answer-block">
                            <div class="answer-label">Answer</div>
                            {response}
                        </div>
                        """, unsafe_allow_html=True)
                        st.session_state.chat_history.append({
                            "timestamp": datetime.now().strftime("%H:%M"),
                            "question": query,
                            "answer": response,
                        })
                        st.session_state.total_queries += 1
                    except Exception as retry_err:
                        st.markdown(f"""
                        <div style="background:#1e0f0f;border:1px solid #4a1515;border-left:3px solid #e24b4a;
                                    border-radius:0 8px 8px 0;padding:1rem 1.25rem;margin-top:0.75rem">
                            <div style="font-size:10px;font-weight:600;text-transform:uppercase;
                                        letter-spacing:0.1em;color:#e24b4a;margin-bottom:6px">Still rate-limited</div>
                            <div style="font-size:13px;color:rgba(255,255,255,0.7);line-height:1.6">
                                Groq is still throttling requests. Please wait a minute before trying again.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # ── Any other error ───────────────────────────────────────
                else:
                    st.markdown(f"""
                    <div style="background:#1e0f0f;border:1px solid #4a1515;border-left:3px solid #e24b4a;
                                border-radius:0 8px 8px 0;padding:1rem 1.25rem;margin-top:0.75rem">
                        <div style="font-size:10px;font-weight:600;text-transform:uppercase;
                                    letter-spacing:0.1em;color:#e24b4a;margin-bottom:6px">Error</div>
                        <div style="font-size:13px;color:rgba(255,255,255,0.7);line-height:1.6;font-family:monospace">
                            {err_str}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── History ───────────────────────────────────────────────────────────────────
if st.session_state.show_history and st.session_state.chat_history:
    st.markdown("<div class='ponder-card'>", unsafe_allow_html=True)
    st.markdown("""<div class='ponder-card-label'>
        <i class='ti ti-clock-hour-4' aria-hidden='true' style='font-size:14px'></i> Recent queries
    </div>""", unsafe_allow_html=True)

    for chat in reversed(st.session_state.chat_history[-6:]):
        label = f"{chat['timestamp']}  ·  {chat['question'][:65]}{'…' if len(chat['question']) > 65 else ''}"
        with st.expander(label):
            st.markdown(f"**Question:** {chat['question']}")
            st.markdown(f"**Answer:** {chat['answer']}")

    st.markdown("</div>", unsafe_allow_html=True)