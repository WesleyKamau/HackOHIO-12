import React from 'react';
import { BUILD_ENV } from '../api';

function EnvSwitcher() {
  // Only render the runtime switcher for development builds. In production
  // the switcher won't be present in the UI.
  if (BUILD_ENV !== 'development') return null;

  const current = (typeof window !== 'undefined' && (localStorage.getItem('RHAC_ENV') || window.__RHAC_ENV__)) || '';

  const setEnv = (env) => {
    if (typeof window === 'undefined') return;
    localStorage.setItem('RHAC_ENV', env);
    // reload to have runtime effect; the app reads runtime override on load
    window.location.reload();
  };

  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
      <label style={{ fontSize: 12, color: '#666' }}>Runtime env:</label>
      <select
        value={current}
        onChange={(e) => setEnv(e.target.value)}
        style={{ fontSize: 12 }}
      >
        <option value="">(use build env)</option>
        <option value="development">development</option>
        <option value="production">production</option>
      </select>
    </div>
  );
}

export default EnvSwitcher;
