import React, { useState, useRef, useLayoutEffect } from 'react';
import { createPortal } from 'react-dom';

interface TooltipProps {
  children: React.ReactNode;
  content: string;
  shortcut?: string;
}

export const Tooltip: React.FC<TooltipProps> = ({ children, content, shortcut }) => {
  const [visible, setVisible] = useState(false);
  const [coords, setCoords] = useState({ x: 0, y: 0, showBelow: false });
  const [adjustedX, setAdjustedX] = useState(0);
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  const updateCoords = () => {
    if (triggerRef.current) {
        const rect = triggerRef.current.getBoundingClientRect();
        const showBelow = rect.top < 60;
        const centerX = rect.left + rect.width / 2;
        setCoords({
            x: centerX,
            y: showBelow ? rect.bottom : rect.top,
            showBelow
        });
        setAdjustedX(centerX);
    }
  };

  useLayoutEffect(() => {
    if (visible && tooltipRef.current) {
        const tooltipRect = tooltipRef.current.getBoundingClientRect();
        const halfWidth = tooltipRect.width / 2;
        let newX = coords.x;

        const margin = 8;
        if (coords.x - halfWidth < margin) {
            newX = halfWidth + margin;
        } else if (coords.x + halfWidth > window.innerWidth - margin) {
            newX = window.innerWidth - halfWidth - margin;
        }
        setAdjustedX(newX);
    }
  }, [visible, coords.x]);

  const handleMouseEnter = () => {
      updateCoords();
      setVisible(true);
  };

  if (!content) return <>{children}</>;

  const arrowOffset = coords.x - adjustedX;

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
          ref={tooltipRef}
          className={`fixed z-[9999] px-2 py-1.5 flex flex-col items-center border rounded-[var(--ui-radius)] shadow-xl pointer-events-none -translate-x-1/2 transition-opacity duration-150 ${coords.showBelow ? 'translate-y-2' : '-translate-y-[calc(100%+8px)]'}`}
          style={{
            left: adjustedX,
            top: coords.y,
            backgroundColor: 'var(--color-surface)',
            borderColor: 'var(--color-grid)',
            color: 'var(--color-text)',
            borderWidth: 'var(--ui-border)'
          }}
        >
          <div className="text-[10px] font-bold whitespace-nowrap">{content}</div>
          {shortcut && (
              <div className="text-[9px] opacity-60 font-mono mt-0.5 bg-black/20 px-1.5 py-0.5 rounded border border-white/5">
                  {shortcut}
              </div>
          )}
          {/* Arrow */}
          {coords.showBelow ? (
              <>
                <div className="absolute bottom-full border-4 border-transparent"
                     style={{
                         left: `calc(50% + ${arrowOffset}px)`,
                         transform: 'translateX(-50%)',
                         borderBottomColor: 'var(--color-grid)'
                     }} />
                <div className="absolute bottom-[calc(100%-1px)] border-[3px] border-transparent"
                     style={{
                         left: `calc(50% + ${arrowOffset}px)`,
                         transform: 'translateX(-50%)',
                         borderBottomColor: 'var(--color-surface)'
                     }} />
              </>
          ) : (
              <>
                <div className="absolute top-full border-4 border-transparent"
                     style={{
                         left: `calc(50% + ${arrowOffset}px)`,
                         transform: 'translateX(-50%)',
                         borderTopColor: 'var(--color-grid)'
                     }} />
                <div className="absolute top-[calc(100%-1px)] border-[3px] border-transparent"
                     style={{
                         left: `calc(50% + ${arrowOffset}px)`,
                         transform: 'translateX(-50%)',
                         borderTopColor: 'var(--color-surface)'
                     }} />
              </>
          )}
        </div>,
        document.body
      )}
    </div>
  );
};
