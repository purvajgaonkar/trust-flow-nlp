# Trust Flow — Intelligent NLP Security & Reliability Framework for LLMs

> **"Trust Flow watches what goes INTO AI and verifies what comes OUT."**

## 🎯 Overview

Trust Flow is a competition-grade, research-quality framework that:
1. **Detects prompt injection attacks** using a 4-layer pipeline (Regex, Fuzzy, Semantic, Transformer)
2. **Verifies LLM responses** for hallucinations using NLI + evidence retrieval
3. **Explains every decision** with evidence, confidence, and limitations
4. **Supports multilingual inputs**: English, Hindi, Marathi, Hinglish

---

## ⚡ Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### Docker (Full Stack)
```bash
docker-compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

---

## 🏗️ Architecture

```
User Prompt
    │
    ▼
Input Validation (length, encoding, HTML, URLs)
    │
    ▼
Language Detection (English / Hindi / Marathi / Hinglish)
    │
    ▼
NLP Analysis (spaCy: tokenize, POS, NER, dependencies)
    │
    ▼
┌───────────────────────────────────────────────┐
│              4-Layer Security Pipeline        │
│  Layer A: Regex Rules  (weight: 25%)          │
│  Layer B: Fuzzy Match  (weight: 20%)          │
│  Obfuscation Check     (weight: 20%)          │
│  Layer C: Semantic     (weight: 20%)          │
│  Layer D: Transformer  (weight: 15%)          │
│  Language Penalty      (weight: 10%)          │
└───────────────────────────────────────────────┘
    │
    ▼
Risk Fusion Engine → Risk Level (SAFE/LOW/MEDIUM/HIGH/CRITICAL)
    │
    ▼
[If safe] → Mock LLM Response
    │
    ▼
Hallucination Pipeline:
  Claim Extraction → Evidence Retrieval → NLI → Scoring
    │
    ▼
Trust Report (exportable)
```

---

## 🔒 Security Features

| Layer | Technique | Detects |
|-------|-----------|---------|
| A | Regex patterns (20+) | Direct injection, jailbreaks, extraction |
| B | Levenshtein fuzzy | Typo obfuscation, leet-speak |
| Obf | Multi-technique | Zero-width, BiDi, homoglyphs, Base64, URL encoding |
| C | Sentence-BERT | Semantic variants of known attacks |
| D | Transformer classifier | Novel attack patterns |

**Attack Types**: DIRECT_INJECTION, INDIRECT_INJECTION, JAILBREAK, SYSTEM_PROMPT_EXTRACTION, DATA_EXFILTRATION, ROLE_MANIPULATION, OBFUSCATION, MULTILINGUAL_ATTACK, UNKNOWN_ATTACK

---

## 🧪 Hallucination Detection

1. **Claim Extraction**: Sentence segmentation → atomic verifiable claims
2. **Evidence Retrieval**: Sentence-BERT semantic search over Wikipedia knowledge base
3. **NLI**: Cross-encoder classifies ENTAILMENT / CONTRADICTION / NEUTRAL
4. **Scoring**: Composite risk from NLI + evidence presence + semantic similarity

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze/prompt` | Full pipeline analysis |
| POST | `/api/analyze/response` | Hallucination verification |
| POST | `/api/analyze/document` | PDF/DOCX/TXT analysis |
| POST | `/api/security/injection` | Security detection only |
| POST | `/api/security/obfuscation` | Obfuscation detection only |
| POST | `/api/hallucination/claims` | Claim extraction |
| POST | `/api/hallucination/verify` | Full hallucination pipeline |
| POST | `/api/retrieval/search` | Evidence search |
| POST | `/api/nlp/analyze` | NLP analysis |
| GET | `/api/knowledge-graph` | Knowledge graph data |
| GET | `/api/models` | Available models |
| GET | `/api/benchmarks` | Benchmark references |
| GET | `/api/experiments` | Research results |
| GET | `/api/health` | Health check |

**Interactive API docs**: http://localhost:8000/docs

---

## ⚠️ Research Integrity

- **NEVER** fabricated accuracy/precision/recall/F1 values
- All demo metrics are labeled **DEMO DATA**
- Mock model results are labeled **MOCK/DEMONSTRATION MODE**
- Evaluation metrics display **"Evaluation pending"** where not measured
- All academic citations are to real published papers with accurate URLs

---

## 📚 References

1. Yi et al. (2023). *Prompt Injection Attacks and Defenses in LLM-Integrated Applications*. arXiv:2306.05499
2. Perez & Ribeiro (2022). *Ignore Previous Prompt: Attack Techniques For Language Models*. NeurIPS ML Safety Workshop 2022. arXiv:2211.09527
3. Li et al. (2023). *HaluEval: A Large-Scale Hallucination Evaluation Benchmark*. EMNLP 2023. arXiv:2305.11747
4. Niu et al. (2024). *RAGTruth: A Hallucination Corpus for RAG*. ACL 2024. arXiv:2401.00396
5. Reimers & Gurevych (2019). *Sentence-BERT*. EMNLP 2019. arXiv:1908.10084
6. Devlin et al. (2019). *BERT: Pre-training of Deep Bidirectional Transformers*. NAACL 2019. arXiv:1810.04805

---

## 🛠️ Tech Stack

**Backend**: Python 3.10+, FastAPI, spaCy, HuggingFace Transformers, Sentence-Transformers, scikit-learn, FAISS, NetworkX

**Frontend**: React 18, TypeScript, Tailwind CSS, Framer Motion, Recharts, D3.js

**Deployment**: Docker, Docker Compose

---

## 📄 License

MIT License — for academic and research use.
