# 📚 PdfTalker — AI-Powered PDF Chatbot & Question Paper Generator

> Upload any PDF. Ask questions. Generate exam-ready question papers — all powered by Retrieval-Augmented Generation (RAG).

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.49-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.3-green)
![FAISS](https://img.shields.io/badge/FAISS-CPU-orange)
![HuggingFace](https://img.shields.io/badge/HuggingFace-sentence--transformers-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📖 Table of Contents

- [What is PdfTalker?](#-what-is-pdftalker)
- [Features](#-features)
- [Architecture](#-architecture)
- [Question Paper Generation](#-question-paper-generation)
- [App Versions](#-app-versions)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Usage Guide](#-usage-guide)
- [Prompt Engineering for Question Papers](#-prompt-engineering-for-question-papers)
- [Example Outputs](#-example-outputs)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🧠 What is PdfTalker?

**PdfTalker** is an intelligent, dual-purpose AI application that lets you:

1. **Chat with any PDF** — Ask natural-language questions about the document and receive accurate, context-grounded answers.
2. **Generate Question Papers** — Automatically produce structured exam papers (MCQs, short-answer, long-answer, true/false) directly from the content of any uploaded PDF.

It is built on a **RAG (Retrieval-Augmented Generation)** pipeline, ensuring every answer and every generated question is rooted in the actual document — not hallucinated from general training data.

---

## ✨ Features

### 💬 PDF Chatbot
- Upload any PDF (textbooks, research papers, reports, notes)
- Instant semantic search across the entire document
- AI-generated, context-aware answers
- Chat history with timestamped Q&A pairs
- Query counter and session statistics
- One-click session reset

### 📝 Question Paper Generator
- Auto-generate questions from any section or the entire PDF
- Supports multiple question types: MCQ, Short Answer, Long Answer, True/False, Fill in the Blank
- Configurable number of questions per type
- Difficulty level control (Easy / Medium / Hard)
- Topic-specific question generation (e.g., "Generate questions only on Chapter 3")
- Clean, formatted output ready for printing or export

### 🎨 UI & Experience
- Three polished UI variants (app2, app3, app4) with glassmorphism and gradient themes
- Progress bar during PDF processing
- Responsive two-column layout
- Animated answer display
- Sidebar with live statistics and settings

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  User Interface                  │
│              (Streamlit — app4.py)               │
└────────────────┬────────────────────────────────┘
                 │  Upload PDF
                 ▼
┌─────────────────────────────────────────────────┐
│           utils/loader.py                        │
│    Reads and parses PDF using pypdf              │
└────────────────┬────────────────────────────────┘
                 │  Raw text pages
                 ▼
┌─────────────────────────────────────────────────┐
│           utils/chunker.py                       │
│    Splits text into overlapping chunks           │
│    (LangChain RecursiveCharacterTextSplitter)    │
└────────────────┬────────────────────────────────┘
                 │  List of Document chunks
                 ▼
┌─────────────────────────────────────────────────┐
│           utils/vectorstore.py                   │
│    Embeds chunks with sentence-transformers      │
│    Stores embeddings in FAISS index              │
└────────────────┬────────────────────────────────┘
                 │  FAISS Retriever
                 ▼
┌─────────────────────────────────────────────────┐
│           utils/final_chain.py                   │
│    Builds LangChain RetrievalQA chain            │
│    Combines retriever + LLM for generation       │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
  User Question     Question Paper
  → Direct Answer   Generation Prompt
                    → Structured Paper
```

### Core Pipeline Steps

**Step 1 — Load:** `pypdf` reads the uploaded PDF and extracts all text content page by page.

**Step 2 — Chunk:** LangChain's `RecursiveCharacterTextSplitter` splits the extracted text into overlapping chunks (e.g., 500 tokens with 50-token overlap). Overlapping ensures context is not lost at chunk boundaries.

**Step 3 — Embed & Index:** Each chunk is converted into a dense vector using `sentence-transformers`. All vectors are stored in a FAISS (Facebook AI Similarity Search) index for fast nearest-neighbor retrieval.

**Step 4 — Retrieve & Generate:** When a user asks a question or requests a question paper, the query is embedded and the top-k most relevant chunks are retrieved from FAISS. These chunks are passed as context to the LLM via a LangChain chain, which produces the final grounded response.

---

## 📝 Question Paper Generation

This is one of the most powerful features of PdfTalker — the ability to turn any PDF into a complete, formatted question paper in seconds.

### How It Works

The question paper generator uses the **same RAG pipeline** as the chatbot, but with a carefully crafted **generation prompt** that instructs the LLM to produce structured exam questions rather than a conversational answer.

```
PDF Content (chunked + indexed)
         │
         ▼
  Retrieval: Fetch relevant chunks
  based on topic or full document
         │
         ▼
  Prompt Template:
  "You are an expert examiner.
   Based on the following content,
   generate [N] [type] questions
   at [difficulty] level..."
         │
         ▼
  LLM generates structured question paper
         │
         ▼
  Formatted output displayed in UI
```

### Question Types Supported

| Type | Description | Example |
|---|---|---|
| **MCQ** | Multiple choice with 4 options (A–D) | "Which of the following best describes...?" |
| **Short Answer** | 2–3 sentence responses | "Define the term X in context of Y." |
| **Long Answer** | Detailed explanatory questions | "Explain the significance of X with examples." |
| **True / False** | Statement-based verification | "State whether the following is True or False." |
| **Fill in the Blank** | Sentence completion | "The process of X is known as ___." |
| **Case-Based** | Scenario followed by sub-questions | "Read the passage. Answer the following..." |

### Generation Prompt Templates

You can trigger question paper generation by typing prompts like the following in the chat box:

**Generate a full question paper:**
```
Generate a question paper with 5 MCQs, 3 short-answer questions, 
and 2 long-answer questions based on this document.
```

**Topic-specific generation:**
```
Generate 10 MCQ questions only about [topic name] from this document.
All questions should be of medium difficulty.
```

**Difficulty-controlled:**
```
Create 5 hard-level analytical questions that test deep understanding 
of the key concepts in this PDF.
```

**True/False set:**
```
Generate 10 True or False statements based on the facts in this document. 
Include the correct answer for each.
```

**Fill in the blanks:**
```
Create 10 fill-in-the-blank questions from the definitions and key terms 
mentioned in this document.
```

**Section-specific:**
```
Based only on pages 10 to 25 of this document, generate a 20-mark 
question paper with MCQs and short-answer questions.
```

### Output Format

A typical generated question paper looks like:

```
╔══════════════════════════════════════════════════╗
║           QUESTION PAPER — [PDF Title]           ║
║         Total Marks: 40 | Time: 90 mins          ║
╚══════════════════════════════════════════════════╝

SECTION A — Multiple Choice Questions (1 mark each)

Q1. Which of the following best describes [concept]?
    A) Option one
    B) Option two
    C) Option three ✓
    D) Option four

Q2. ...

──────────────────────────────────────────────────

SECTION B — Short Answer Questions (3 marks each)

Q6. Define [term] and explain its significance.

Q7. ...

──────────────────────────────────────────────────

SECTION C — Long Answer Questions (5 marks each)

Q9. Discuss in detail [topic] with relevant examples.

Q10. ...
```

### Step-by-Step: Generate a Question Paper

1. **Upload your PDF** — This can be a textbook chapter, research paper, lecture notes, or any study material.

2. **Click "🚀 Process PDF"** — The document is parsed, chunked, embedded, and indexed into FAISS. This typically takes 10–30 seconds depending on document length.

3. **Type your generation prompt** in the question box. Be specific about:
   - Number of questions
   - Question types (MCQ, short, long, true/false)
   - Difficulty level (easy, medium, hard)
   - Topic or section (optional)
   - Total marks (optional)

4. **Click "🔍 Answer"** — The LangChain chain retrieves the most relevant content from the PDF and passes it to the LLM to generate your question paper.

5. **Copy or export the output** — The formatted question paper appears in the answer box. You can copy it directly or extend the app to add a PDF/Word export feature.

### Tips for Better Question Papers

- **Be specific in your prompt.** Vague prompts like "generate questions" produce generic output. Prompts like "generate 5 MCQs on the water cycle for Grade 10 students" produce targeted, usable questions.
- **Chunk your document by topic.** If your PDF covers multiple chapters, ask questions one chapter at a time for higher accuracy.
- **Use difficulty modifiers.** Words like "analytical", "application-based", "recall-based", "HOTS (Higher Order Thinking Skills)" steer the LLM toward the right cognitive level.
- **Request answer keys.** Add "Include the correct answer after each question" to get a ready-to-use answer key alongside the question paper.
- **Specify marks.** "Each MCQ carries 1 mark, short answer carries 3 marks" helps the LLM format the output more consistently.
- **Use academic language.** Phrasing like "as per the document" or "based strictly on the uploaded content" reinforces that the LLM should not use outside knowledge.

---

## 🗂️ App Versions

The repository contains three UI versions of the same core pipeline:

| File | Theme | Notable Features |
|---|---|---|
| `app2.py` | Purple gradient, white cards | Progress bar, file size display, example prompts |
| `app3.py` | Translucent purple + blur | Glassmorphism panels, animated transitions, custom scrollbar |
| `app4.py` | Dark glass + background image | Background image support, minimal layout, compact sidebar |

All three versions share the identical `utils/` pipeline. **`app4.py` is the recommended production version.**

---

## 📁 Project Structure

```
PdfTalker-chatbot/
│
├── app2.py                 # UI Version 2 — Purple gradient theme
├── app3.py                 # UI Version 3 — Glassmorphism theme
├── app4.py                 # UI Version 4 — Dark glass + background image (recommended)
│
├── utils/
│   ├── loader.py           # PDF loading with pypdf
│   ├── chunker.py          # Text splitting (RecursiveCharacterTextSplitter)
│   ├── vectorstore.py      # FAISS vector index creation
│   └── final_chain.py      # LangChain RetrievalQA chain builder
│
├── assets/                 # Background images (used in app4.py)
├── .devcontainer/          # GitHub Codespaces configuration
├── requirements.txt        # All Python dependencies
├── .gitignore
└── LICENSE                 # MIT License
```

### Module Details

**`utils/loader.py`**
Loads a PDF from a given file path using `pypdf`. Returns a list of `Document` objects, one per page, with page content and metadata.

**`utils/chunker.py`**
Takes the list of documents and splits them into smaller, overlapping chunks using LangChain's `RecursiveCharacterTextSplitter`. This preserves sentence boundaries and prevents context from being cut off at chunk edges.

**`utils/vectorstore.py`**
Embeds each chunk using `sentence-transformers` (HuggingFace) and stores the resulting dense vectors in a FAISS CPU index. Returns a LangChain-compatible retriever object.

**`utils/final_chain.py`**
Constructs a LangChain `RetrievalQA` chain that combines the FAISS retriever with the configured LLM. The chain accepts a query, retrieves the top-k relevant chunks, and generates a grounded response.

---

## 📦 Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Web UI | Streamlit | 1.49.1 |
| PDF Parsing | pypdf | 6.0.0 |
| Text Splitting | LangChain Text Splitters | 0.3.11 |
| Embeddings | sentence-transformers | 5.1.0 |
| Vector Store | FAISS (CPU) | 1.12.0 |
| LLM Orchestration | LangChain + LangChain Community | 0.3.27 / 0.3.29 |
| HuggingFace Integration | langchain-huggingface | 0.3.1 |
| Data Handling | numpy, pandas | 2.3.3 / 2.3.2 |
| ML Utilities | scikit-learn | 1.7.2 |
| Validation | pydantic | 2.11.9 |
| Config | python-dotenv | 1.1.1 |
| Image Processing | Pillow | 11.3.0 |

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

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 3. Install all dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root for any API keys required by your LLM or embedding model:

```env
# HuggingFace API token (required if using gated models)
HUGGINGFACEHUB_API_TOKEN=hf_your_token_here

# Optional: specify a custom model name
# MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

### Run the App

```bash
# Recommended (latest version)
streamlit run app4.py

# Or run an earlier version
streamlit run app3.py
streamlit run app2.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📘 Usage Guide

### Chatbot Mode

1. Open the app in your browser.
2. In the **Upload Document** section, click to browse or drag-and-drop a PDF file.
3. Click **🚀 Process PDF** and wait for the progress indicator to complete.
4. Once the status shows **● Ready**, type any question about the document in the chat box.
5. Click **🔍 Answer** to receive an AI-generated, document-grounded response.
6. Your Q&A pairs are saved in **Recent Insights** / **Chat History** at the bottom.
7. Use **🗑 Reset App** in the sidebar to clear the session and start with a new document.

### Question Paper Generation Mode

1. Upload and process your PDF (same steps as above).
2. In the question/chat box, type a generation prompt (see examples in the section above).
3. Click **🔍 Answer** — the app generates the question paper using RAG over your document.
4. The formatted question paper appears in the answer bubble.
5. Copy the output directly, or extend the app with a download button for PDF/Word export.

---

## 🧪 Prompt Engineering for Question Papers

The quality of the generated question paper depends heavily on how you phrase your prompt. Here are tested, reusable patterns:

### Pattern 1 — Standard Exam Paper
```
Generate a complete question paper from this document with the following structure:
- Section A: 10 MCQs (1 mark each)
- Section B: 5 short-answer questions (3 marks each)
- Section C: 2 long-answer questions (5 marks each)
Total: 35 marks. Include the correct answers for Section A.
```

### Pattern 2 — Topic-Focused
```
From this PDF, generate 8 questions specifically about [topic].
Mix MCQs and short-answer questions. Difficulty: medium.
```

### Pattern 3 — Bloom's Taxonomy Levels
```
Generate 10 questions at three cognitive levels:
- 3 knowledge/recall questions
- 4 understanding/application questions
- 3 analysis/evaluation questions
Base all questions strictly on this document only.
```

### Pattern 4 — Quick Quiz
```
Generate a 5-question quick quiz from the key points in this PDF.
Format: MCQ with 4 options each. Show the answer after each question.
```

### Pattern 5 — Fill in the Blank Worksheet
```
Create a fill-in-the-blank worksheet with 15 questions derived from 
important definitions and facts in this document.
Leave a blank line after each question for the student to write in.
```

### Pattern 6 — Answer Key Generation
```
Generate 10 MCQ questions from this document along with a separate 
answer key at the end. Clearly label the answer key section.
```

---

## 💡 Example Outputs

### Example 1 — Chatbot Answer

**Question:** What is the main methodology used in this research paper?

**Answer:**
> The study employed a mixed-methods approach, combining quantitative survey data collected from 320 participants with qualitative interviews conducted across three regions. Statistical analysis was performed using SPSS, and thematic analysis was applied to interview transcripts...

### Example 2 — Generated MCQ Set

**Prompt:** Generate 3 MCQs from this document on the topic of neural networks.

**Output:**
```
Q1. Which of the following activation functions is most commonly used 
    in hidden layers of deep neural networks?
    A) Sigmoid
    B) ReLU ✓
    C) Tanh
    D) Softmax

Q2. What does backpropagation compute in a neural network?
    A) Forward pass outputs
    B) Loss function value
    C) Gradients of the loss with respect to weights ✓
    D) Number of training epochs

