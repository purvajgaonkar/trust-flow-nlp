import { useState } from 'react';
import { motion } from 'framer-motion';
import { FlaskConical, Loader2, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { api } from '../lib/api';
import { getRiskClass, formatPercent } from '../lib/utils';

const DEMO_RESPONSES = [
  {
    label: 'Accurate',
    prompt: 'When was Tesla founded?',
    response: 'Tesla was founded in July 2003 by Martin Eberhard and Marc Tarpenning. Elon Musk joined as an early investor in 2004.',
  },
  {
    label: 'Hallucinated',
    prompt: 'Tell me about Tesla.',
    response: 'Tesla was founded in 2002 by Elon Musk in Silicon Valley. The company went public in 2009 and has always been profitable.',
  },
  {
    label: 'Contradictory',
    prompt: 'Tell me about Einstein.',
    response: 'Albert Einstein was born in France in 1885. He invented the telephone and never won any scientific awards.',
  },
  {
    label: 'Unsupported',
    prompt: 'Explain quantum entanglement.',
    response: 'Quantum entanglement is caused by dark matter channels that allow particles to communicate faster than light using quantum foam.',
  },
];

const NLI_COLORS: Record<string, string> = {
  ENTAILMENT: '#22c55e',
  CONTRADICTION: '#ef4444',
  NEUTRAL: '#f59e0b',
};

const NLI_ICONS: Record<string, React.ReactNode> = {
  ENTAILMENT: <CheckCircle size={14} className="text-emerald-400" />,
  CONTRADICTION: <XCircle size={14} className="text-red-400" />,
  NEUTRAL: <AlertCircle size={14} className="text-amber-400" />,
};

export default function HallucinationLab() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  async function handleVerify() {
    if (!response.trim()) return;
    setLoading(true); setError(''); setResult(null);
    try {
      const data = await api.verifyResponse(prompt, response);
      setResult(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
          <div className="p-2 rounded-xl bg-pink-500/20 border border-pink-500/30">
            <FlaskConical className="text-pink-400" size={24} />
          </div>
          Hallucination Lab
        </h1>
        <p className="text-slate-400">Verify LLM responses against evidence using NLI and semantic similarity</p>
      </div>

      {/* Demo examples */}
      <div className="glass-card p-4 mb-6">
        <div className="text-xs text-slate-400 mb-3 uppercase tracking-wider">Demo Scenarios (DEMO DATA)</div>
        <div className="flex flex-wrap gap-2">
          {DEMO_RESPONSES.map(d => (
            <button
              key={d.label}
              onClick={() => { setPrompt(d.prompt); setResponse(d.response); }}
              className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
                d.label === 'Accurate' ? 'border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10' :
                d.label === 'Contradictory' || d.label === 'Hallucinated' ? 'border-red-500/30 text-red-400 hover:bg-red-500/10' :
                'border-amber-500/30 text-amber-400 hover:bg-amber-500/10'
              }`}
            >
              {d.label}
            </button>
          ))}
        </div>
      </div>

      {/* Inputs */}
      <div className="glass-card p-6 mb-6 space-y-4">
        <div>
          <label className="text-xs text-slate-400 uppercase tracking-wider mb-2 block">User Prompt (Optional)</label>
          <input
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            placeholder="What was the prompt that generated this response?"
            className="w-full bg-slate-900/60 border border-slate-700 rounded-xl p-3 text-slate-200 placeholder-slate-500 text-sm focus:outline-none focus:border-pink-500/50 transition-colors"
          />
        </div>
        <div>
          <label className="text-xs text-slate-400 uppercase tracking-wider mb-2 block">AI Response to Verify</label>
          <textarea
            value={response}
            onChange={e => setResponse(e.target.value)}
            placeholder="Paste the LLM response to check for hallucinations..."
            rows={5}
            className="w-full bg-slate-900/60 border border-slate-700 rounded-xl p-4 text-slate-200 placeholder-slate-500 text-sm resize-none focus:outline-none focus:border-pink-500/50 transition-colors"
          />
        </div>
        <div className="flex justify-end">
          <button onClick={handleVerify} disabled={loading || !response.trim()} className="px-6 py-3 bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white font-semibold rounded-xl flex items-center gap-2 transition-all disabled:opacity-50">
            {loading ? <Loader2 size={16} className="animate-spin" /> : <FlaskConical size={16} />}
            {loading ? 'Verifying...' : 'Verify Response'}
          </button>
        </div>
      </div>

      {error && <div className="glass-card border-red-500/30 bg-red-500/5 p-4 mb-6 text-red-400 text-sm">{error}</div>}

      {result && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* Summary */}
          <div className={`glass-card p-6 border ${
            result.risk_level === 'SAFE' ? 'border-emerald-500/30 bg-emerald-500/5' :
            result.risk_level === 'HIGH' || result.risk_level === 'CRITICAL' ? 'border-red-500/30 bg-red-500/5' :
            'border-amber-500/30 bg-amber-500/5'
          }`}>
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <span className={`text-sm font-bold px-3 py-1 rounded-full ${getRiskClass(result.risk_level)}`}>
                    {result.risk_level} HALLUCINATION RISK
                  </span>
                </div>
                <p className="text-slate-400 text-sm">{result.explanation}</p>
              </div>
              <div className="text-right">
                <div className="text-4xl font-black" style={{
                  color: result.overall_hallucination_risk > 0.6 ? '#ef4444' : result.overall_hallucination_risk > 0.3 ? '#f59e0b' : '#22c55e'
                }}>
                  {formatPercent(result.overall_hallucination_risk)}
                </div>
                <div className="text-xs text-slate-400 mt-1">Hallucination Risk</div>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-3">
              {[
                { label: 'Total', val: result.total_claims, color: '#94a3b8' },
                { label: 'Supported', val: result.supported_claims, color: '#22c55e' },
                { label: 'Contradicted', val: result.contradicted_claims, color: '#ef4444' },
                { label: 'Unverified', val: result.unverified_claims, color: '#f59e0b' },
              ].map(m => (
                <div key={m.label} className="bg-slate-900/50 rounded-xl p-3 text-center">
                  <div className="text-3xl font-black" style={{ color: m.color }}>{m.val}</div>
                  <div className="text-xs text-slate-400 mt-1">{m.label} Claims</div>
                </div>
              ))}
            </div>
          </div>

          {/* Key Findings */}
          {result.key_findings?.length > 0 && (
            <div className="glass-card p-5 space-y-2">
              <h3 className="text-white font-semibold text-sm mb-3">Key Findings</h3>
              {result.key_findings.map((f: string, i: number) => (
                <div key={i} className="flex items-start gap-2 text-sm text-slate-300">
                  <span className="text-amber-400 mt-0.5">→</span>
                  {f}
                </div>
              ))}
            </div>
          )}

          {/* Claim-by-claim */}
          <div className="glass-card p-6">
            <h3 className="text-white font-semibold mb-5">Claim Verification</h3>
            <div className="space-y-5">
              {result.claims?.map((cv: any, i: number) => (
                <div key={i} className={`rounded-2xl p-5 border ${
                  cv.nli_result.label === 'ENTAILMENT' ? 'border-emerald-500/25 bg-emerald-500/5' :
                  cv.nli_result.label === 'CONTRADICTION' ? 'border-red-500/25 bg-red-500/5' :
                  'border-amber-500/25 bg-amber-500/5'
                }`}>
                  {/* Claim text */}
                  <div className="flex items-start justify-between gap-4 mb-4">
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Claim {i + 1}</div>
                      <div className="text-sm font-medium text-white">{cv.claim.text}</div>
                    </div>
                    <div className="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg" style={{
                      backgroundColor: `${NLI_COLORS[cv.nli_result.label]}15`,
                      border: `1px solid ${NLI_COLORS[cv.nli_result.label]}40`,
                      color: NLI_COLORS[cv.nli_result.label],
                    }}>
                      {NLI_ICONS[cv.nli_result.label]}
                      <span className="text-xs font-bold">{cv.nli_result.label}</span>
                    </div>
                  </div>

                  {/* NLI scores */}
                  <div className="grid grid-cols-3 gap-2 mb-3">
                    {[
                      { label: 'Entailment', val: cv.nli_result.entailment_score, color: '#22c55e' },
                      { label: 'Contradiction', val: cv.nli_result.contradiction_score, color: '#ef4444' },
                      { label: 'Neutral', val: cv.nli_result.neutral_score, color: '#f59e0b' },
                    ].map(s => (
                      <div key={s.label} className="bg-slate-900/40 rounded-lg p-2">
                        <div className="text-xs text-slate-400 mb-1">{s.label}</div>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-slate-800 rounded-full h-1.5">
                            <div className="h-1.5 rounded-full" style={{ width: `${s.val * 100}%`, backgroundColor: s.color }} />
                          </div>
                          <span className="text-xs font-mono" style={{ color: s.color }}>{(s.val * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {cv.nli_result.is_mock && (
                    <div className="text-[10px] text-amber-500 mb-2">⚠️ MOCK/DEMONSTRATION MODE – NLI uses keyword heuristics, not a real NLI model</div>
                  )}

                  {/* Best evidence */}
                  {cv.evidence_pieces?.[0] && (
                    <div className="border-l-2 border-shield-500/50 pl-3">
                      <div className="text-xs text-slate-400 mb-1">
                        Top Evidence (sim: {(cv.semantic_similarity * 100).toFixed(0)}%)
                      </div>
                      <div className="text-xs text-slate-300">{cv.evidence_pieces[0].text}</div>
                      <div className="text-xs text-slate-500 mt-1">Source: {cv.evidence_pieces[0].source}</div>
                    </div>
                  )}

                  <div className="mt-3 text-xs text-slate-400 flex items-center gap-1.5">
                    <span>Hallucination Risk: </span>
                    <span className="font-mono font-bold" style={{
                      color: cv.hallucination_risk > 0.6 ? '#ef4444' : cv.hallucination_risk > 0.3 ? '#f59e0b' : '#22c55e'
                    }}>
                      {formatPercent(cv.hallucination_risk)}
                    </span>
                    <span>•</span>
                    <span>{cv.explanation}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
