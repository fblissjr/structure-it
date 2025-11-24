import { useState } from 'react';
import { DocumentIngest } from './components/DocumentIngest';
import { ExtractionWorkbench } from './components/ExtractionWorkbench';
import { Box } from 'lucide-react';

export default function App() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (file: File) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/api/extract', {
        method: 'POST',
        body: formData
      });
      const json = await res.json();
      setData(json);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="h-16 border-b border-white/10 flex items-center px-6 glass-panel z-50 relative">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center">
            <Box className="w-5 h-5 text-white" />
          </div>
          <h1 className="font-bold text-lg tracking-tight">Structure Studio</h1>
        </div>
      </header>

      {/* Main Content */}
      <main>
        {!data ? (
          <DocumentIngest onUpload={handleUpload} isLoading={loading} />
        ) : (
          <ExtractionWorkbench
            rawText={data.raw_text}
            data={data.data}
            highlights={data.highlights}
          />
        )}
      </main>
    </div>
  );
}
