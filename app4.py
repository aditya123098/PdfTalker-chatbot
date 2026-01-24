import streamlit as st
from utils import loader, chunker, vectorstore, final_chain
import tempfile
import time
from datetime import datetime
import os
import base64

# ----------------- Helper Function -----------------
def get_base64_of_bin_file(bin_file):
    """Encodes a local file to base64 for CSS injection."""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# ----------------- Page configuration -----------------
st.set_page_config(
    page_title="PDF Talker",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- Background Processing -----------------
img_path = os.path.join('assets', 'claudio-schwarz-n4VMPADwI6c-unsplash.jpg')
img_base64 = get_base64_of_bin_file(img_path)

if img_base64:
    bg_style = f'background-image: url("data:image/jpg;base64,{img_base64}");'
else:
    bg_style = 'background-color: #0f1117;'

# ----------------- Modern Minimalist CSS -----------------
st.markdown(f"""
<style>
/* 1. Base App Layer */
.stApp {{
    {bg_style}
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: #ffffff;
}}

/* 2. Transparency for Overlays */
.main, .stMainBlockContainer, [data-testid="stAppViewMain"] {{
    background-color: transparent !important;
}}

/* 3. Improved Glass Container Targeting */
/* We target 'stVerticalBlock' and 'element-container' to force the glass background 
   to wrap around the full height of your UI elements */
[data-testid="stVerticalBlock"] > div > div > [data-testid="element-container"] {{
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(15px);
    border-radius: 15px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 20px !important;
    margin-bottom: 20px !important;
    display: block;
}}

/* 4. Reset for Columns */
/* We remove background from the columns so the glass container above handles it */
div[data-testid="column"] {{
    background: transparent !important;
    backdrop-filter: none !important;
    border: none !important;
    box-shadow: none !important;
}}

/* 5. Input Styling (Drag & Drop + Text Area) */
[data-testid="stFileUploader"], .stTextArea textarea {{
    background-color: rgba(0, 0, 0, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    color: white !important;
}}

/* 6. Sidebar & Buttons */
section[data-testid="stSidebar"] {{
    background: rgba(0, 0, 0, 0.4) !important;
    backdrop-filter: blur(25px);
}}

.stButton>button {{
    background: rgba(255, 255, 255, 0.1);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    width: 100%;
    transition: 0.3s;
}}

.stButton>button:hover {{
    background: rgba(255, 255, 255, 0.2);
    border-color: #ffffff;
}}

/* 7. Answer Box Styling */
.answer-bubble {{
    background: rgba(255,255,255,0.05); 
    padding: 15px; 
    border-radius: 10px; 
    border-left: 3px solid #00e5ff;
    margin-top: 10px;
}}

/* Hide unnecessary default UI elements */
#MainMenu, footer, header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ----------------- Session State Fix -----------------
if 'chat_history' not in st.session_state or not isinstance(st.session_state.chat_history, list):
    st.session_state.chat_history = []
if 'pdf_processed' not in st.session_state: st.session_state.pdf_processed = False
if 'current_pdf' not in st.session_state: st.session_state.current_pdf = None
if 'retriever' not in st.session_state: st.session_state.retriever = None
if 'total_queries' not in st.session_state: st.session_state.total_queries = 0

# ----------------- Sidebar -----------------
with st.sidebar:
    st.title("📚 PDF Talker")
    st.markdown("---")
    st.metric("Queries", st.session_state.total_queries)
    st.metric("History", len(st.session_state.chat_history))
    st.markdown("---")
    show_history = st.checkbox("Show History", value=True)
    if st.button("🗑 Reset App"):
        st.session_state.clear()
        st.rerun()

# ----------------- Main UI -----------------
st.markdown("<h1 style='text-align: center; font-weight: 200;'>📊 PDF Talker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.6;'>Talk to your PDF with AI Document Intelligence</p><br>", unsafe_allow_html=True)

# --- Upload & Status Section ---
col_up, col_stat = st.columns([2, 1])

with col_up:
    st.markdown("### 📄 Upload Document")
    uploaded_file = st.file_uploader("Upload", type="pdf", label_visibility="collapsed")
    if uploaded_file:
        st.caption(f"**Selected File:** {uploaded_file.name}")
        if st.button("🚀 Process PDF"):
            with st.spinner("Processing..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    path = tmp.name
                docs = loader.load_docs(path)
                chunks = chunker.chunk_docs(docs)
                st.session_state.retriever = vectorstore.create_vector_store(chunks)
                st.session_state.pdf_processed = True
                st.session_state.current_pdf = uploaded_file.name
                os.remove(path)
                st.rerun()

with col_stat:
    st.markdown("### 📊 Status")
    if st.session_state.pdf_processed:
        st.markdown(f"<span style='color: #00ffcc;'>● Ready:</span> <br>{st.session_state.current_pdf}", unsafe_allow_html=True)
    else:
        st.markdown("<span style='color: #ff4b4b; opacity: 0.8;'>● No file active</span>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Chat Section ---
st.markdown("### 💬 Ask anything")
query = st.text_area("Question", placeholder="Type a question about your document...", label_visibility="collapsed")

btn_col1, btn_col2, _ = st.columns([1, 1, 4])
with btn_col1:
    ask = st.button("🔍 Answer")
with btn_col2:
    if st.button("💡 Example"):
        st.toast("Try: 'Give me a summary'")

if ask and query:
    if st.session_state.pdf_processed:
        with st.spinner("Thinking..."):
            chain = final_chain.output(st.session_state.retriever)
            ans = chain.invoke(query)
            st.markdown(f"<div class='answer-bubble'>{ans}</div>", unsafe_allow_html=True)
            st.session_state.chat_history.append({'q': query, 'a': ans})
            st.session_state.total_queries += 1
    else:
        st.error("Upload a PDF first!")

# --- History Section ---
if show_history and st.session_state.chat_history:
    st.markdown("<br>### 📜 Recent Insights", unsafe_allow_html=True)
    # Safety filter to prevent the Traceback error
    valid_history = [c for c in st.session_state.chat_history if isinstance(c, dict)]
    for chat in reversed(valid_history[-3:]):
        with st.expander(f"Q: {chat.get('q', '')[:60]}..."):
            st.write(chat.get('a', ''))
