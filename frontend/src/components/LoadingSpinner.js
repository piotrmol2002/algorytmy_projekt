import React from 'react';

function LoadingSpinner() {
  return (
    <div className="loading-overlay">
      <div className="loading-content">
        <div className="spinner-container">
          <div className="firefly-spinner">
            <div className="firefly"></div>
            <div className="firefly"></div>
            <div className="firefly"></div>
          </div>
        </div>
        <h3>Optymalizacja w toku...</h3>
        <p>Algorytm Firefly przeszukuje przestrzeń rozwiązań</p>
        <div className="progress-bar">
          <div className="progress-fill"></div>
        </div>
      </div>
    </div>
  );
}

export default LoadingSpinner;