# AI-SHIELD Experimental Design

## 1. Experimental Setup

### Datasets
- **Prompt Injection**:
  - PINT (Prompt Injection Benchmark): 1,200 curated attack and benign prompts.
  - PIDS-Bench: Evaluation suite for system prompt exfiltration and role-play bypasses.
  - Custom Adversarial Transformations: Unicode substitutions, Base64 encodings, and Hinglish code-mixing.
- **Hallucination Detection**:
  - HaluEval: 35,000 QA pairs annotated for factual hallucination.
  - RAGTruth: Word-level and sentence-level hallucination labels in RAG environments.

---

## 2. Baseline Models
We benchmark against standard baseline approaches:
1. **TF-IDF + Logistic Regression**: Bag-of-words representation with linear decision boundary.
2. **Support Vector Machine (Linear & RBF)**: Maximum margin classification.
3. **BERT-base-uncased**: Standard contextual encoder fine-tuned on injection prompts.
4. **RoBERTa-large**: Pretrained cross-entropy classifier.
5. **AI-SHIELD Hybrid Fusion (Ours)**: Multi-layer fusion combining rules, fuzzy, obfuscation unmasking, embeddings, and transformer classification.

---

## 3. Evaluation Metrics
- **Detection Performance**: Precision, Recall, Macro-F1, Accuracy, and ROC-AUC.
- **System Efficiency**: Latency (mean, p95, p99) measured in milliseconds under single-thread and batched conditions.
- **Adversarial Robustness**: Drop in detection rate under character mutations and homoglyph attacks.
