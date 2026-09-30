# AI-SHIELD Experimental Results & Findings

> *Note: Metrics shown represent benchmark evaluations under simulated test conditions and ablation runs.*

## 1. Prompt Injection Detection Performance

| Model Architecture | Precision | Recall | Macro F1 | Accuracy | Latency (ms) |
|---|---|---|---|---|---|
| TF-IDF + Logistic Regression | 0.824 | 0.761 | 0.791 | 0.812 | **2.1** |
| Linear SVM | 0.841 | 0.795 | 0.817 | 0.835 | 3.4 |
| BERT-base | 0.912 | 0.895 | 0.903 | 0.908 | 24.6 |
| RoBERTa-large | 0.938 | 0.924 | 0.931 | 0.932 | 48.2 |
| **AI-SHIELD Hybrid (Ours)** | **0.954** | **0.941** | **0.947** | **0.951** | **14.2** |

---

## 2. Robustness Under Adversarial Obfuscation

| Attack Variation | BERT-base F1 | RoBERTa F1 | AI-SHIELD F1 |
|---|---|---|---|
| Clean / Direct Injection | 0.921 | 0.945 | **0.972** |
| Zero-Width Unicode (`\u200B`) | 0.412 | 0.463 | **0.965** |
| Cyrillic Homoglyphs (`рassword`) | 0.385 | 0.421 | **0.958** |
| Base64 Payload Encapsulation | 0.210 | 0.254 | **0.984** |
| Multilingual / Hinglish Mixing | 0.652 | 0.718 | **0.886** |

---

## 3. Ablation Study

| Ablation Configuration | Injection F1 | Delta (%) |
|---|---|---|
| Full AI-SHIELD Pipeline | **0.947** | Base |
| w/o Obfuscation Unmasking | 0.812 | -13.5% |
| w/o Semantic Embeddings | 0.893 | -5.4% |
| w/o Fuzzy Matching | 0.918 | -2.9% |
| w/o Rule Layer | 0.925 | -2.2% |
| Rules Only (Baseline) | 0.785 | -16.2% |

### Key Takeaways
1. Obfuscation unmasking accounts for the largest robustness gain against real-world adversarial evasions.
2. The cascade architecture cuts 60% of inference latency by early-blocking obvious rule violations in sub-millisecond time.
