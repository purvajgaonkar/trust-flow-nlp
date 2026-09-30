# AI-SHIELD Research Methodology

## 1. Problem Formulation
Adversarial attacks on Large Language Models exploit the lack of distinction between control flow and data input in autoregressive language architectures. Prompt injection bypasses system directives, while hallucination undermines factual reliability in retrieval-augmented workflows.

AI-SHIELD addresses both failure modes simultaneously:
$$\text{Trust}(P, R) = f(\mathcal{S}(P), \mathcal{H}(R \mid \mathcal{K}))$$
where:
- $P$ is the input prompt
- $R$ is the generated response
- $\mathcal{S}(P) \in [0, 1]$ is the adversarial risk score
- $\mathcal{H}(R \mid \mathcal{K}) \in [0, 1]$ is the hallucination score evaluated against verifiable knowledge base $\mathcal{K}$

---

## 2. Ingress Defense Layering
We formulate prompt defense as a multi-tier cascade to optimize latency while guaranteeing robust detection:

1. **Deterministic Lexical Screening (Layer A)**: Fast regex matching over normalized string space.
2. **Approximate String Matching (Layer B)**: Levenshtein distance $\mathcal{L}(s_1, s_2)$ computed on character unigrams.
3. **Canonical Normalization**: Unicode NFKC normalization and homoglyph unmasking to defeat evasive character encodings.
4. **Dense Representation Matching (Layer C)**: Cosine similarity in Sentence-BERT metric space:
$$\cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|}$$
5. **Transformer Classification (Layer D)**: Fine-tuned multi-class transformer mapping inputs into attack topologies.

---

## 3. Claim-Level Hallucination Verification
To verify response reliability, sentences are segmented into atomic claims $\mathcal{C} = \{c_1, c_2, \dots, c_m\}$. For each claim $c_i$:
- Top-k evidence passages $\mathcal{E}_i = \{e_{i1}, \dots, e_{ik}\}$ are retrieved via dense inner-product indexing.
- Cross-encoder reranking prioritizes candidates.
- Natural Language Inference evaluates conditional probability:
$$P(\text{Entailment} \mid e, c_i), \quad P(\text{Contradiction} \mid e, c_i), \quad P(\text{Neutral} \mid e, c_i)$$
