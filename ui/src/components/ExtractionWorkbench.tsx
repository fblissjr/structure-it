import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronDown } from 'lucide-react';

// Generic Interfaces
interface Highlight { id: string; start: number; end: number; text?: string; }
interface Props { 
  rawText: string; 
  data: any; 
  highlights: Highlight[]; 
  onOpenGraph: () => void;
}

// --- GENERIC DATA NODE COMPONENT ---
const GenericDataNode: React.FC<{ 
  data: any; 
  label?: string; 
  path: string;
  activeId: string | null;
  setActiveId: (id: string | null) => void;
}> = ({ data, label, path, activeId, setActiveId }) => {
  const [isOpen, setIsOpen] = useState(true);

  // 1. Handle Primitives (Leaf Nodes)
  if (typeof data !== 'object' || data === null) {
    const isHighlightable = typeof data === 'string' && data.length > 10;
    const isActive = activeId === path;

    return (
      <div 
        id={`card-${path}`}
        className={`
          ml-4 mb-2 p-2 rounded border-l-2 transition-all
          ${isActive 
            ? 'bg-neon-purple/20 border-neon-purple shadow-glow-purple' 
            : 'border-slate-800 hover:border-slate-700'}
          ${isHighlightable ? 'cursor-pointer' : ''}
        `}
        onMouseEnter={() => isHighlightable && setActiveId(path)}
        onMouseLeave={() => isHighlightable && setActiveId(null)}
      >
        <div className="flex items-start gap-2">
          <span className="text-xs font-mono text-slate-500 mt-0.5">{label}:</span>
          <span className={`text-sm break-words font-mono ${isActive ? 'text-neon-blue' : 'text-slate-300'}`}>
             {String(data)}
          </span>
        </div>
      </div>
    );
  }

  // 2. Handle Arrays and Objects (Container Nodes)
  const isArray = Array.isArray(data);
  const entries = Object.entries(data);

  if (entries.length === 0) return null;

  return (
    <div className="ml-4 mb-2">
      <div 
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 cursor-pointer text-slate-400 hover:text-neon-blue mb-1 select-none transition-colors"
      >
        {isOpen ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
        <span className="text-xs font-bold uppercase tracking-wider font-display">
          {label || (isArray ? 'List' : 'Object')} 
          <span className="text-slate-600 ml-2 font-normal font-mono">
            {isArray ? `[${entries.length}]` : '{...}'}
          </span>
        </span>
      </div>
      
      {isOpen && (
        <div className="border-l border-white/5 pl-2">
          {entries.map(([key, value]) => (
            <GenericDataNode
              key={key}
              label={isArray ? `#${key}` : key}
              data={value}
              path={path ? (isArray ? `${path}[${key}]` : `${path}.${key}`) : key}
              activeId={activeId}
              setActiveId={setActiveId}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const ExtractionWorkbench: React.FC<Props> = ({ rawText, data, highlights, onOpenGraph }) => {
  const [activeId, setActiveId] = useState<string | null>(null);

  // --- X-RAY RENDERING LOGIC ---
  const renderDocument = () => {
    const sortedHighlights = [...highlights].sort((a, b) => a.start - b.start);
    const nodes = [];
    let cursor = 0;

    sortedHighlights.forEach((h) => {
      // Text before highlight
      if (h.start > cursor) nodes.push(<span key={`text-${cursor}`}>{rawText.slice(cursor, h.start)}</span>);

      // The Highlighted Span
      const isActive = activeId === h.id; 
      
      nodes.push(
        <span
          key={`${h.id}-${h.start}`}
          id={`source-${h.id}`}
          onMouseEnter={() => setActiveId(h.id)}
          className={`
            transition-all duration-200 cursor-pointer border-b-2 rounded px-0.5
            ${isActive
              ? 'bg-neon-yellow/20 border-neon-yellow text-neon-yellow shadow-glow-blue'
              : 'bg-neon-blue/5 border-neon-blue/20 hover:bg-neon-blue/10 text-slate-200'}
          `}
        >
          {rawText.slice(h.start, h.end)}
        </span>
      );
      cursor = h.end;
    });

    if (cursor < rawText.length) nodes.push(<span key="text-end">{rawText.slice(cursor)}</span>);
    return <div className="font-mono text-sm leading-relaxed whitespace-pre-wrap text-slate-400">{nodes}</div>;
  };

  // Auto-scroll logic
  useEffect(() => {
    if (activeId) {
      // Scroll Document
      document.getElementById(`source-${activeId}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      // Scroll Card
      document.getElementById(`card-${activeId}`)?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [activeId]);

  const isPolicy = !!data.requirements;

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* LEFT: Document Canvas */}
      <div className="w-1/2 bg-slate-950/50 overflow-y-auto p-8 border-r border-white/5 shadow-inner custom-scrollbar">
        <div className="max-w-3xl mx-auto">{renderDocument()}</div>
      </div>

      {/* RIGHT: Data Form */}
      <div className="w-1/2 bg-slate-900/30 overflow-y-auto p-6 custom-scrollbar">
        <div className="max-w-2xl mx-auto space-y-4">
          
          {/* MODE: SPECIALIZED POLICY VIEW */}
          {isPolicy ? (
             data.requirements.map((req: any) => (
              <div
                key={req.requirement_id}
                id={`card-${req.requirement_id}`}
                onMouseEnter={() => setActiveId(req.requirement_id)}
                className={`
                  glass-panel p-4 rounded-xl transition-all duration-300 border-l-4
                  ${activeId === req.requirement_id 
                    ? 'border-l-neon-purple translate-x-2 shadow-glow-purple bg-slate-900/80' 
                    : 'border-l-transparent hover:bg-white/5'}
                `}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-slate-500">{req.requirement_id}</span>
                  <span className={`text-xs font-bold px-2 py-1 rounded-full uppercase tracking-wider font-display ${
                    req.requirement_type === 'mandatory' 
                        ? 'bg-neon-pink/10 text-neon-pink border border-neon-pink/20' 
                        : 'bg-neon-green/10 text-neon-green border border-neon-green/20'
                  }`}>
                    {req.requirement_type}
                  </span>
                </div>
                <p className="text-sm text-slate-200 font-sans">{req.statement}</p>
              </div>
            ))
          ) : (
            /* MODE: GENERIC TREE VIEW */
            <div className="glass-panel p-6 rounded-xl border-neon-blue/20">
                <h3 className="text-lg font-bold mb-4 text-neon-blue border-b border-white/10 pb-2 font-display tracking-widest">Extracted Data</h3>
                <GenericDataNode 
                    data={data} 
                    path="" 
                    activeId={activeId} 
                    setActiveId={setActiveId} 
                />
            </div>
          )}

          {/* Common Controls */}
          <div className="pt-4 flex justify-end">
            <button
              onClick={onOpenGraph}
              className="px-6 py-3 bg-neon-blue/10 hover:bg-neon-blue/20 text-neon-blue border border-neon-blue/50 rounded-lg shadow-glow-blue transition-all flex items-center gap-2 font-display tracking-wider uppercase text-sm font-bold backdrop-blur-md"
            >
              <span className="text-lg">⚡</span> Open Constellation View
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
