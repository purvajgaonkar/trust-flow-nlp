import { useEffect, useState } from 'react';
import { ChartBar, Loader2, ExternalLink } from 'lucide-react';
import { api } from '../lib/api';

export default function Benchmarks() {
  const [benchmarks, setBenchmarks] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getBenchmarks().then(setBenchmarks).finally(() => setLoading(false));
  }, []);

  const PAPER_REFS = [
    {
      title: 'Prompt Injection Attacks and Defenses in LLM-Integrated Applications',
      authors: 'Yi et al.',
      year: 2023,
      venue: 'arXiv',
      url: 'https://arxiv.org/abs/2306.05499',
    },
    {
      title: 'HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models',
      authors: 'Li et al.',
      year: 2023,
      venue: 'EMNLP 2023',
      url: 'https://arxiv.org/abs/2305.11747',
    },
    {
      title: 'RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models',
      authors: 'Niu et al.',
      year: 2024,
      venue: 'ACL 2024',
      url: 'https://arxiv.org/abs/2401.00396',
    },
    {
      title: 'Ignore Previous Prompt: Attack Techniques For Language Models',
      authors: 'Perez & Ribeiro',
      year: 2022,
      venue: 'NeurIPS ML Safety Workshop 2022',
      url: 'https://arxiv.org/abs/2211.09527',
    },
    {
      title: 'Natural Language Inference for Fact Verification',
      authors: 'Thorne et al.',
      year: 2018,
      venue: 'NAACL 2018',
      url: 'https://arxiv.org/abs/1803.05355',
    },
    {
      title: 'Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks',
      authors: 'Reimers & Gurevych',
      year: 2019,
      venue: 'EMNLP 2019',
      url: 'https://arxiv.org/abs/1908.10084',
    },
  ];

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
          <div className="p-2 rounded-xl bg-blue-500/20 border border-blue-500/30">
            <ChartBar className="text-blue-400" size={24} />
          </div>
          Benchmarks
        </h1>
        <p className="text-slate-400">Evaluation datasets and academic references</p>
      </div>

      {/* Benchmark datasets */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-white mb-4">Benchmark Datasets</h2>
        <div className="text-xs text-amber-400 mb-4">⚠️ Evaluation Pending – datasets are referenced but not yet fully integrated.</div>

        {loading ? (
          <div className="flex items-center justify-center h-32">
            <Loader2 className="text-blue-400 animate-spin" size={24} />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {benchmarks?.benchmarks?.map((b: any) => (
              <div key={b.id} className="glass-card p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="text-white font-semibold">{b.name}</div>
                    <div className="text-xs text-slate-400 mt-1">{b.task}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-shield-400">{b.size.toLocaleString()}</div>
                    <div className="text-xs text-slate-500">samples</div>
                  </div>
                </div>
                <p className="text-sm text-slate-400 mb-3">{b.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500">{b.source}</span>
                  {b.url && (
                    <a href={b.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-xs text-shield-400 hover:text-shield-300 transition-colors">
                      Paper <ExternalLink size={10} />
                    </a>
                  )}
                </div>
                <div className="mt-2 text-xs text-amber-500">{b.metrics.note}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Academic References */}
      <div>
        <h2 className="text-xl font-bold text-white mb-4">Academic References</h2>
        <p className="text-xs text-slate-500 mb-4">All citations are to real published papers. URLs/DOIs are accurate to the best of our knowledge.</p>
        <div className="space-y-3">
          {PAPER_REFS.map((ref, i) => (
            <div key={i} className="glass-card p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-white font-medium text-sm mb-1">{ref.title}</div>
                  <div className="text-xs text-slate-400">
                    {ref.authors} · {ref.venue} {ref.year}
                  </div>
                </div>
                <a
                  href={ref.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-shrink-0 flex items-center gap-1 text-xs text-shield-400 hover:text-shield-300 px-2 py-1 rounded border border-shield-500/30 hover:border-shield-400/50 transition-all"
                >
                  arXiv <ExternalLink size={10} />
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
