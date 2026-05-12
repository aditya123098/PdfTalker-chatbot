# PdfTalker-chatbot
# 📚 PdfTalker — AI-Powered PDF Chatbot

> Upload any PDF and have a natural conversation with it using Retrieval-Augmented Generation (RAG).

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.49-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.3-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🧠 What is PdfTalker?

PdfTalker is an intelligent chatbot that lets you **ask questions about any PDF document** and receive accurate, context-aware answers — powered by a RAG (Retrieval-Augmented Generation) pipeline. Instead of reading through long documents, just upload your PDF and chat with it.

---

## ✨ Features

- 📄 **PDF Upload & Processing** — Upload any PDF and process it instantly
- 🔍 **Semantic Search** — FAISS vector store retrieves the most relevant document chunks
- 🤖 **AI-Powered Answers** — LangChain + HuggingFace models generate grounded responses
- 💬 **Chat History** — Keeps track of your Q&A session within the app
- 📊 **Query Counter** — Tracks how many questions you've asked
- 🎨 **Glassmorphism UI** — Beautiful frosted-glass interface built with Streamlit
- 🗑️ **Reset Anytime** — Clear the session and start fresh with a new document

---

## 🏗️ Architecture

```
User uploads PDF
       │
       ▼
  PDF Loader (pypdf)
       │
       ▼
  Text Chunker (LangChain TextSplitter)
       │
       ▼
  Embeddings (sentence-transformers)
       │
       ▼
  FAISS Vector Store
       │
  User asks a question
       │
       ▼
  Retriever → Relevant Chunks
       │
       ▼
  LangChain Chain → LLM Response
       │
       ▼
  Answer displayed in UI
```

The `utils/` folder contains modular pipeline components:

| Module | Responsibility |
|---|---|
| `utils/loader.py` | Load and parse PDF documents |
| `utils/chunker.py` | Split documents into overlapping text chunks |
| `utils/vectorstore.py` | Create and manage the FAISS embedding store |
| `utils/final_chain.py` | Build the LangChain retrieval-QA chain |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/aditya123098/PdfTalker-chatbot.git
cd PdfTalker-chatbot

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root if you need to configure API keys or model paths:

```env
# Example — add any keys required by your chosen LLM/embedding model
HUGGINGFACEHUB_API_TOKEN=your_token_here
```

### Run the App

```bash
streamlit run app4.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🖥️ Usage

1. **Upload a PDF** using the file uploader on the left panel.
2. Click **🚀 Process PDF** to extract text, chunk it, and build the vector index.
3. Type your question in the chat box and click **🔍 Answer**.
4. View the AI-generated answer directly in the interface.
5. Expand **Recent Insights** to review your conversation history.
6. Click **🗑 Reset App** in the sidebar to start over with a new document.

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit 1.49 |
| PDF Parsing | pypdf 6.0 |
| Text Splitting | LangChain Text Splitters |
| Embeddings | sentence-transformers 5.1 |
| Vector Store | FAISS (CPU) |
| LLM Orchestration | LangChain 0.3 + LangChain Community |
| ML Utilities | scikit-learn, numpy, pandas |
| Config | python-dotenv |

---

## 📁 Project Structure

```
PdfTalker-chatbot/
├── app4.py                 # Main Streamlit application
├── app2.py                 # Earlier prototype
├── app3.py                 # Earlier prototype
├── requirements.txt        # Python dependencies
├── .gitignore
├── LICENSE
├── .devcontainer/          # Dev container configuration
└── utils/
    ├── loader.py           # PDF document loader
    ├── chunker.py          # Text chunking logic
    ├── vectorstore.py      # FAISS vector store creation
    └── final_chain.py      # LangChain QA chain
```

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to your branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

**Aditya** — [@aditya123098](https://github.com/aditya123098)

---

*Built with ❤️ using LangChain, FAISS, and Streamlit*
