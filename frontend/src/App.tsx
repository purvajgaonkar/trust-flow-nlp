import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Brain, Lock, ChartBar, Network, Beaker, Swords, Trophy, HelpCircle, Activity, FlaskConical, Search } from 'lucide-react';

// Pages
import Home from './pages/Home';
import Analyze from './pages/Analyze';
import NLPExplorer from './pages/NLPExplorer';
import SecurityLab from './pages/SecurityLab';
import HallucinationLab from './pages/HallucinationLab';
import EvidenceLab from './pages/EvidenceLab';
import ResearchLab from './pages/ResearchLab';
import Benchmarks from './pages/Benchmarks';
import KnowledgeGraph from './pages/KnowledgeGraph';
import AttackLab from './pages/AttackLab';
import CompetitionMode from './pages/CompetitionMode';
import HowItWorks from './pages/HowItWorks';

type Page =
  | 'home' | 'analyze' | 'nlp' | 'security' | 'hallucination'
  | 'evidence' | 'research' | 'benchmarks' | 'graph' | 'attacks'
  | 'competition' | 'howto';

const NAV_ITEMS: { id: Page; label: string; icon: React.ReactNode; group: string }[] = [
  { id: 'home', label: 'Home', icon: <Shield size={16} />, group: 'main' },
  { id: 'analyze', label: 'Analyze', icon: <Activity size={16} />, group: 'main' },
  { id: 'howto', label: 'How It Works', icon: <HelpCircle size={16} />, group: 'main' },
  { id: 'nlp', label: 'NLP Explorer', icon: <Brain size={16} />, group: 'tools' },
  { id: 'security', label: 'Security Lab', icon: <Lock size={16} />, group: 'tools' },
  { id: 'hallucination', label: 'Hallucination Lab', icon: <FlaskConical size={16} />, group: 'tools' },
  { id: 'evidence', label: 'Evidence Lab', icon: <Search size={16} />, group: 'tools' },
  { id: 'attacks', label: 'Attack Lab', icon: <Swords size={16} />, group: 'tools' },
  { id: 'graph', label: 'Knowledge Graph', icon: <Network size={16} />, group: 'research' },
  { id: 'research', label: 'Research Lab', icon: <Beaker size={16} />, group: 'research' },
  { id: 'benchmarks', label: 'Benchmarks', icon: <ChartBar size={16} />, group: 'research' },
  { id: 'competition', label: 'Competition Mode', icon: <Trophy size={16} />, group: 'special' },
];

export default function App() {
  const [page, setPage] = useState<Page>('home');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const navigate = (p: string) => setPage(p as Page);

  useEffect(() => {
    fetch('http://localhost:8000/api/health')
      .then(r => r.ok ? setBackendStatus('online') : setBackendStatus('offline'))
      .catch(() => setBackendStatus('offline'));
  }, []);

  const groups = {
    main: NAV_ITEMS.filter(n => n.group === 'main'),
    tools: NAV_ITEMS.filter(n => n.group === 'tools'),
    research: NAV_ITEMS.filter(n => n.group === 'research'),
    special: NAV_ITEMS.filter(n => n.group === 'special'),
  };

  const renderPage = () => {
    const pages: Record<Page, React.ReactNode> = {
      home: <Home onNavigate={navigate} />,
      analyze: <Analyze />,
      nlp: <NLPExplorer />,
      security: <SecurityLab />,
      hallucination: <HallucinationLab />,
      evidence: <EvidenceLab />,
      research: <ResearchLab />,
      benchmarks: <Benchmarks />,
      graph: <KnowledgeGraph />,
      attacks: <AttackLab />,
      competition: <CompetitionMode />,
      howto: <HowItWorks />,
    };
    return pages[page];
  };

  if (page === 'competition') {
    return (
      <AnimatePresence mode="wait">
        <motion.div key="competition" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <CompetitionMode onExit={() => setPage('home')} />
        </motion.div>
      </AnimatePresence>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-slate-950">
      {/* Sidebar */}
      <motion.aside
        initial={{ width: sidebarOpen ? 240 : 64 }}
        animate={{ width: sidebarOpen ? 240 : 64 }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="flex-shrink-0 bg-slate-900/90 border-r border-slate-800 flex flex-col overflow-hidden z-20"
      >
        {/* Logo */}
        <div className="p-4 flex items-center gap-3 border-b border-slate-800">
          <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-shield-500 to-cyber-600 flex items-center justify-center shadow-lg glow-blue">
            <Shield size={20} className="text-white" />
          </div>
          {sidebarOpen && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <div className="font-bold text-white text-sm">Trust Flow</div>
              <div className="text-[10px] text-slate-400">NLP Security Framework</div>
            </motion.div>
          )}
        </div>

        {/* Backend status */}
        {sidebarOpen && (
          <div className="px-4 py-2 flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
              backendStatus === 'online' ? 'bg-emerald-500 shadow-[0_0_6px_rgba(34,197,94,0.6)]' :
              backendStatus === 'offline' ? 'bg-red-500 shadow-[0_0_6px_rgba(239,68,68,0.6)]' :
              'bg-amber-500 animate-pulse'
            }`} />
            <span className="text-[10px] text-slate-400">
              Backend: {backendStatus === 'checking' ? 'Connecting...' : backendStatus === 'online' ? 'Online' : 'Offline (Demo Mode)'}
            </span>
          </div>
        )}

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto p-3 space-y-4">
          {(Object.entries(groups) as [string, typeof NAV_ITEMS][] ).map(([groupKey, items]) => (
            <div key={groupKey}>
              {sidebarOpen && (
                <div className="px-2 mb-1 text-[10px] text-slate-500 uppercase tracking-widest font-medium">
                  {groupKey === 'main' ? 'Navigation' : groupKey === 'tools' ? 'Analysis Tools' : groupKey === 'research' ? 'Research' : 'Demo'}
                </div>
              )}
              <div className="space-y-1">
                {items.map(item => (
                  <button
                    key={item.id}
                    onClick={() => setPage(item.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all duration-200 group ${
                      page === item.id
                        ? 'bg-gradient-to-r from-shield-600/30 to-cyber-600/20 text-shield-300 border border-shield-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                    } ${item.id === 'competition' ? 'border border-amber-500/30 text-amber-400 hover:bg-amber-500/10' : ''}`}
                    title={!sidebarOpen ? item.label : undefined}
                  >
                    <span className={`flex-shrink-0 transition-transform duration-200 group-hover:scale-110 ${
                      page === item.id ? 'text-shield-400' : ''
                    } ${item.id === 'competition' ? 'text-amber-400' : ''}`}>
                      {item.icon}
                    </span>
                    {sidebarOpen && (
                      <span className="text-xs font-medium truncate">{item.label}</span>
                    )}
                    {sidebarOpen && page === item.id && (
                      <motion.div layoutId="active-indicator" className="ml-auto w-1.5 h-1.5 rounded-full bg-shield-400" />
                    )}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </nav>

        {/* Toggle sidebar button */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-4 text-slate-500 hover:text-slate-300 transition-colors border-t border-slate-800 text-xs flex items-center gap-2"
        >
          <span>{sidebarOpen ? '◀' : '▶'}</span>
          {sidebarOpen && <span>Collapse</span>}
        </button>
      </motion.aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <AnimatePresence mode="wait">
          <motion.div
            key={page}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            className="min-h-full"
          >
            {renderPage()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
