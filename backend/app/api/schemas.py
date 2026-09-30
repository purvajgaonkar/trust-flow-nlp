"""
Pydantic Schemas for API requests and responses.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import time


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

class AttackType(str, Enum):
    SAFE = "SAFE"
    DIRECT_INJECTION = "DIRECT_INJECTION"
    INDIRECT_INJECTION = "INDIRECT_INJECTION"
    JAILBREAK = "JAILBREAK"
    SYSTEM_PROMPT_EXTRACTION = "SYSTEM_PROMPT_EXTRACTION"
    DATA_EXFILTRATION = "DATA_EXFILTRATION"
    ROLE_MANIPULATION = "ROLE_MANIPULATION"
    OBFUSCATION = "OBFUSCATION"
    MULTILINGUAL_ATTACK = "MULTILINGUAL_ATTACK"
    UNKNOWN_ATTACK = "UNKNOWN_ATTACK"


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class NLILabel(str, Enum):
    ENTAILMENT = "ENTAILMENT"
    CONTRADICTION = "CONTRADICTION"
    NEUTRAL = "NEUTRAL"


class Language(str, Enum):
    ENGLISH = "english"
    HINDI = "hindi"
    MARATHI = "marathi"
    HINGLISH = "hinglish"
    UNKNOWN = "unknown"


# ─────────────────────────────────────────────────────────────────────────────
# Common
# ─────────────────────────────────────────────────────────────────────────────

class TextInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000, description="Input text")
    context: Optional[str] = Field(None, description="Optional context")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @field_validator("text")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return v.strip()


class ValidationResult(BaseModel):
    is_valid: bool
    issues: List[str] = []
    warnings: List[str] = []


# ─────────────────────────────────────────────────────────────────────────────
# NLP Analysis
# ─────────────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    text: str
    lemma: str
    pos: str
    tag: str
    dep: str
    is_stop: bool
    is_punct: bool
    idx: int


class Entity(BaseModel):
    text: str
    label: str
    start: int
    end: int
    description: Optional[str] = None
    confidence: float = 1.0


class DependencyEdge(BaseModel):
    governor: str
    dependent: str
    relation: str
    gov_idx: int
    dep_idx: int


class Sentence(BaseModel):
    text: str
    start: int
    end: int
    tokens: List[Token] = []


class TokenizerComparison(BaseModel):
    simple_tokens: List[str]
    spacy_tokens: List[str]
    bert_tokens: List[str]
    simple_count: int
    spacy_count: int
    bert_count: int


class NLPAnalysisResult(BaseModel):
    text: str
    language: Language
    language_confidence: float
    tokens: List[Token]
    entities: List[Entity]
    sentences: List[Sentence]
    dependencies: List[DependencyEdge]
    tokenizer_comparison: Optional[TokenizerComparison] = None
    pos_distribution: Dict[str, int] = {}
    entity_distribution: Dict[str, int] = {}
    processing_time_ms: float


# ─────────────────────────────────────────────────────────────────────────────
# Security Analysis
# ─────────────────────────────────────────────────────────────────────────────

class RuleMatch(BaseModel):
    pattern_name: str
    pattern: str
    matched_text: str
    attack_type: AttackType
    confidence: float
    position: Optional[int] = None


class FuzzyMatch(BaseModel):
    target_phrase: str
    matched_text: str
    similarity_score: float
    attack_type: AttackType
    technique: str  # "levenshtein", "phonetic", "typoglycemia"


class ObfuscationFlag(BaseModel):
    technique: str
    description: str
    occurrences: List[str]
    severity: float
    positions: List[int] = []


class SemanticMatch(BaseModel):
    reference_text: str
    similarity_score: float
    attack_type: AttackType
    embedding_model: str


class TransformerPrediction(BaseModel):
    attack_type: AttackType
    confidence: float
    all_scores: Dict[str, float]
    model_name: str
    is_mock: bool = False


class LayerScores(BaseModel):
    rules_score: float = 0.0
    fuzzy_score: float = 0.0
    obfuscation_score: float = 0.0
    semantic_score: float = 0.0
    transformer_score: float = 0.0
    language_penalty: float = 0.0


class SecurityResult(BaseModel):
    # Core result
    attack_type: AttackType
    risk_level: RiskLevel
    risk_score: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    should_block: bool
    should_review: bool

    # Layer details
    layer_scores: LayerScores
    rule_matches: List[RuleMatch] = []
    fuzzy_matches: List[FuzzyMatch] = []
    obfuscation_flags: List[ObfuscationFlag] = []
    semantic_matches: List[SemanticMatch] = []
    transformer_prediction: Optional[TransformerPrediction] = None

    # Explainability
    explanation: str
    evidence: List[str] = []
    limitations: List[str] = []

    # Metadata
    processing_time_ms: float
    is_demo: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# Hallucination Analysis
# ─────────────────────────────────────────────────────────────────────────────

class Claim(BaseModel):
    id: str
    text: str
    entities: List[str] = []
    relations: List[Dict[str, str]] = []  # [{subject, predicate, object}]


class Evidence(BaseModel):
    id: str
    text: str
    source: str
    relevance_score: float
    claim_id: str


class NLIResult(BaseModel):
    label: NLILabel
    entailment_score: float
    contradiction_score: float
    neutral_score: float
    model_name: str
    is_mock: bool = False


class ClaimVerification(BaseModel):
    claim: Claim
    evidence_pieces: List[Evidence]
    nli_result: NLIResult
    semantic_similarity: float
    hallucination_risk: float  # 0.0-1.0
    explanation: str
    confidence: float


class SelfConsistencyResult(BaseModel):
    samples: List[str]
    consistency_score: float
    conflicting_claims: List[str] = []
    is_mock: bool = True


class HallucinationResult(BaseModel):
    # Summary
    overall_hallucination_risk: float  # 0.0-1.0
    risk_level: RiskLevel
    total_claims: int
    supported_claims: int
    contradicted_claims: int
    unverified_claims: int

    # Details
    claims: List[ClaimVerification]
    self_consistency: Optional[SelfConsistencyResult] = None

    # Explainability
    explanation: str
    key_findings: List[str] = []

    processing_time_ms: float
    is_demo: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# Full Analysis
# ─────────────────────────────────────────────────────────────────────────────

class AnalyzePromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=50000)
    context: Optional[str] = None
    run_nlp: bool = True
    run_security: bool = True
    generate_response: bool = True

    @field_validator("prompt")
    @classmethod
    def strip_prompt(cls, v: str) -> str:
        return v.strip()


class AnalyzeResponseRequest(BaseModel):
    prompt: Optional[str] = Field(default="", max_length=50000)
    response: str = Field(..., min_length=1, max_length=100000)
    knowledge_base_ids: Optional[List[str]] = None
    run_nli: bool = True
    run_self_consistency: bool = False


class FullAnalysisResult(BaseModel):
    request_id: str
    timestamp: float = Field(default_factory=time.time)

    # Input
    prompt_hash: str
    prompt_preview: str  # First 100 chars

    # Results
    nlp_analysis: Optional[NLPAnalysisResult] = None
    security_result: Optional[SecurityResult] = None
    llm_response: Optional[str] = None
    hallucination_result: Optional[HallucinationResult] = None

    # Summary
    trust_score: float  # Overall trust (0-1)
    recommendation: str
    is_demo: bool = False

    total_processing_time_ms: float


# ─────────────────────────────────────────────────────────────────────────────
# Trust Report
# ─────────────────────────────────────────────────────────────────────────────

class TrustReport(BaseModel):
    request_id: str
    timestamp: float

    prompt_security: str  # HIGH / MEDIUM / LOW
    attack_type: str
    response_groundedness: str
    total_claims: int
    supported_claims: int
    contradicted_claims: int
    unverified_claims: int
    evidence_coverage: float  # 0-1
    hallucination_risk: float  # 0-1
    key_findings: List[str]
    limitations: List[str]
    is_demo: bool = True


# ─────────────────────────────────────────────────────────────────────────────
# Evidence/Retrieval
# ─────────────────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    top_k: int = Field(default=5, ge=1, le=20)
    rerank: bool = True


class SearchResult(BaseModel):
    id: str
    text: str
    source: str
    score: float
    rank: int


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_found: int
    processing_time_ms: float


# ─────────────────────────────────────────────────────────────────────────────
# Knowledge Graph
# ─────────────────────────────────────────────────────────────────────────────

class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    properties: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    weight: float = 1.0
    properties: Dict[str, Any] = {}


class KnowledgeGraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    total_nodes: int
    total_edges: int


# ─────────────────────────────────────────────────────────────────────────────
# Models & Benchmarks
# ─────────────────────────────────────────────────────────────────────────────

class ModelInfo(BaseModel):
    id: str
    name: str
    type: str
    task: str
    loaded: bool
    size_mb: Optional[float] = None
    description: str
    is_mock: bool = False


class BenchmarkDataset(BaseModel):
    id: str
    name: str
    task: str
    size: int
    source: str
    url: Optional[str] = None
    description: str
    metrics: Dict[str, Any] = {}


class ExperimentResult(BaseModel):
    id: str
    name: str
    model: str
    dataset: str
    metrics: Dict[str, float]
    is_demo: bool = True
    notes: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    components: Dict[str, str]
    timestamp: float = Field(default_factory=time.time)
