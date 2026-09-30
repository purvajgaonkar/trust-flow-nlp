// TypeScript types matching backend Pydantic schemas

export type AttackType =
  | 'SAFE'
  | 'DIRECT_INJECTION'
  | 'INDIRECT_INJECTION'
  | 'JAILBREAK'
  | 'SYSTEM_PROMPT_EXTRACTION'
  | 'DATA_EXFILTRATION'
  | 'ROLE_MANIPULATION'
  | 'OBFUSCATION'
  | 'MULTILINGUAL_ATTACK'
  | 'UNKNOWN_ATTACK';

export type RiskLevel = 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type NLILabel = 'ENTAILMENT' | 'CONTRADICTION' | 'NEUTRAL';
export type Language = 'english' | 'hindi' | 'marathi' | 'hinglish' | 'unknown';

// NLP
export interface Token {
  text: string;
  lemma: string;
  pos: string;
  tag: string;
  dep: string;
  is_stop: boolean;
  is_punct: boolean;
  idx: number;
}

export interface Entity {
  text: string;
  label: string;
  start: number;
  end: number;
  description?: string;
  confidence: number;
}

export interface DependencyEdge {
  governor: string;
  dependent: string;
  relation: string;
  gov_idx: number;
  dep_idx: number;
}

export interface Sentence {
  text: string;
  start: number;
  end: number;
  tokens: Token[];
}

export interface TokenizerComparison {
  simple_tokens: string[];
  spacy_tokens: string[];
  bert_tokens: string[];
  simple_count: number;
  spacy_count: number;
  bert_count: number;
}

export interface NLPAnalysisResult {
  text: string;
  language: Language;
  language_confidence: number;
  tokens: Token[];
  entities: Entity[];
  sentences: Sentence[];
  dependencies: DependencyEdge[];
  tokenizer_comparison?: TokenizerComparison;
  pos_distribution: Record<string, number>;
  entity_distribution: Record<string, number>;
  processing_time_ms: number;
}

// Security
export interface RuleMatch {
  pattern_name: string;
  pattern: string;
  matched_text: string;
  attack_type: AttackType;
  confidence: number;
  position?: number;
}

export interface FuzzyMatch {
  target_phrase: string;
  matched_text: string;
  similarity_score: number;
  attack_type: AttackType;
  technique: string;
  effective_confidence: number;
}

export interface ObfuscationFlag {
  technique: string;
  description: string;
  occurrences: string[];
  severity: number;
  positions: number[];
}

export interface SemanticMatch {
  reference_text: string;
  similarity_score: number;
  attack_type: AttackType;
  embedding_model: string;
  effective_confidence: number;
}

export interface TransformerPrediction {
  attack_type: AttackType;
  confidence: number;
  all_scores: Record<string, number>;
  model_name: string;
  is_mock: boolean;
}

export interface LayerScores {
  rules_score: number;
  fuzzy_score: number;
  obfuscation_score: number;
  semantic_score: number;
  transformer_score: number;
  language_penalty: number;
}

export interface SecurityResult {
  attack_type: AttackType;
  risk_level: RiskLevel;
  risk_score: number;
  confidence: number;
  should_block: boolean;
  should_review: boolean;
  layer_scores: LayerScores;
  rule_matches: RuleMatch[];
  fuzzy_matches: FuzzyMatch[];
  obfuscation_flags: ObfuscationFlag[];
  semantic_matches: SemanticMatch[];
  transformer_prediction?: TransformerPrediction;
  explanation: string;
  evidence: string[];
  limitations: string[];
  processing_time_ms: number;
  is_demo: boolean;
}

// Hallucination
export interface Claim {
  id: string;
  text: string;
  entities: string[];
  relations: { subject: string; predicate: string; object: string }[];
}

export interface Evidence {
  id: string;
  text: string;
  source: string;
  relevance_score: number;
  claim_id: string;
  rank?: number;
}

export interface NLIResult {
  label: NLILabel;
  entailment_score: number;
  contradiction_score: number;
  neutral_score: number;
  model_name: string;
  is_mock: boolean;
}

export interface ClaimVerification {
  claim: Claim;
  evidence_pieces: Evidence[];
  nli_result: NLIResult;
  semantic_similarity: number;
  hallucination_risk: number;
  explanation: string;
  confidence: number;
}

export interface HallucinationResult {
  overall_hallucination_risk: number;
  risk_level: RiskLevel;
  total_claims: number;
  supported_claims: number;
  contradicted_claims: number;
  unverified_claims: number;
  claims: ClaimVerification[];
  explanation: string;
  key_findings: string[];
  processing_time_ms: number;
  is_demo: boolean;
}

// Full Analysis
export interface FullAnalysisResult {
  request_id: string;
  timestamp: number;
  prompt_hash: string;
  prompt_preview: string;
  nlp_analysis?: NLPAnalysisResult;
  security_result?: SecurityResult;
  llm_response?: string;
  hallucination_result?: HallucinationResult;
  trust_score: number;
  recommendation: string;
  is_demo: boolean;
  total_processing_time_ms: number;
}

// Knowledge Graph
export interface GraphNode {
  id: string;
  label: string;
  type: string;
  properties: Record<string, unknown>;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation: string;
  weight: number;
  properties: Record<string, unknown>;
}

export interface KnowledgeGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  total_nodes: number;
  total_edges: number;
}

// Models
export interface ModelInfo {
  id: string;
  name: string;
  type: string;
  task: string;
  loaded: boolean;
  size_mb?: number;
  description: string;
  is_mock: boolean;
}

// Demo Scenarios
export interface DemoScenario {
  id: number;
  name: string;
  type: string;
  prompt: string;
  response?: string;
  expected_risk?: string;
  expected_hallucination_risk?: string;
  description: string;
}

// Health
export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  components: Record<string, string>;
  timestamp: number;
}
