import React, { useRef, useState } from 'react';
import { Upload, Loader2, FileType, ChevronDown } from 'lucide-react';

interface Props {
  onUpload: (file: File, type: string) => Promise<void>;
  isLoading: boolean;
}

export const DocumentIngest: React.FC<Props> = ({ onUpload, isLoading }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [docType, setDocType] = useState('policy');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files?.[0]) await onUpload(e.dataTransfer.files[0], docType);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files?.[0]) {
          await onUpload(e.target.files[0], docType);
      }
  };

  return (
    <div className="flex h-screen flex-col items-center justify-center p-8 gap-8 relative overflow-hidden">
      {/* Background Ambience */}
      <div className="absolute inset-0 bg-cyber-grid bg-[length:50px_50px] opacity-20 pointer-events-none" />
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-neon-purple/20 rounded-full blur-[100px] pointer-events-none animate-pulse-slow" />
      <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-neon-blue/20 rounded-full blur-[100px] pointer-events-none animate-pulse-slow" />

      {/* Header Text */}
      <div className="z-10 text-center">
          <h1 className="text-4xl md:text-6xl font-display font-bold text-white mb-2 tracking-tighter">
              STRUCTURE <span className="text-neon-blue">STUDIO</span>
          </h1>
          <p className="text-slate-400 font-mono text-sm md:text-base tracking-widest uppercase">
              Advanced Document Intelligence Interface
          </p>
      </div>

      {/* Document Type Selector */}
      <div className="z-10 relative group">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-neon-blue to-neon-purple rounded-xl opacity-75 group-hover:opacity-100 blur transition duration-1000 group-hover:duration-200" />
        <div className="relative flex items-center gap-3 bg-slate-900 p-2 rounded-xl border border-white/10">
            <div className="p-2 bg-neon-blue/10 rounded-lg">
                <FileType className="w-5 h-5 text-neon-blue" />
            </div>
            <div className="relative">
                <select 
                    value={docType}
                    onChange={(e) => setDocType(e.target.value)}
                    className="appearance-none bg-transparent text-white font-display tracking-wide outline-none border-none cursor-pointer min-w-[200px] py-1 pr-8 uppercase font-bold"
                    disabled={isLoading}
                >
                    <option value="policy" className="bg-slate-900 text-slate-300">Policy Document</option>
                    <option value="academic" className="bg-slate-900 text-slate-300">Academic Paper</option>
                    <option value="article" className="bg-slate-900 text-slate-300">Web Article</option>
                    <option value="code" className="bg-slate-900 text-slate-300">Code Documentation</option>
                    <option value="meeting" className="bg-slate-900 text-slate-300">Meeting Notes</option>
                    <option value="media" className="bg-slate-900 text-slate-300">Media Transcript</option>
                </select>
                <ChevronDown className="absolute right-0 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
            </div>
        </div>
      </div>

      {/* Upload Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => !isLoading && inputRef.current?.click()}
        className={`
          z-10 relative w-full max-w-2xl aspect-video rounded-3xl border-2 border-dashed transition-all cursor-pointer flex flex-col items-center justify-center
          backdrop-blur-md
          ${isDragging 
            ? 'border-neon-blue bg-neon-blue/10 scale-105 shadow-glow-blue' 
            : 'border-slate-700 hover:border-neon-blue/50 hover:bg-slate-800/50 hover:shadow-glow-blue'}
          ${isLoading ? 'pointer-events-none opacity-80 border-neon-purple bg-neon-purple/5' : ''}
        `}
      >
        {isLoading ? (
          <div className="text-center">
            <div className="relative">
                <Loader2 className="w-16 h-16 animate-spin text-neon-purple mx-auto mb-4" />
                <div className="absolute inset-0 animate-pulse bg-neon-purple/20 blur-xl rounded-full" />
            </div>
            <p className="text-xl font-display font-bold text-white tracking-widest">ANALYZING...</p>
            <p className="text-sm font-mono text-neon-blue mt-2 animate-pulse">
                &gt; INGESTING {docType.toUpperCase()}_SCHEMA
            </p>
          </div>
        ) : (
          <>
            <div className="w-20 h-20 rounded-2xl bg-slate-900 border border-white/10 flex items-center justify-center mb-6 shadow-2xl group-hover:scale-110 transition-transform">
              <Upload className="w-10 h-10 text-slate-400 group-hover:text-white" />
            </div>
            <h3 className="text-3xl font-display font-bold text-white mb-2 tracking-tight">
                UPLOAD <span className="text-neon-blue">TARGET</span>
            </h3>
            <p className="text-slate-400 font-mono text-sm">
                DRAG & DROP OR CLICK TO BROWSE
            </p>
            <div className="mt-4 flex gap-2 text-[10px] font-mono text-slate-600 uppercase tracking-widest">
                <span className="px-2 py-1 bg-slate-900 rounded border border-white/5">.PDF</span>
                <span className="px-2 py-1 bg-slate-900 rounded border border-white/5">.MD</span>
                <span className="px-2 py-1 bg-slate-900 rounded border border-white/5">.TXT</span>
            </div>
          </>
        )}
        <input ref={inputRef} type="file" className="hidden" onChange={handleFileSelect} />
      </div>
    </div>
  );
};
