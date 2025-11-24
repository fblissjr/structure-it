import React from 'react';
import { TopicTimeline } from '../../components/TopicTimeline';

interface Props {
    searchResults: any[];
    query: string;
    onSelect: (id: string) => void;
}

export const CitizenExplorer: React.FC<Props> = ({ searchResults, query, onSelect: _onSelect }) => {
    // In a real app, we might fetch initial data here if searchResults is empty
    
    return (
        <div className="h-full overflow-y-auto custom-scrollbar bg-slate-950 relative">
             {/* Background Texture specific to Citizen Explorer */}
             <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-cyan-900/20 via-slate-950 to-slate-950 pointer-events-none fixed" />
             
             <div className="relative z-10 py-8">
                {searchResults.length > 0 ? (
                    <TopicTimeline items={searchResults} query={query} />
                ) : (
                    <div className="flex flex-col items-center justify-center h-[60vh] text-slate-500 space-y-4">
                        <div className="w-16 h-16 rounded-full bg-slate-900 border border-white/5 flex items-center justify-center">
                             <span className="text-2xl">🏛️</span>
                        </div>
                        <h3 className="font-display text-xl font-bold text-slate-300">Citizen Explorer</h3>
                        <p className="max-w-md text-center text-sm">
                            Search for topics like "Zoning", "Budget", or "Parking" to see the timeline of democracy in action.
                        </p>
                    </div>
                )}
             </div>
        </div>
    );
};
