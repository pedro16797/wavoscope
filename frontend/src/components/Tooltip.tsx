import React, { useState, useRef } from 'react';
import { createPortal } from 'react-dom';

interface TooltipProps {
  children: React.ReactNode;
  content: string;
}

export const Tooltip: React.FC<TooltipProps> = ({ children, content }) => {
  const [visible, setVisible] = useState(false);
  const [coords, setCoords] = useState({ x: 0, y: 0, showBelow: false });
  const triggerRef = useRef<HTMLDivElement>(null);

  const updateCoords = () => {
    if (triggerRef.current) {
        const rect = triggerRef.current.getBoundingClientRect();
        const showBelow = rect.top < 50;
        setCoords({
            x: rect.left + rect.width / 2,
            y: showBelow ? rect.bottom : rect.top,
            showBelow
        });
    }
  };

  const handleMouseEnter = () => {
      updateCoords();
      setVisible(true);
  };

  if (!content) return <>{children}</>;

  return (
    <div
      ref={triggerRef}
      className="inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={() => setVisible(false)}
    >
      {children}
      {visible && createPortal(
        <div
          className={`fixed z-[9999] px-2 py-1 text-[10px] font-bold whitespace-nowrap border rounded-[var(--ui-radius)] shadow-xl pointer-events-none -translate-x-1/2 transition-opacity duration-150 ${coords.showBelow ? 'translate-y-2' : '-translate-y-[calc(100%+8px)]'}`}
          style={{
            left: coords.x,
            top: coords.y,
            backgroundColor: 'var(--color-surface)',
            borderColor: 'var(--color-grid)',
            color: 'var(--color-text)',
            borderWidth: 'var(--ui-border)'
          }}
        >
          {content}
          {/* Arrow */}
          {coords.showBelow ? (
              <>
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 border-4 border-transparent"
                     style={{ borderBottomColor: 'var(--color-grid)' }} />
                <div className="absolute bottom-[calc(100%-1px)] left-1/2 -translate-x-1/2 border-[3px] border-transparent"
                     style={{ borderBottomColor: 'var(--color-surface)' }} />
              </>
          ) : (
              <>
                <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent"
                     style={{ borderTopColor: 'var(--color-grid)' }} />
                <div className="absolute top-[calc(100%-1px)] left-1/2 -translate-x-1/2 border-[3px] border-transparent"
                     style={{ borderTopColor: 'var(--color-surface)' }} />
              </>
          )}
        </div>,
        document.body
      )}
    </div>
  );
};
