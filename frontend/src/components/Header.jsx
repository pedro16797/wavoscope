import React from 'react';
import useStore from '../store';
import themes from '../themes.json';

const Header = ({ onOpenSettings, onOpenOpen }) => {
  const { theme, setTheme, status } = useStore();

  return (
    <header className="app-header">
      <div className="header-left">
        <h1 className="app-title">Wavoscope</h1>
        <button onClick={onOpenOpen} className="header-button">Open...</button>
        <button onClick={onOpenSettings} className="header-button">Settings</button>
      </div>
      <div className="header-center">
        {status && <span className="current-file">{status.audio_path.split('/').pop()}</span>}
      </div>
      <div className="header-right">
        <label className="theme-label">Theme:</label>
        <select
          value={theme}
          onChange={(e) => setTheme(e.target.value)}
          className="theme-select"
        >
          {Object.keys(themes).map(t => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>
    </header>
  );
};

export default Header;
