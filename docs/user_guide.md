# AI-SHIELD User Guide

## 1. Quick Start

### Starting the Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # On Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8000
```
Swagger UI will be available at: `http://localhost:8000/docs`

### Starting the Frontend
```bash
cd frontend
npm install
npm run dev
```
Access the web console at: `http://localhost:5173`

---

## 2. Navigating the AI-SHIELD Console

### 1. Unified Analyze Workspace (`/analyze`)
- Submit any prompt or upload documents (PDF/DOCX/TXT).
- Watch the live **Animated Pipeline** track execution across:
  - Language Detection & Input Validation
  - Lexical Normalization & Homoglyph Unmasking
  - Rule, Fuzzy, and Semantic Attack Scanning
  - Transformer Classification & Calibrated Fusion
- Review AI-generated response alongside **Claim-Level Groundedness**.
- Click **"WHY?"** on any verdict to inspect the explainable reasoning modal.
- Export full **Trust Audit Reports** as JSON, CSV, or formatted PDF summaries.

### 2. NLP Explorer (`/nlp`)
- Visualize token-level POS tags with universal color coding.
- Inspect standard linguistic and custom security NER spans.
- Examine syntactic dependency relation trees and dense sentence vector embeddings.

### 3. Security Lab (`/security`)
- Run deep adversarial inspections.
- Test across 10 discrete attack classes (Direct Injection, Jailbreak, System Prompt Extraction, Base64, Cyrillic Homoglyphs, etc.).
- Inspect per-layer raw scores and component weights.

### 4. Hallucination Lab & Evidence Lab (`/hallucination`, `/evidence`)
- Enter an AI response and evaluate claim extraction.
- View corroborated and contradicted propositions with linked knowledge passages and NLI entailment confidence scores.

### 5. Research Lab & Benchmarks (`/research`, `/benchmarks`)
- Compare baseline models (TF-IDF, SVM, BERT, RoBERTa, AI-SHIELD Hybrid).
- Review ablation charts and academic benchmark references (PINT, PIDS-Bench, HaluEval, RAGTruth).

### 6. Knowledge Graph (`/graph`)
- Explore interactive NetworkX entities and semantic relations (e.g. Elon Musk $\to$ FOUNDED $\to$ Tesla).

### 7. Attack Lab (`/attack-lab`)
- 1-click adversarial mutation engine: NORMAL, TYPO, UNICODE, BASE64, HOMOGRAPH, ZERO-WIDTH, MULTILINGUAL, HINGLISH.
- Observe how AI-SHIELD unmasks transformations in real time.

### 8. Competition Mode (`/competition`)
- Full-screen 10-step demo walkthrough built specifically for hackathons and academic presentations.
