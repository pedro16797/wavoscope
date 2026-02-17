import React from 'react';
import { useStore } from '../store/useStore';

export const ProgressDialog: React.FC = () => {
  const export_status = useStore(state => state.export_status);

  if (!export_status.active) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
      <div className="bg-surface border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] shadow-2xl w-full max-w-sm overflow-hidden text-text flex flex-col p-6 space-y-4"
           style={{ backgroundColor: 'var(--color-surface)', borderWidth: 'var(--ui-border)' }}>
        <div className="text-center space-y-2">
            <h3 className="font-bold text-sm uppercase tracking-widest opacity-80">Exporting MusicXML</h3>
            <p className="text-xs opacity-60 h-4">{export_status.message}</p>
        </div>

        <div className="w-full h-2 bg-background rounded-full overflow-hidden border border-grid" style={{ borderWidth: 'var(--ui-border)' }}>
            <div className="h-full bg-accent transition-all duration-300"
                 style={{ width: `${export_status.progress * 100}%` }} />
        </div>

        <div className="text-[10px] font-mono opacity-40 text-center">
            {Math.round(export_status.progress * 100)}%
        </div>
      </div>
    </div>
  );
};
