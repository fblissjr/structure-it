import React, { useRef, useState } from 'react';
import { Upload, Loader2 } from 'lucide-react';

interface Props {
  onUpload: (file: File) => Promise<void>;
  isLoading: boolean;
}

export const DocumentIngest: React.FC<Props> = ({ onUpload, isLoading }) => {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files?.[0]) await onUpload(e.dataTransfer.files[0]);
  };

  return (
    <div className="flex h-screen items-center justify-center p-8">
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`
          relative w-full max-w-2xl aspect-video rounded-3xl border-2 border-dashed transition-all cursor-pointer flex flex-col items-center justify-center
          ${isDragging ? 'border-violet-500 bg-violet-500/10 scale-105' : 'border-slate-700 hover:border-slate-500 hover:bg-white/5'}
          ${isLoading ? 'pointer-events-none opacity-50' : ''}
        `}
      >
        {isLoading ? (
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin text-violet-500 mx-auto mb-4" />
            <p className="text-lg font-mono text-violet-300">EXTRACTING_STRUCTURE...</p>
          </div>
        ) : (
          <>
            <div className="w-16 h-16 rounded-2xl bg-slate-800 flex items-center justify-center mb-4 shadow-lg">
              <Upload className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">Drop Policy PDF</h3>
            <p className="text-slate-500 font-mono text-sm">Supports .PDF, .MD</p>
          </>
        )}
        <input ref={inputRef} type="file" className="hidden" onChange={(e) => e.target.files?.[0] && onUpload(e.target.files[0])} />
      </div>
    </div>
  );
};
