import streamlit as st
from utils import loader, chunker, vectorstore, final_chain
import tempfile
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="PDF Intelligence Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= Custom CSS =================
st.markdown("""
    <style>
    /* ======= Base Layout ======= */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-family: 'Inter', sans-serif;
    }

    .main, .block-container, .element-container,
    div[data-testid="stVerticalBlock"],
    div[data-testid="stHorizontalBlock"],
    div[data-testid="column"] {
        background: transparent !important;
        box-shadow: none !important;
    }

    /* ======= Text & Headings ======= */
    h1, h2, h3, h4, h5, h6, p, label, span {
        color: #fff !important;
    }

    /* ======= Sidebar Styling ======= */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }
    [data-testid="stSidebarNav"] {
        background: transparent !important;
    }

    /* ======= Upload Section ======= */
    section[data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1.5px dashed rgba(255, 255, 255, 0.3) !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        transition: all 0.3s ease-in-out;
    }
    section[data-testid="stFileUploader"]:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: #b19cd9 !important;
    }
    div[data-testid="stFileUploader"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* ======= Chat Container ======= */
    .chat-container {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 2rem;
        transition: transform 0.3s;
    }
    .chat-container:hover {
        transform: translateY(-3px);
    }

    /* ======= Upload Section ======= */
    .upload-section {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* ======= Response Box ======= */
    .response-box {
        background: rgba(0, 0, 0, 0.25);
        border-left: 5px solid #00e5ff;
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        color: white;
        animation: fadeIn 0.5s ease-in-out;
        backdrop-filter: blur(10px);
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ======= Chat History ======= */
    .history-item {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.7rem;
        border-left: 4px solid #b39ddb;
        backdrop-filter: blur(10px);
    }

    /* ======= Metric Cards ======= */
    .metric-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        color: white;
    }

    /* ======= Text Area ======= */
    .stTextArea > div > div {
        background: rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    textarea {
        color: white !important;
    }
    textarea::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }

    /* ======= Buttons ======= */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }

    /* ======= Expanders ======= */
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
    }

    /* ======= Scrollbar ======= */
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# ================== Session State ==================
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'pdf_processed' not in st.session_state:
    st.session_state.pdf_processed = False
if 'current_pdf' not in st.session_state:
    st.session_state.current_pdf = None
if 'retriever' not in st.session_state:
    st.session_state.retriever = None
if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0

# ================= Sidebar =================
with st.sidebar:
    st.markdown("### 📚 PDF Intelligence Assistant")
    st.markdown("---")

    # Statistics
    st.markdown("### 📊 Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Queries", st.session_state.total_queries)
    with col2:
        st.metric("Chat History", len(st.session_state.chat_history))

    st.markdown("---")

    # Settings
    st.markdown("### ⚙ Settings")
    show_history = st.checkbox("Show Chat History", value=True)
    clear_history = st.button("🗑 Clear History")

    if clear_history:
        st.session_state.chat_history = []
        st.session_state.total_queries = 0
        st.rerun()

    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.info("""
    - Upload a PDF document  
    - Ask specific questions  
    - Review chat history  
    - Get instant answers  
    """)

    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    st.markdown("[Documentation](#) | [Support](#) | [About](#)")

# ================= Main Page =================
st.markdown("<h1 style='text-align: center; color: white;'>📚 PDF Intelligence Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white; font-size: 1.2rem;'>Upload your PDF and get instant answers to your questions</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ===== Upload Section =====
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
    st.markdown("### 📄 Upload Your Document")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF document to analyze",
        label_visibility="collapsed"
    )

    if uploaded_file:
        file_details = {
            "Filename": uploaded_file.name,
            "FileSize": f"{uploaded_file.size / 1024:.2f} KB",
            "FileType": uploaded_file.type
        }

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"📄 Name:** {file_details['Filename']}")
        with col_b:
            st.markdown(f"💾 Size:** {file_details['FileSize']}")
        with col_c:
            st.markdown(f"📋 Type:** PDF")

        if st.button("🚀 Process PDF", use_container_width=True):
            with st.spinner("🔄 Processing your PDF..."):
                progress_bar = st.progress(0)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_file_path = tmp_file.name
                progress_bar.progress(25)

                docs = loader.load_docs(tmp_file_path)
                progress_bar.progress(50)
                chunks = chunker.chunk_docs(docs=docs)
                progress_bar.progress(75)
                st.session_state.retriever = vectorstore.create_vector_store(chunks)
                progress_bar.progress(100)

                st.session_state.pdf_processed = True
                st.session_state.current_pdf = uploaded_file.name

                st.success(f"✅ PDF '{uploaded_file.name}' processed successfully!")
                time.sleep(1)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("### 📊 Status")
    if st.session_state.pdf_processed:
        st.success("✅ PDF Ready")
        st.markdown(f"*Current PDF:*  \n{st.session_state.current_pdf}")
    else:
        st.warning("⏳ No PDF loaded")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===== Chat Interface =====
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
st.markdown("### 💬 Ask Your Question")

query = st.text_area(
    "Type your question here...",
    height=100,
    placeholder="e.g., What is the main topic of this document?",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    ask_button = st.button("🔍 Get Answer", use_container_width=True)
with col2:
    example_button = st.button("💡 Example", use_container_width=True)

if example_button:
    st.info("📝 Example questions:\n- Summarize the main points\n- What methodology was used?\n- List the key findings")

if ask_button:
    if not st.session_state.pdf_processed:
        st.error("⚠ Please upload and process a PDF first!")
    elif not query.strip():
        st.warning("⚠ Please enter a question!")
    else:
        with st.spinner("🤔 Thinking..."):
            try:
                response_chain = final_chain.output(st.session_state.retriever)
                response = response_chain.invoke(query)

                st.markdown("<div class='response-box'>", unsafe_allow_html=True)
                st.markdown("### 🎯 Answer")
                st.markdown(response)
                st.markdown("</div>", unsafe_allow_html=True)

                st.session_state.chat_history.append({
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'question': query,
                    'answer': response
                })
                st.session_state.total_queries += 1

                st.success("✅ Answer generated successfully!")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.markdown("</div>", unsafe_allow_html=True)

# ===== Chat History =====
if show_history and st.session_state.chat_history:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    st.markdown("### 📜 Chat History")

    for idx, chat in enumerate(reversed(st.session_state.chat_history[-5:])):
        with st.expander(f"🕐 {chat['timestamp']} - Q: {chat['question'][:50]}..."):
            st.markdown(f"*Question:* {chat['question']}")
            st.markdown(f"*Answer:* {chat['answer']}")

    st.markdown("</div>", unsafe_allow_html=True)

# ===== Footer =====
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white;'>Made with ❤ using Streamlit & LangChain</p>", unsafe_allow_html=True)