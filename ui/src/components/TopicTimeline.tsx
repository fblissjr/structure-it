import React from 'react';
import { Calendar, FileText, ArrowRight } from 'lucide-react';

interface TimelineItem {
  content: string;
  type: string;
  properties: any;
  source_title: string;
  source_url: string;
  location: string;
}

interface Props {
  items: TimelineItem[];
  query: string;
}

export const TopicTimeline: React.FC<Props> = ({ items, query }) => {
  if (!items || items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-slate-500">
        <p>No timeline data found for "{query}"</p>
      </div>
    );
  }

  return (
    <div className="relative p-8 max-w-4xl mx-auto">
      {/* Central Line */}
      <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-neon-blue/50 to-transparent" />

      <h2 className="text-center text-2xl font-display font-bold text-white mb-12 tracking-widest">
        TIMELINE: <span className="text-neon-blue">{query.toUpperCase()}</span>
      </h2>

      <div className="space-y-12">
        {items.map((item, idx) => {
          const isLeft = idx % 2 === 0;
          return (
            <div key={idx} className={`flex items-center justify-between w-full group ${isLeft ? 'flex-row' : 'flex-row-reverse'}`}>
              
              {/* Content Card */}
              <div className="w-5/12">
                <div className={`
                  glass-panel p-6 rounded-xl border-l-4 transition-all duration-300 hover:-translate-y-1 hover:shadow-glow-blue
                  ${isLeft ? 'text-right border-l-neon-blue' : 'text-left border-l-neon-purple'}
                `}>
                  <div className={`flex items-center gap-2 text-xs font-mono text-slate-400 mb-2 ${isLeft ? 'justify-end' : 'justify-start'}`}>
                    <span className="uppercase tracking-wider text-neon-blue">{item.type}</span>
                    <span>•</span>
                    <span>{item.location || 'N/A'}</span>
                  </div>
                  
                  <p className="text-sm text-slate-200 font-sans leading-relaxed mb-4 line-clamp-4">
                    "{item.content}"
                  </p>

                  <div className={`flex items-center gap-2 ${isLeft ? 'justify-end' : 'justify-start'}`}>
                    <span className="text-xs font-bold px-2 py-1 rounded bg-slate-800 text-slate-400 border border-white/10">
                      {item.properties.classification || 'Info'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Timeline Node */}
              <div className="z-10 flex items-center justify-center w-8 h-8 rounded-full bg-slate-950 border border-neon-blue shadow-glow-blue group-hover:scale-125 transition-transform">
                <div className="w-2 h-2 rounded-full bg-neon-blue animate-pulse" />
              </div>

              {/* Date/Source Label */}
              <div className="w-5/12 px-4">
                <div className={`flex flex-col ${isLeft ? 'items-start' : 'items-end'}`}>
                  <div className="flex items-center gap-2 text-slate-400 mb-1">
                    <Calendar className="w-4 h-4" />
                    <span className="font-mono text-sm">2024-01-12</span> {/* Mock Date */}
                  </div>
                  <div className="flex items-center gap-2 text-slate-500 hover:text-white transition-colors cursor-pointer">
                    <FileText className="w-4 h-4" />
                    <span className="font-bold text-sm truncate max-w-[200px]">{item.source_title}</span>
                    <ArrowRight className="w-3 h-3" />
                  </div>
                </div>
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
};