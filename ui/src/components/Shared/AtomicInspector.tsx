import React from 'react';
import { X, Code, Activity } from 'lucide-react';

interface Props {
  itemId: string | null;
  data: any;
  onClose: () => void;
}

export const AtomicInspector: React.FC<Props> = ({ itemId, data, onClose }) => {
  if (!itemId) return null;

  // Helper to render JSON tree
  const renderJson = (obj: any, depth = 0) => {
    if (typeof obj !== 'object' || obj === null) {
      return <span className="text-neon-blue break-all">{String(obj)}</span>;
    }

    return (
      <div className="pl-2 border-l border-white/5">
        {Object.entries(obj).map(([key, value]) => (
          <div key={key} className="my-1">
            <span className="text-slate-500 text-xs font-mono mr-2">{key}:</span>
            {typeof value === 'object' && value !== null ? (
              <div className="mt-1">{renderJson(value, depth + 1)}</div>
            ) : (
              <span className="text-slate-300 text-sm font-mono">{String(value)}</span>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-slate-900/95 border-l border-white/10 shadow-2xl transform transition-transform duration-300 z-[60] backdrop-blur-xl">
      <div className="h-full flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-white/10 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center gap-2">
            <Code className="w-4 h-4 text-neon-purple" />
            <h3 className="font-display font-bold text-sm tracking-widest uppercase text-white">Atomic Inspector</h3>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-500 hover:text-white transition-colors p-1 hover:bg-white/5 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
          <div className="mb-6">
            <h4 className="text-xs font-bold text-slate-500 uppercase mb-2 font-mono">Entity ID</h4>
            <div className="p-3 bg-slate-950 rounded-lg border border-white/5 font-mono text-xs text-neon-blue break-all">
              {itemId}
            </div>
          </div>

          <div className="mb-6">
            <h4 className="text-xs font-bold text-slate-500 uppercase mb-2 font-mono">Raw Data</h4>
            <div className="bg-slate-950/50 rounded-lg p-3 border border-white/5 text-xs font-mono overflow-x-auto">
               {data ? renderJson(data) : <span className="text-slate-600 italic">No data available for this entity.</span>}
            </div>
          </div>

          {/* Mock Vector Visualization */}
          <div>
             <h4 className="text-xs font-bold text-slate-500 uppercase mb-2 font-mono flex items-center gap-2">
                <Activity className="w-3 h-3" /> Embedding Vector
             </h4>
             <div className="flex items-end gap-px h-16 bg-slate-950 p-2 rounded-lg border border-white/5">
                {Array.from({ length: 40 }).map((_, i) => (
                    <div 
                        key={i} 
                        className="flex-1 bg-neon-purple/40 hover:bg-neon-purple transition-colors"
                        style={{ height: `${Math.random() * 100}%` }}
                    />
                ))}
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};
