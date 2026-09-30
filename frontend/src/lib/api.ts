// API client for Trust Flow backend

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    let msg = 'API Error';
    if (typeof err.detail === 'string') {
      msg = err.detail;
    } else if (Array.isArray(err.detail)) {
      msg = err.detail.map((d: any) => d.msg || `${d.loc?.join('.')}: ${d.type}`).join(', ');
    } else if (err.detail) {
      msg = JSON.stringify(err.detail);
    } else {
      msg = `API error ${res.status}`;
    }
    throw new Error(msg);
  }
  return res.json();
}

export const api = {
  // Health
  health: () => request<any>('/health'),

  // Full analysis
  analyzePrompt: (prompt: string, context?: string) =>
    request<any>('/analyze/prompt', {
      method: 'POST',
      body: JSON.stringify({ prompt, context, run_nlp: true, run_security: true, generate_response: true }),
    }),

  analyzeResponse: (prompt: string, response: string) =>
    request<any>('/analyze/response', {
      method: 'POST',
      body: JSON.stringify({ prompt, response, run_nli: true }),
    }),

  // Security
  detectInjection: (text: string) =>
    request<any>('/security/injection', {
      method: 'POST',
      body: JSON.stringify({ text }),
    }),

  detectObfuscation: (text: string) =>
    request<any>('/security/obfuscation', {
      method: 'POST',
      body: JSON.stringify({ text }),
    }),

  // Hallucination
  extractClaims: (text: string) =>
    request<any>('/hallucination/claims', {
      method: 'POST',
      body: JSON.stringify({ text }),
    }),

  verifyResponse: (prompt: string, response: string) =>
    request<any>('/hallucination/verify', {
      method: 'POST',
      body: JSON.stringify({ prompt, response }),
    }),

  // NLP
  nlpAnalyze: (text: string) =>
    request<any>('/nlp/analyze', {
      method: 'POST',
      body: JSON.stringify({ text }),
    }),

  // Retrieval
  searchEvidence: (query: string, top_k = 5) =>
    request<any>('/retrieval/search', {
      method: 'POST',
      body: JSON.stringify({ query, top_k, rerank: true }),
    }),

  // Knowledge graph
  getKnowledgeGraph: (entity?: string) => {
    const qs = entity ? `?entity=${encodeURIComponent(entity)}` : '';
    return request<any>(`/knowledge-graph${qs}`);
  },

  // Research
  getModels: () => request<any>('/models'),
  getBenchmarks: () => request<any>('/benchmarks'),
  getExperiments: () => request<any>('/experiments'),
  getDemoScenarios: () => request<any>('/demo/scenarios'),

  // Document upload
  analyzeDocument: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return fetch(`${BASE_URL}/analyze/document`, { method: 'POST', body: form }).then(r => {
      if (!r.ok) throw new Error(`Upload failed: ${r.statusText}`);
      return r.json();
    });
  },
};