Q3. The vanishing gradient problem is most associated with which architecture?
    A) Convolutional Neural Networks
    B) Deep Recurrent Neural Networks ✓
    C) Random Forests
    D) Support Vector Machines
```

### Example 3 — Short Answer Questions

**Prompt:** Generate 3 short-answer questions from this PDF on data preprocessing.

**Output:**
```
Q1. Define data normalization and explain why it is important before 
    training a machine learning model. (3 marks)

Q2. What is the difference between label encoding and one-hot encoding? 
    When should each be used? (3 marks)

Q3. Briefly describe two common techniques for handling missing values 
    in a dataset. (3 marks)
```

---

## 🤝 Contributing

Contributions are welcome! Some ideas for what to add next:

- **Export to PDF/Word** — Add a download button to save generated question papers
- **Difficulty slider** — UI control to set question difficulty before generating
- **Multi-PDF support** — Allow querying across multiple uploaded documents
- **Answer key toggle** — Show/hide answers in the generated paper
- **Question bank** — Save and accumulate generated questions across sessions
- **Mark scheme generator** — Auto-generate model answers alongside questions

### How to Contribute

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: add your feature description"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

**Aditya** — [@aditya123098](https://github.com/aditya123098)

---

*Built with ❤️ using LangChain, FAISS, sentence-transformers, and Streamlit*
