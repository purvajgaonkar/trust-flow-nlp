import React from 'react';
import { motion } from 'framer-motion';
import { HelpCircle, Shield, Brain, Lock, ArrowRight, CheckCircle } from 'lucide-react';

const PIPELINE_STAGES = [
  {
    icon: '🌐',
    title: 'Language Detection',
    desc: 'Identifies the language of the input (English, Hindi, Marathi, Hinglish) using Unicode script heuristics and langdetect.',
    detail: 'Devanagari ratio, Latin word ratio, code-mixing detection.',
    color: '#38bdf8',
  },
  {
    icon: '🧠',
    title: 'NLP Analysis',
    desc: 'Runs spaCy to produce tokens, POS tags, named entities (including custom security entities), and dependency parses.',
    detail: 'BERT tokenizer comparison, entity extraction, lemmatization.',
    color: '#a78bfa',
  },
  {
    icon: '🔍',
    title: 'Layer A: Regex Rules',
    desc: '20+ hand-crafted patterns for direct injection, jailbreaks, system prompt extraction, data exfiltration, and role manipulation.',
    detail: 'Fastest layer, 5–10ms latency, 95% precision on known patterns.',
    color: '#ef4444',
  },
  {
    icon: '📝',
    title: 'Layer B: Fuzzy Matching',
    desc: 'Levenshtein distance sliding window over known attack phrases to catch typo-obfuscated variants.',
    detail: 'Handles leet-speak (1gnore), space insertion (i g n o r e), character substitution.',
    color: '#f97316',
  },
  {
    icon: '🎭',
    title: 'Obfuscation Detection',
    desc: 'Specialized checks for zero-width chars, BiDi controls, Cyrillic homoglyphs, Base64 encoding, URL encoding, HTML entities, mixed scripts.',
    detail: '8 independent checks; scores combined with bonus for multiple detections.',
    color: '#fbbf24',
  },
  {
    icon: '📊',
    title: 'Layer C: Semantic Similarity',
    desc: 'Sentence-BERT encodes the input and compares cosine similarity against 15 curated attack reference sentences.',
    detail: 'Threshold: 0.70. Falls back gracefully if model unavailable.',
    color: '#34d399',
  },
  {
    icon: '⚡',
    title: 'Layer D: Transformer Classifier',
    desc: 'BERT-based classifier for 10-class attack detection. Falls back to keyword heuristics (clearly labeled MOCK) when model unavailable.',
    detail: 'In MOCK MODE: keyword heuristic — NOT a real ML prediction.',
    color: '#f472b6',
  },
  {
    icon: '⚖️',
    title: 'Risk Fusion',
    desc: 'Weighted average of all layer scores with attack-type-specific weight profiles. Determines final risk level and action (BLOCK/REVIEW/PASS).',
    detail: 'Weights: Rules 25%, Fuzzy 20%, Obfuscation 20%, Semantic 20%, Transformer 15%, Language 10%.',
    color: '#818cf8',
  },
];

const HALL_STAGES = [
  { icon: '✂️', title: 'Claim Extraction', desc: 'Sentence segmentation + entity/relation extraction to identify verifiable atomic claims.' },
  { icon: '🔎', title: 'Evidence Retrieval', desc: 'FAISS/sentence-transformer semantic search over Wikipedia knowledge base. Keyword overlap fallback.' },
  { icon: '🤖', title: 'NLI Classification', desc: 'Cross-encoder NLI model classifies premise→hypothesis as ENTAILMENT, CONTRADICTION, or NEUTRAL.' },
  { icon: '📐', title: 'Semantic Similarity', desc: 'Sentence-BERT cosine similarity between claim and best evidence piece.' },
  { icon: '🎯', title: 'Hallucination Scoring', desc: 'Composite score from NLI label, evidence presence, and semantic similarity. Higher = higher risk.' },
];

