import { useState } from 'react';
import { Sidebar, type AppID } from './components/Layout/Sidebar';
import { CitizenExplorer } from './apps/CitizenExplorer';
import { ComplianceMonitor } from './apps/ComplianceMonitor';
import { DataSources } from './apps/DataSources';
import { AtomicInspector } from './components/Shared/AtomicInspector';

export default function App() {
  // Shell State
  const [activeApp, setActiveApp] = useState<AppID>('data');
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);

  // Data State
  const [extractionData, setExtractionData] = useState<any>(null);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Actions
  const handleUpload = async (file: File, type: string) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    try {
      const res = await fetch('http://localhost:8000/api/extract', {
        method: 'POST',
        body: formData
      });
      const json = await res.json();
      setExtractionData(json);
      // Auto-switch to Compliance Monitor after successful upload
      setActiveApp('compliance');
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && searchQuery.trim()) {
      setLoading(true);
      try {
        const res = await fetch(`http://localhost:8000/api/search?q=${encodeURIComponent(searchQuery)}`);
        const json = await res.json();
        setSearchResults(json.results);
        // Auto-switch to Citizen Explorer after search
        setActiveApp('citizen');
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 font-sans overflow-hidden selection:bg-neon-pink selection:text-white">
      {/* 1. Global Nav */}
      <Sidebar activeApp={activeApp} onSwitch={setActiveApp} />

      {/* 2. Main Stage */}
      <div className="flex-1 flex flex-col relative min-w-0">
        {/* Dynamic Header / Search */}
        <header className="h-16 border-b border-white/5 flex items-center px-6 bg-white/5 backdrop-blur-md z-50 justify-between">
            <h2 className="text-xl font-bold tracking-widest font-display text-white uppercase">
                {activeApp === 'citizen' && <span className="text-cyan-400 drop-shadow-[0_0_10px_rgba(34,211,238,0.5)]">Citizen Explorer</span>}
                {activeApp === 'compliance' && <span className="text-violet-400 drop-shadow-[0_0_10px_rgba(167,139,250,0.5)]">Compliance Monitor</span>}
                {activeApp === 'data' && <span className="text-slate-400">Data Sources</span>}
            </h2>
            
            <div className="w-96 relative group">
                <input 
                    type="text" 
                    placeholder={`Search ${activeApp === 'citizen' ? 'democracy...' : 'knowledge base...'}`}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={handleSearch}
                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 pl-10 text-sm focus:outline-none focus:border-white/20 transition-all font-mono text-slate-300 placeholder:text-slate-600"
                />
                 {/* Search Icon or Loading Spinner */}
                 <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">
                    {loading ? (
                        <div className="w-4 h-4 border-2 border-slate-500 border-t-transparent rounded-full animate-spin" />
                    ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                    )}
                 </div>
            </div>
        </header>

        {/* App Context */}
        <div className="flex-1 overflow-hidden relative bg-slate-950">
            {activeApp === 'citizen' && (
                <CitizenExplorer 
                    searchResults={searchResults} 
                    query={searchQuery} 
                    onSelect={setSelectedItemId} 
                />
            )}
            {activeApp === 'compliance' && (
                <ComplianceMonitor 
                    data={extractionData} 
                    onSelect={setSelectedItemId} 
                />
            )}
            {activeApp === 'data' && (
                <DataSources 
                    onUpload={handleUpload} 
                    isLoading={loading} 
                />
            )}
        </div>
      </div>

      {/* 3. Global Inspector (Slide-over) */}
      {selectedItemId && (
          <AtomicInspector 
            itemId={selectedItemId} 
            data={null} // Pass actual object detail here if available
            onClose={() => setSelectedItemId(null)} 
          />
      )}
    </div>
  );
}