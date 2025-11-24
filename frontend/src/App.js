import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import NetworkForm from './components/NetworkForm';
import OptimizationResults from './components/OptimizationResults';
import LoadingSpinner from './components/LoadingSpinner';
import Header from './components/Header';

// Konfiguracja axios - używamy względnych ścieżek (nginx przekieruje do backendu)

function App() {
  const [objectives, setObjectives] = useState([]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [currentStep, setCurrentStep] = useState(1);

  // Pobierz dostępne funkcje celu przy starcie
  useEffect(() => {
    fetchObjectives();
  }, []);

  const fetchObjectives = async () => {
    try {
      const response = await axios.get('/api/objectives');
      setObjectives(response.data);
    } catch (err) {
      console.error('Błąd pobierania funkcji celu:', err);
      setError('Nie można pobrać listy funkcji celu');
    }
  };

  const handleOptimize = async (formData) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // Timeout 10 minut dla dlugich optymalizacji (100 swietlikow * 200 iteracji moze trwac dlugo)
      const response = await axios.post('/optimize', formData, {
        timeout: 600000 // 10 minut
      });

      if (response.data.success) {
        setResults(response.data);
        setCurrentStep(2); // Przejdź do wyników
      } else {
        setError(response.data.error || 'Wystąpił błąd podczas optymalizacji');
      }
    } catch (err) {
      console.error('Błąd optymalizacji:', err);
      setError(err.response?.data?.error || 'Błąd połączenia z serwerem');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
    setCurrentStep(1);
  };

  return (
    <div className="App">
      <Header />

      <main className="main-container">
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <div>
              <h3>Wystąpił błąd</h3>
              <p>{error}</p>
            </div>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        {loading && <LoadingSpinner />}

        {!loading && currentStep === 1 && (
          <NetworkForm
            objectives={objectives}
            onSubmit={handleOptimize}
          />
        )}

        {!loading && currentStep === 2 && results && (
          <>
            <OptimizationResults results={results} />
            <div className="action-buttons">
              <button
                className="btn-secondary"
                onClick={handleReset}
              >
                Nowa optymalizacja
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;