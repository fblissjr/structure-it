import React, { useState, useEffect } from 'react';
// CheckCircle2 and AlertCircle were imported in the prompt but unused. I'm removing them to pass the build.
// import { CheckCircle2, AlertCircle } from 'lucide-react';

// Define the Types based on the Python API response
interface Highlight { id: string; start: number; end: number; }
interface Requirement { requirement_id: string; statement: string; requirement_type: string; }
interface Props { rawText: string; data: { requirements: Requirement[] }; highlights: Highlight[]; }

export const ExtractionWorkbench: React.FC<Props> = ({ rawText, data, highlights }) => {
  const [activeId, setActiveId] = useState<string | null>(null);

  // --- X-RAY RENDERING LOGIC ---
  // Slices the raw text string into <span>s based on highlight indices
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
          key={h.id}
          id={`source-${h.id}`}
          onMouseEnter={() => setActiveId(h.id)}
          className={`
            transition-all duration-200 cursor-pointer border-b-2 rounded px-0.5
            ${isActive
              ? 'bg-yellow-500/40 border-yellow-400 text-white shadow-[0_0_10px_rgba(234,179,8,0.3)]'
              : 'bg-yellow-500/10 border-yellow-500/30 hover:bg-yellow-500/20'}
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
      document.getElementById(`source-${activeId}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      document.getElementById(`card-${activeId}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [activeId]);

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* LEFT: Document Canvas */}
      <div className="w-1/2 bg-slate-950 overflow-y-auto p-8 border-r border-white/10 shadow-inner">
        <div className="max-w-3xl mx-auto">{renderDocument()}</div>
      </div>

      {/* RIGHT: Data Form */}
      <div className="w-1/2 bg-slate-900/30 overflow-y-auto p-6">
        <div className="max-w-2xl mx-auto space-y-4">
          {data.requirements.map((req) => (
            <div
              key={req.requirement_id}
              id={`card-${req.requirement_id}`}
              onMouseEnter={() => setActiveId(req.requirement_id)}
              className={`
                glass-panel p-4 rounded-xl transition-all duration-300 border-l-4
                ${activeId === req.requirement_id ? 'border-l-violet-500 translate-x-2 shadow-violet-500/10' : 'border-l-transparent hover:bg-white/5'}
              `}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-slate-500">{req.requirement_id}</span>
                <span className={`text-xs font-bold px-2 py-1 rounded-full uppercase tracking-wider ${
                  req.requirement_type === 'mandatory' ? 'bg-red-500/10 text-red-400' : 'bg-emerald-500/10 text-emerald-400'
                }`}>
                  {req.requirement_type}
                </span>
              </div>
              <p className="text-sm text-slate-200">{req.statement}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
