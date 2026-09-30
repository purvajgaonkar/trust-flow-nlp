# AI-SHIELD System Architecture

## Core Philosophy
> *"AI-SHIELD watches what goes INTO AI and verifies what comes OUT."*

AI-SHIELD provides bidirectional inspection for Large Language Model (LLM) applications:
1. **Ingress Protection (Security Pipeline)**: Detects direct & indirect prompt injections, jailbreaks, data exfiltration, and sophisticated adversarial obfuscations (zero-width characters, homoglyphs, base64 payloads, bilingual code-mixing).
2. **Egress Verification (Reliability Pipeline)**: Deconstructs LLM responses into atomic factual claims, conducts FAISS vector search across verified knowledge repositories, performs Natural Language Inference (NLI) classification, and scores hallucination risk.

---

## 1. High-Level Architecture Diagram

```
                     ┌────────────────────────────────┐
                     │          User Request          │
                     └────────────────┬───────────────┘
                                      │
                     ┌────────────────▼───────────────┐
                     │   Ingress: Security Pipeline   │
                     │  (Rules + Fuzzy + Obfuscation  │
                     │   + Semantic + Transformer)    │
                     └────────────────┬───────────────┘
                                      │
                         [Blocked if Risk >= 0.8]
                                      │ (If Safe / Allowed)
                     ┌────────────────▼───────────────┐
                     │        LLM Model Inference     │
                     └────────────────┬───────────────┘
                                      │
                     ┌────────────────▼───────────────┐
                     │  Egress: Hallucination Engine  │
                     │ (Claim Extraction -> Evidence  │
                     │  Retrieval -> NLI -> Scoring)  │
                     └────────────────┬───────────────┘
                                      │
                     ┌────────────────▼───────────────┐
                     │ Comprehensive Trust Report     │
                     └────────────────────────────────┘
```

---

## 2. Ingress Security Multi-Layer Pipeline

- **Layer A (Regex Rules)**: High-speed zero-latency deterministic pattern matcher targeting signature prompt injection keywords and bypass idioms.
- **Layer B (Fuzzy Matcher)**: Levenshtein distance matching against typo-injected keywords (`1gn0re`, `byp@ss`).
- **Obfuscation Engine**: Multi-script decoder detecting:
  - Zero-width unicode spaces (`\u200B`, `\uFEFF`, etc.)
  - Cyrillic / Greek homoglyph substitutions
  - Base64 / URL encoded payloads
  - Bidi override control codepoints (`\u202E`)
- **Layer C (Semantic Similarity)**: Dense sentence embeddings via Sentence-BERT compared against known attack manifolds with cosine similarity thresholding.
- **Layer D (Transformer Classifier)**: Fine-tuned encoder model classifying input into 10 discrete attack categories.
- **Weighted Fusion Engine**: Aggregates layer signals using calibrated weight vectors to determine final risk: Block (>= 0.8), Review (>= 0.5), or Safe (< 0.5).

---

## 3. Egress Hallucination Verification Pipeline

- **Atomic Claim Extraction**: Uses syntax splitting and dependency trees to split responses into verifiable factual propositions.
- **Evidence Retrieval**: Sub-millisecond dense retrieval using FAISS IndexFlatIP coupled with Cross-Encoder reranking.
- **NLI Classification**: Evaluates premise-hypothesis entailment, contradiction, and neutral relationships with calibrated confidence scores.
- **Explainable Scoring Engine**: Computes overall groundedness metrics and maps contradictions directly to cited sources.
