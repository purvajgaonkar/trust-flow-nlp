import { useEffect, useState } from 'react';
import { Beaker, Loader2, AlertTriangle, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../lib/api';

export default function ResearchLab() {
  const [experiments, setExperiments] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<'ablation_injection' | 'ablation_hallucination' | 'model_comparison'>('model_comparison');

  useEffect(() => {
    api.getExperiments().then(setExperiments).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-96">
        <Loader2 className="text-cyber-400 animate-spin" size={32} />
      </div>
    );
  }

  const TOOLTIP_STYLE = {
    backgroundColor: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '8px',
    color: '#cbd5e1',
    fontSize: '12px',
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
          <div className="p-2 rounded-xl bg-cyber-500/20 border border-cyber-500/30">
            <Beaker className="text-cyber-400" size={24} />
          </div>
          Research Lab
        </h1>
        <p className="text-slate-400">Model comparisons, ablation studies, and evaluation metrics</p>
      </div>

      {experiments && (
        <div className="glass-card p-4 border-amber-500/30 bg-amber-500/5 mb-6 flex items-start gap-3">
          <AlertTriangle size={16} className="text-amber-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-amber-300">
            <strong>DEMO DATA</strong> – All metrics below are for illustration purposes only. 
            Real evaluation requires running models against benchmark datasets (HaluEval, PINT, etc.) which are pending integration.
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {[
          { key: 'model_comparison', label: 'Model Comparison' },
          { key: 'ablation_injection', label: 'Ablation: Injection' },
          { key: 'ablation_hallucination', label: 'Ablation: Hallucination' },
        ].map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key as any)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === t.key
                ? 'bg-cyber-600/30 text-cyber-300 border border-cyber-500/40'
                : 'text-slate-400 hover:text-slate-200 border border-slate-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'model_comparison' && experiments && (
        <div className="space-y-6">
          <div className="glass-card p-6">
            <h3 className="text-white font-semibold mb-5 flex items-center gap-2">
              <TrendingUp size={16} className="text-cyber-400" />
              Model Comparison – F1 Score (DEMO DATA)
            </h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={experiments.model_comparison} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="model" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <YAxis domain={[0, 1]} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Bar dataKey="f1" fill="#0ea5e9" name="F1 Score" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="roc_auc" fill="#8b5cf6" name="ROC-AUC" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-card p-6">
            <h3 className="text-white font-semibold mb-5">Latency Comparison (ms) – DEMO DATA</h3>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={experiments.model_comparison}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="model" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Bar dataKey="latency_ms" fill="#f97316" name="Latency (ms)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Table */}
          <div className="glass-card p-6 overflow-x-auto">
            <h3 className="text-white font-semibold mb-4">Full Results Table – DEMO DATA</h3>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-slate-400 border-b border-slate-700">
                  <th className="pb-3 pr-4">Model</th>
                  <th className="pb-3 pr-4">F1</th>
                  <th className="pb-3 pr-4">ROC-AUC</th>
                  <th className="pb-3">Latency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {experiments.model_comparison.map((m: any) => (
                  <tr key={m.model} className="text-slate-300 hover:bg-slate-800/30">
                    <td className="py-2.5 pr-4 font-medium">{m.model}</td>
                    <td className="py-2.5 pr-4 font-mono" style={{ color: m.f1 > 0.85 ? '#22c55e' : m.f1 > 0.75 ? '#f59e0b' : '#94a3b8' }}>
                      {m.f1.toFixed(2)}
                    </td>
                    <td className="py-2.5 pr-4 font-mono text-slate-400">{m.roc_auc.toFixed(2)}</td>
                    <td className="py-2.5 font-mono text-slate-400">{m.latency_ms}ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'ablation_injection' && experiments && (
        <div className="space-y-6">
          <div className="glass-card p-6">
            <h3 className="text-white font-semibold mb-5">Ablation Study – Prompt Injection Detection (DEMO DATA)</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={experiments.ablation_prompt_injection}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <YAxis domain={[0, 1]} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Bar dataKey="f1" fill="#ef4444" name="F1" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="precision" fill="#f97316" name="Precision" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="recall" fill="#fbbf24" name="Recall" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-slate-400 border-b border-slate-700">
                    <th className="pb-2 pr-4">Configuration</th>
                    <th className="pb-2 pr-4">F1</th>
                    <th className="pb-2 pr-4">Precision</th>
                    <th className="pb-2 pr-4">Recall</th>
                    <th className="pb-2">Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {experiments.ablation_prompt_injection.map((r: any) => (
                    <tr key={r.name} className="text-slate-300 hover:bg-slate-800/30">
                      <td className="py-2 pr-4 text-xs">{r.name}</td>
                      <td className="py-2 pr-4 font-mono text-xs" style={{ color: r.f1 > 0.85 ? '#22c55e' : '#f59e0b' }}>{r.f1}</td>
                      <td className="py-2 pr-4 font-mono text-xs text-slate-400">{r.precision}</td>
                      <td className="py-2 pr-4 font-mono text-xs text-slate-400">{r.recall}</td>
                      <td className="py-2 font-mono text-xs text-slate-400">{r.latency_ms}ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {tab === 'ablation_hallucination' && experiments && (
        <div className="space-y-6">
          <div className="glass-card p-6">
            <h3 className="text-white font-semibold mb-5">Ablation Study – Hallucination Detection (DEMO DATA)</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={experiments.ablation_hallucination}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <YAxis domain={[0, 1]} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Bar dataKey="f1" fill="#a78bfa" name="F1" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="precision" fill="#60a5fa" name="Precision" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="recall" fill="#34d399" name="Recall" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
