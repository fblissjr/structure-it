import React, { useState } from 'react';
import { ExtractionWorkbench } from '../../components/ExtractionWorkbench';
import { PolicyGraph } from '../../components/PolicyGraph';

interface Props {
    data: any; // The full extraction result object
    onSelect: (id: string) => void;
}

type ViewMode = 'workbench' | 'graph';

export const ComplianceMonitor: React.FC<Props> = ({ data, onSelect: _onSelect }) => {
    const [view, setView] = useState<ViewMode>('workbench');

    if (!data) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-4 relative overflow-hidden">
                 <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-violet-900/20 via-slate-950 to-slate-950 pointer-events-none" />
                 
                 <div className="relative z-10 flex flex-col items-center">
                    <div className="w-16 h-16 rounded-full bg-slate-900 border border-white/5 flex items-center justify-center mb-4">
                        <span className="text-2xl">🛡️</span>
                    </div>
                    <h3 className="font-display text-xl font-bold text-slate-300">Compliance Monitor</h3>
                    <p className="max-w-md text-center text-sm">
                        No active document. Go to <strong>Data Sources</strong> to ingest a policy or regulation.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col relative">
            {/* App-Specific Toolbar (Floating) */}
            <div className="absolute top-4 right-6 z-50 flex gap-2">
                <button 
                    onClick={() => setView('workbench')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-all border ${
                        view === 'workbench' 
                        ? 'bg-violet-500/20 text-violet-300 border-violet-500/50 shadow-glow-purple' 
                        : 'bg-slate-900/50 text-slate-400 border-white/10 hover:bg-white/5'
                    }`}
                >
                    Workbench
                </button>
                <button 
                    onClick={() => setView('graph')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-all border ${
                        view === 'graph' 
                        ? 'bg-violet-500/20 text-violet-300 border-violet-500/50 shadow-glow-purple' 
                        : 'bg-slate-900/50 text-slate-400 border-white/10 hover:bg-white/5'
                    }`}
                >
                    Graph View
                </button>
            </div>

            {/* View Content */}
            <div className="flex-1 overflow-hidden">
                {view === 'workbench' ? (
                    <ExtractionWorkbench 
                        rawText={data.raw_text} 
                        data={data.data} 
                        highlights={data.highlights || []} 
                        onOpenGraph={() => setView('graph')}
                    />
                ) : (
                    <PolicyGraph 
                        data={data.data} 
                        onBack={() => setView('workbench')} 
                    />
                )}
            </div>
        </div>
    );
};
