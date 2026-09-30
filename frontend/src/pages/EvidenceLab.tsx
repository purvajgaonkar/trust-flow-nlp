import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Loader2, Database } from 'lucide-react';
import { api } from '../lib/api';

export default function EvidenceLab() {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const SAMPLES = [
    'When was Tesla founded?',
    'Who built the Eiffel Tower?',
    'Albert Einstein Nobel Prize',
    'Python programming language creator',
    'ChatGPT release date',
  ];

  async function handleSearch() {
    if (!query.trim()) return;
    setLoading(true); setError(''); setResult(null);
    try {
      const data = await api.searchEvidence(query, topK);
      setResult(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
          <div className="p-2 rounded-xl bg-cyan-500/20 border border-cyan-500/30">
            <Search className="text-cyan-400" size={24} />
          </div>
          Evidence Lab
        </h1>
        <p className="text-slate-400">Search the knowledge base for evidence to support or contradict claims</p>
      </div>

      <div className="glass-card p-4 mb-6">
        <div className="text-xs text-slate-400 mb-3">Knowledge base sources (Wikipedia snippets):</div>
        <div className="flex flex-wrap gap-2 text-xs text-slate-400">
          {['Tesla, Inc.', 'Eiffel Tower', 'Albert Einstein', 'Python (language)', 'ChatGPT', 'Great Wall', 'Moon', 'Water (chemistry)'].map(s => (
            <span key={s} className="px-2 py-1 bg-slate-800 rounded border border-slate-700">{s}</span>
          ))}
        </div>
      </div>

      <div className="glass-card p-6 mb-6">
        <div className="flex gap-2 flex-wrap mb-3">
          {SAMPLES.map(s => (
            <button key={s} onClick={() => setQuery(s)} className="text-xs px-2 py-1 rounded border border-slate-600 text-slate-400 hover:text-slate-200 hover:border-slate-500 transition-colors">
              {s}
            </button>
          ))}
        </div>
        <div className="flex gap-3">
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="Search for evidence..."
            className="flex-1 bg-slate-900/60 border border-slate-700 rounded-xl p-3 text-slate-200 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500/50 transition-colors"
          />
          <select
            value={topK}
            onChange={e => setTopK(Number(e.target.value))}
            className="bg-slate-900/60 border border-slate-700 rounded-xl p-3 text-slate-200 text-sm focus:outline-none"
          >
            {[3, 5, 8, 10].map(k => <option key={k} value={k}>Top {k}</option>)}
          </select>
          <button onClick={handleSearch} disabled={loading || !query.trim()} className="px-5 py-3 bg-gradient-to-r from-cyan-600 to-shield-600 text-white font-semibold rounded-xl flex items-center gap-2 transition-all disabled:opacity-50 hover:scale-105">
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
            Search
          </button>
        </div>
      </div>

      {error && <div className="glass-card border-red-500/30 bg-red-500/5 p-4 mb-6 text-red-400 text-sm">{error}</div>}

      {result && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">
              {result.total_found} results for "<span className="text-slate-200">{result.query}</span>"
            </span>
            <span className="text-slate-500">{result.processing_time_ms?.toFixed(0)}ms</span>
          </div>

          {result.results?.map((r: any, i: number) => (
            <motion.div
              key={r.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              className="glass-card p-5"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-600 flex items-center justify-center text-xs font-bold text-slate-300">
                    {r.rank || i + 1}
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 flex items-center gap-1.5">
                      <Database size={10} />
                      {r.source}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="text-right">
                    <div className="text-sm font-bold" style={{
                      color: r.relevance_score > 0.7 ? '#22c55e' : r.relevance_score > 0.4 ? '#f59e0b' : '#94a3b8'
                    }}>
                      {(r.relevance_score * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-slate-500">Relevance</div>
                  </div>
                </div>
              </div>

              <p className="text-sm text-slate-300 leading-relaxed">{r.text}</p>

              <div className="mt-3 flex items-center gap-2">
                <div className="flex-1 bg-slate-800 rounded-full h-1.5">
                  <div
                    className="h-1.5 rounded-full bg-gradient-to-r from-shield-500 to-cyan-500"
                    style={{ width: `${r.relevance_score * 100}%` }}
                  />
                </div>
                <span className="text-xs text-slate-500 font-mono">{r.relevance_score?.toFixed(4)}</span>
              </div>
            </motion.div>
          ))}

          {result.results?.length === 0 && (
            <div className="glass-card p-8 text-center">
              <Database className="mx-auto text-slate-600 mb-3" size={32} />
              <div className="text-slate-400">No relevant evidence found in the knowledge base.</div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}
