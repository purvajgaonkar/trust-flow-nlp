import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Network, Loader2, Search } from 'lucide-react';
import { api } from '../lib/api';

const NODE_COLORS: Record<string, string> = {
  PERSON: '#fbbf24',
  ORGANIZATION: '#60a5fa',
  PLACE: '#4ade80',
  DATE: '#f472b6',
  CONCEPT: '#a78bfa',
  PRODUCT: '#34d399',
  AWARD: '#fb923c',
  ENTITY: '#94a3b8',
};

export default function KnowledgeGraph() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [entity, setEntity] = useState('');
  const [error, setError] = useState('');
  const [selectedNode, setSelectedNode] = useState<any>(null);

  async function loadGraph(ent?: string) {
    setLoading(true); setError('');
    try {
      const d = await api.getKnowledgeGraph(ent || undefined);
      setData(d);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadGraph(); }, []);

  useEffect(() => {
    if (!data || !svgRef.current) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const W = svgRef.current.clientWidth || 800;
    const H = 500;

    const g = svg.append('g');

    // Zoom
    const zoom = d3.zoom<SVGSVGElement, unknown>().scaleExtent([0.3, 3]).on('zoom', e => {
      g.attr('transform', e.transform.toString());
    });
    svg.call(zoom);

    const nodes = data.nodes.map((n: any) => ({ ...n }));
    const links = data.edges.map((e: any) => ({
      source: e.source,
      target: e.target,
      relation: e.relation,
    }));

    const sim = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(120))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(W / 2, H / 2))
      .force('collision', d3.forceCollide(40));

    // Arrowhead
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 20)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#475569');

    // Links
    const link = g.append('g').selectAll('line')
      .data(links).join('line')
      .attr('stroke', '#334155')
      .attr('stroke-width', 1.5)
      .attr('marker-end', 'url(#arrowhead)');

    // Link labels
    const linkLabel = g.append('g').selectAll('text')
      .data(links).join('text')
      .attr('text-anchor', 'middle')
      .attr('fill', '#64748b')
      .attr('font-size', '9px')
      .attr('font-family', 'JetBrains Mono, monospace')
      .text((d: any) => d.relation);

    // Nodes
    const node = g.append('g').selectAll('circle')
      .data(nodes).join('circle')
      .attr('r', 18)
      .attr('fill', (d: any) => `${NODE_COLORS[d.type] || '#94a3b8'}33`)
      .attr('stroke', (d: any) => NODE_COLORS[d.type] || '#94a3b8')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('click', (_, d: any) => setSelectedNode(d))
      .call(
        d3.drag<SVGCircleElement, any>()
          .on('start', (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
          .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
          .on('end', (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }) as any
      );

    // Node labels
    const label = g.append('g').selectAll('text')
      .data(nodes).join('text')
      .attr('text-anchor', 'middle')
      .attr('dy', 30)
      .attr('fill', '#cbd5e1')
      .attr('font-size', '10px')
      .attr('font-family', 'Inter, sans-serif')
      .text((d: any) => d.label.length > 12 ? d.label.slice(0, 12) + '…' : d.label)
      .style('pointer-events', 'none');

    // Node type indicator
    g.append('g').selectAll('text')
      .data(nodes).join('text')
      .attr('text-anchor', 'middle')
      .attr('fill', (d: any) => NODE_COLORS[d.type] || '#94a3b8')
      .attr('font-size', '10px')
      .attr('font-weight', 'bold')
      .text((d: any) => d.type?.[0] || '?')
      .style('pointer-events', 'none');

    sim.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      linkLabel
        .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
        .attr('y', (d: any) => (d.source.y + d.target.y) / 2);

      node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y);
      label.attr('x', (d: any) => d.x).attr('y', (d: any) => d.y);
      g.selectAll('text:not([dy])').attr('x', (d: any) => (d as any).x).attr('y', (d: any) => (d as any).y + 4);
    });
  }, [data]);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
          <div className="p-2 rounded-xl bg-green-500/20 border border-green-500/30">
            <Network className="text-green-400" size={24} />
          </div>
          Knowledge Graph
        </h1>
        <p className="text-slate-400">Interactive entity-relationship graph (drag nodes, zoom, click to explore)</p>
      </div>

      <div className="glass-card p-4 mb-6 flex items-center gap-3">
        <input
          value={entity}
          onChange={e => setEntity(e.target.value)}
          placeholder="Filter by entity (e.g., 'Elon Musk', 'Tesla')..."
          className="flex-1 bg-slate-900/60 border border-slate-700 rounded-xl p-3 text-slate-200 placeholder-slate-500 text-sm focus:outline-none focus:border-green-500/50"
        />
        <button onClick={() => loadGraph(entity || undefined)} disabled={loading} className="px-4 py-3 bg-green-600/80 hover:bg-green-500/80 text-white rounded-xl flex items-center gap-2 text-sm disabled:opacity-50">
          {loading ? <Loader2 size={14} className="animate-spin" /> : <Search size={14} />}
          Filter
        </button>
        <button onClick={() => { setEntity(''); loadGraph(); }} className="px-4 py-3 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-xl text-sm">
          Show All
        </button>
      </div>

      {error && <div className="glass-card border-red-500/30 bg-red-500/5 p-4 mb-6 text-red-400 text-sm">{error}</div>}

      <div className="glass-card overflow-hidden mb-6">
        {loading ? (
          <div className="h-[500px] flex items-center justify-center">
            <Loader2 className="text-green-400 animate-spin" size={32} />
          </div>
        ) : (
          <svg ref={svgRef} className="w-full h-[500px]" />
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Legend */}
        <div className="glass-card p-5">
          <h3 className="text-white font-semibold mb-3 text-sm">Node Types</h3>
          <div className="flex flex-wrap gap-3">
            {Object.entries(NODE_COLORS).map(([type, color]) => (
              <div key={type} className="flex items-center gap-2 text-xs text-slate-300">
                <div className="w-3 h-3 rounded-full border-2" style={{ borderColor: color, backgroundColor: `${color}33` }} />
                {type}
              </div>
            ))}
          </div>
        </div>

        {/* Selected node info */}
        <div className="glass-card p-5">
          <h3 className="text-white font-semibold mb-3 text-sm">Selected Node</h3>
          {selectedNode ? (
            <div>
              <div className="text-xl font-bold mb-1" style={{ color: NODE_COLORS[selectedNode.type] || '#94a3b8' }}>
                {selectedNode.label}
              </div>
              <div className="text-xs text-slate-400">Type: {selectedNode.type}</div>
              {data && (
                <div className="mt-3 text-xs text-slate-400">
                  <div>Connections: {
                    data.edges.filter((e: any) => e.source === selectedNode.id || e.target === selectedNode.id).length
                  }</div>
                  <div className="mt-2 space-y-1">
                    {data.edges
                      .filter((e: any) => e.source === selectedNode.id || e.target === selectedNode.id)
                      .slice(0, 5)
                      .map((e: any, i: number) => (
                        <div key={i} className="text-slate-500">
                          {e.source === selectedNode.id ? '→' : '←'} <span className="text-slate-400">{e.relation}</span>
                          {' → '}{e.source === selectedNode.id ? e.target : e.source}
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-slate-500 text-sm">Click a node to inspect</div>
          )}
        </div>
      </div>

      {data && (
        <div className="mt-4 flex gap-4 text-xs text-slate-500">
          <span>{data.total_nodes} nodes</span>
          <span>{data.total_edges} relationships</span>
          <span>Drag to rearrange • Scroll to zoom • Click to inspect</span>
        </div>
      )}
    </div>
  );
}