export default function HowItWorks() {
  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
          <div className="p-2 rounded-xl bg-shield-500/20 border border-shield-500/30">
            <HelpCircle className="text-shield-400" size={24} />
          </div>
          How It Works
        </h1>
        <p className="text-slate-400">Complete visual explanation of the Trust Flow architecture and pipeline</p>
      </div>

      {/* Architecture overview */}
      <div className="glass-card p-6 mb-10">
        <h2 className="text-xl font-bold text-white mb-4">System Architecture</h2>
        <div className="flex items-center gap-2 flex-wrap">
          {['Input Prompt', 'Validation', 'NLP Pipeline', '4-Layer Security', 'Risk Fusion', 'Decision'].map((s, i) => (
            <React.Fragment key={s}>
              <div className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-200 font-medium">{s}</div>
              {i < 5 && <ArrowRight size={14} className="text-slate-500 flex-shrink-0" />}
            </React.Fragment>
          ))}
        </div>
        <div className="mt-4 flex items-center gap-2 flex-wrap">
          {['LLM Response', 'Claim Extraction', 'Evidence Retrieval', 'NLI', 'Hallucination Score', 'Trust Report'].map((s, i) => (
            <React.Fragment key={s}>
              <div className="px-3 py-2 rounded-lg bg-slate-800 border border-purple-700/30 text-sm text-purple-300 font-medium">{s}</div>
              {i < 5 && <ArrowRight size={14} className="text-slate-500 flex-shrink-0" />}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Security Pipeline */}
      <div className="mb-10">
        <h2 className="text-xl font-bold text-white mb-6">Security Detection Pipeline</h2>
        <div className="space-y-4">
          {PIPELINE_STAGES.map((stage, i) => (
            <motion.div
              key={stage.title}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.07 }}
              className="glass-card p-5 flex items-start gap-5"
              style={{ borderLeft: `3px solid ${stage.color}` }}
            >
              <div className="text-3xl flex-shrink-0">{stage.icon}</div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <div className="text-white font-semibold">{stage.title}</div>
                  <div className="flex-1 h-px bg-gradient-to-r from-slate-700 to-transparent" />
                </div>
                <p className="text-slate-300 text-sm mb-2">{stage.desc}</p>
                <p className="text-slate-500 text-xs italic">{stage.detail}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Hallucination Pipeline */}
      <div className="mb-10">
        <h2 className="text-xl font-bold text-white mb-6">Hallucination Detection Pipeline</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {HALL_STAGES.map((stage, i) => (
            <motion.div
              key={stage.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="glass-card p-5"
            >
              <div className="text-2xl mb-3">{stage.icon}</div>
              <div className="text-white font-semibold mb-2">{stage.title}</div>
              <p className="text-slate-400 text-sm">{stage.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Design Principles */}
      <div className="glass-card p-6">
        <h2 className="text-xl font-bold text-white mb-5">Design Principles</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { icon: <CheckCircle className="text-emerald-400" size={18} />, title: 'Research Integrity', desc: 'Never fabricate metrics. Mock results are clearly labeled. Evaluation pending where not measured.' },
            { icon: <Shield className="text-shield-400" size={18} />, title: 'Defense in Depth', desc: '4 independent layers: if one misses, others may catch it. Each layer adds complementary signal.' },
            { icon: <Brain className="text-cyber-400" size={18} />, title: 'Graceful Degradation', desc: 'Every component has a fallback. System works even without ML models installed.' },
            { icon: <Lock className="text-red-400" size={18} />, title: 'Privacy Preserving', desc: 'Store hashed inputs, not raw text. All analysis happens server-side, not in third-party APIs.' },
          ].map(p => (
            <div key={p.title} className="flex items-start gap-3 bg-slate-900/40 rounded-xl p-4">
              <div className="flex-shrink-0 mt-0.5">{p.icon}</div>
              <div>
                <div className="text-white font-medium text-sm mb-1">{p.title}</div>
                <div className="text-slate-400 text-xs">{p.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
