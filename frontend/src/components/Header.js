import React from 'react';

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <div className="logo">
            <span className="logo-icon">🔥</span>
            <h1>Firefly Optimizer</h1>
          </div>
          <p className="subtitle">Optymalizacja systemów kolejkowych algorytmem świetlika</p>
        </div>
        <div className="header-right">
          <div className="status-badge">
            <span className="status-dot"></span>
            <span>System gotowy</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;