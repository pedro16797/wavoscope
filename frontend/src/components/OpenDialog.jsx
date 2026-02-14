import React, { useState } from 'react';
import useStore from '../store';
import Modal from './Modal';

const OpenDialog = ({ isOpen, onClose }) => {
  const [path, setPath] = useState('');
  const { loadProject, browse } = useStore();

  const handleLoad = async () => {
    if (path) {
      await loadProject(path);
      onClose();
    }
  };

  const handleBrowse = async () => {
    const selected = await browse();
    if (selected) {
      setPath(selected);
    }
  };

  return (
    <Modal title="Open Audio File" isOpen={isOpen} onClose={onClose}>
      <div className="open-dialog-content">
        <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
          <input
            type="text"
            value={path}
            onChange={(e) => setPath(e.target.value)}
            placeholder="Absolute path to audio file..."
            style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#222', color: '#fff' }}
          />
          <button onClick={handleBrowse} className="header-button">Browse...</button>
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button onClick={handleLoad} className="header-button" style={{ backgroundColor: 'var(--accent)', color: '#000' }}>Load</button>
        </div>
      </div>
    </Modal>
  );
};

export default OpenDialog;
