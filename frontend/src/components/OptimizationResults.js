import React, { useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

// Rejestruj komponenty Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function OptimizationResults({ results }) {
  const [activeTab, setActiveTab] = useState('summary');

  const baseline = results.results.baseline;
  const optimized = results.results.optimized;
  const improvement = results.results.improvement;
  const plots = results.plots;

  // Dane dla wykresu konwergencji (jeśli dostępne)
  const convergenceData = {
    labels: Array.from({ length: results.results.optimized.solution_vector?.length || 0 }, (_, i) => i + 1),
    datasets: [
      {
        label: 'Wartość funkcji celu',
        data: results.history?.best_values || [],
        borderColor: 'rgb(102, 126, 234)',
        backgroundColor: 'rgba(102, 126, 234, 0.2)',
        tension: 0.1
      }
    ]
  };

  // Dane dla wykresu porównania metryk
  const metricsComparisonData = {
    labels: ['Czas odpowiedzi', 'Długość kolejki', 'Przepustowość', 'Liczba serwerów'],
    datasets: [
      {
        label: 'Przed',
        data: [
          baseline.metrics.mean_response_time,
          baseline.metrics.mean_queue_length,
          baseline.metrics.throughput,
          baseline.metrics.total_servers
        ],
        backgroundColor: 'rgba(255, 107, 107, 0.6)',
        borderColor: 'rgb(255, 107, 107)',
        borderWidth: 2
      },
      {
        label: 'Po',
        data: [
          optimized.metrics.mean_response_time,
          optimized.metrics.mean_queue_length,
          optimized.metrics.throughput,
          optimized.metrics.total_servers
        ],
        backgroundColor: 'rgba(81, 207, 102, 0.6)',
        borderColor: 'rgb(81, 207, 102)',
        borderWidth: 2
      }
    ]
  };

  // Dane dla wykresu kolejek na stacjach
  const queuesData = {
    labels: baseline.metrics.station_names,
    datasets: [
      {
        label: 'Przed optymalizacją',
        data: baseline.metrics.queue_lengths,
        backgroundColor: 'rgba(255, 107, 107, 0.6)',
        borderColor: 'rgb(255, 107, 107)',
        borderWidth: 2
      },
      {
        label: 'Po optymalizacji',
        data: optimized.metrics.queue_lengths,
        backgroundColor: 'rgba(81, 207, 102, 0.6)',
        borderColor: 'rgb(81, 207, 102)',
        borderWidth: 2
      }
    ]
  };

  // Dane dla wykresu wykorzystania serwerów
  const utilizationData = {
    labels: baseline.metrics.station_names,
    datasets: [
      {
        label: 'Przed optymalizacją (%)',
        data: baseline.metrics.utilizations.map(u => u * 100),
        backgroundColor: 'rgba(255, 107, 107, 0.6)',
        borderColor: 'rgb(255, 107, 107)',
        borderWidth: 2
      },
      {
        label: 'Po optymalizacji (%)',
        data: optimized.metrics.utilizations.map(u => u * 100),
        backgroundColor: 'rgba(81, 207, 102, 0.6)',
        borderColor: 'rgb(81, 207, 102)',
        borderWidth: 2
      }
    ]
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'summary':
        return (
          <div className="summary-content">
            {/* Box poprawy */}
            <div className="improvement-card">
              <h3>✨ Poprawa</h3>
              <div className="improvement-value">
                {improvement.percent.toFixed(2)}%
              </div>
              <p className="improvement-desc">
                Funkcja celu: {results.results.optimization_info.objective_description}
              </p>
            </div>

            {/* Metryki przed/po */}
            <div className="metrics-comparison">
              <div className="metric-card baseline">
                <h3>🔴 Przed optymalizacją</h3>
                <div className="metric-row">
                  <span>Konfiguracja serwerów:</span>
                  <strong>[{baseline.network.num_servers.join(', ')}]</strong>
                </div>
                <div className="metric-row">
                  <span>Średni czas odpowiedzi:</span>
                  <strong>{baseline.metrics.mean_response_time.toFixed(4)} s</strong>
                </div>
                <div className="metric-row">
                  <span>Średnia długość kolejki:</span>
                  <strong>{baseline.metrics.mean_queue_length.toFixed(2)}</strong>
                </div>
                <div className="metric-row">
                  <span>Przepustowość:</span>
                  <strong>{baseline.metrics.throughput.toFixed(4)} zadań/s</strong>
                </div>
                <div className="metric-row">
                  <span>Wartość funkcji celu:</span>
                  <strong>{baseline.objective_value.toFixed(4)}</strong>
                </div>
              </div>

              <div className="metric-card optimized">
                <h3>🟢 Po optymalizacji</h3>
                <div className="metric-row">
                  <span>Konfiguracja serwerów:</span>
                  <strong>[{optimized.network.num_servers.join(', ')}]</strong>
                </div>
                <div className="metric-row">
                  <span>Średni czas odpowiedzi:</span>
                  <strong>{optimized.metrics.mean_response_time.toFixed(4)} s</strong>
                </div>
                <div className="metric-row">
                  <span>Średnia długość kolejki:</span>
                  <strong>{optimized.metrics.mean_queue_length.toFixed(2)}</strong>
                </div>
                <div className="metric-row">
                  <span>Przepustowość:</span>
                  <strong>{optimized.metrics.throughput.toFixed(4)} zadań/s</strong>
                </div>
                <div className="metric-row">
                  <span>Wartość funkcji celu:</span>
                  <strong>{optimized.objective_value.toFixed(4)}</strong>
                </div>
              </div>
            </div>

            {/* Szczegóły stacji */}
            <div className="stations-details">
              <h3>📊 Szczegóły stacji</h3>
              <table className="details-table">
                <thead>
                  <tr>
                    <th>Stacja</th>
                    <th>Serwery (przed → po)</th>
                    <th>Kolejka (przed → po)</th>
                    <th>Wykorzystanie (przed → po)</th>
                  </tr>
                </thead>
                <tbody>
                  {baseline.metrics.station_names.map((name, i) => (
                    <tr key={i}>
                      <td>{name}</td>
                      <td>
                        {baseline.network.num_servers[i]} → {optimized.network.num_servers[i]}
                        {optimized.network.num_servers[i] !== baseline.network.num_servers[i] && (
                          <span className="change-indicator">
                            ({optimized.network.num_servers[i] > baseline.network.num_servers[i] ? '+' : ''}{optimized.network.num_servers[i] - baseline.network.num_servers[i]})
                          </span>
                        )}
                      </td>
                      <td>
                        {baseline.metrics.queue_lengths[i].toFixed(2)} → {optimized.metrics.queue_lengths[i].toFixed(2)}
                      </td>
                      <td>
                        {(baseline.metrics.utilizations[i] * 100).toFixed(1)}% → {(optimized.metrics.utilizations[i] * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );

      case 'charts':
        return (
          <div className="charts-content">
            <div className="chart-container">
              <h3>📈 Porównanie metryk</h3>
              <Bar data={metricsComparisonData} options={{
                responsive: true,
                plugins: {
                  legend: { position: 'top' },
                  title: { display: false }
                },
                scales: {
                  y: { beginAtZero: true }
                }
              }} />
            </div>

            <div className="chart-container">
              <h3>📊 Długości kolejek na stacjach</h3>
              <Bar data={queuesData} options={{
                responsive: true,
                plugins: {
                  legend: { position: 'top' },
                  title: { display: false }
                },
                scales: {
                  y: { beginAtZero: true }
                }
              }} />
            </div>

            <div className="chart-container">
              <h3>⚡ Wykorzystanie serwerów (%)</h3>
              <Bar data={utilizationData} options={{
                responsive: true,
                plugins: {
                  legend: { position: 'top' },
                  title: { display: false }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 100
                  }
                }
              }} />
            </div>

            {/* Wykresy z backendu jako obrazy */}
            {plots && (
              <>
                <div className="chart-container">
                  <h3>🔥 Konwergencja algorytmu Firefly</h3>
                  <img src={`data:image/png;base64,${plots.convergence}`} alt="Konwergencja" />
                </div>

                <div className="chart-container">
                  <h3>📊 Szczegółowe porównanie</h3>
                  <img src={`data:image/png;base64,${plots.metrics}`} alt="Metryki" />
                </div>
              </>
            )}
          </div>
        );

      case 'details':
        return (
          <div className="details-content">
            <h3>🔧 Parametry optymalizacji</h3>
            <div className="details-section">
              <h4>Algorytm Firefly</h4>
              <ul>
                <li>Liczba świetlików: {results.results.optimization_info.firefly_params.n_fireflies}</li>
                <li>Liczba iteracji: {results.results.optimization_info.firefly_params.max_iterations}</li>
                <li>Alpha (α): {results.results.optimization_info.firefly_params.alpha}</li>
                <li>Beta₀ (β₀): {results.results.optimization_info.firefly_params.beta_0}</li>
                <li>Gamma (γ): {results.results.optimization_info.firefly_params.gamma}</li>
              </ul>
            </div>

            <div className="details-section">
              <h4>Funkcja celu</h4>
              <ul>
                <li>Nazwa: {results.results.optimization_info.objective_name}</li>
                <li>Opis: {results.results.optimization_info.objective_description}</li>
                <li>Zmienne optymalizowane: {results.results.optimization_info.optimized_variables.join(', ')}</li>
              </ul>
            </div>

            <div className="details-section">
              <h4>Rozwiązanie optymalne</h4>
              <ul>
                <li>Wektor rozwiązania: [{optimized.solution_vector?.join(', ') || 'N/A'}]</li>
                <li>Wartość funkcji celu: {optimized.objective_value.toFixed(6)}</li>
                <li>Poprawa absolutna: {improvement.absolute.toFixed(6)}</li>
              </ul>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="results-container">
      <h2>📊 Wyniki optymalizacji</h2>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveTab('summary')}
        >
          Podsumowanie
        </button>
        <button
          className={`tab ${activeTab === 'charts' ? 'active' : ''}`}
          onClick={() => setActiveTab('charts')}
        >
          Wykresy
        </button>
        <button
          className={`tab ${activeTab === 'details' ? 'active' : ''}`}
          onClick={() => setActiveTab('details')}
        >
          Szczegóły
        </button>
      </div>

      <div className="tab-content">
        {renderTabContent()}
      </div>
    </div>
  );
}

export default OptimizationResults;