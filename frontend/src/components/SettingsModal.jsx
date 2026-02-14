import React from 'react';
import useStore from '../store';
import Modal from './Modal';

const SettingsModal = ({ isOpen, onClose }) => {
  const { status, setClickGain, setMetronome } = useStore();

  if (!status) return null;

  return (
    <Modal title="Settings" isOpen={isOpen} onClose={onClose}>
      <div className="settings-content">
        <div className="setting-item">
          <label>Metronome Enabled</label>
          <input
            type="checkbox"
            checked={status.metronome_enabled}
            onChange={(e) => setMetronome(e.target.checked)}
          />
        </div>
        <div className="setting-item">
          <label>Click Gain: {status.click_gain.toFixed(2)}</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={status.click_gain}
            onChange={(e) => setClickGain(parseFloat(e.target.value))}
          />
        </div>
      </div>
    </Modal>
  );
};

export default SettingsModal;
