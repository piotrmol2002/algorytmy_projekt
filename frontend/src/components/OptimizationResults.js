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
  const cost = results.results.cost;
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
            {/* Inwestycja vs zysk */}
            {cost && cost.type === 'added_servers' && (
              <div className="investment-card">
                <h3>💰 Analiza kosztów optymalizacji</h3>
                <p style={{fontSize: '0.9em', color: '#666', marginBottom: '15px'}}>
                  {cost.description}
                </p>

                <div className="metric-row">
                  <span>Serwery przed:</span>
                  <strong>{cost.baseline_servers}</strong>
                </div>

                <div className="metric-row">
                  <span>Serwery po:</span>
                  <strong>{cost.optimized_servers}</strong>
                </div>

                <div className="metric-row">
                  <span>💸 Dodane serwery (inwestycja):</span>
                  <strong style={{color: '#ff6b6b'}}>{cost.added_servers}</strong>
                </div>

                <div className="metric-row">
                  <span>💚 Poprawa funkcji celu:</span>
                  <strong style={{color: '#51cf66'}}>{cost.improvement_value.toFixed(4)}</strong>
                </div>

                <div className="metric-row">
                  <span>📈 Poprawa procentowa:</span>
                  <strong style={{color: '#51cf66'}}>{cost.improvement_percent.toFixed(2)}%</strong>
                </div>

                <div style={{marginTop: '15px', padding: '10px', background: '#e7f5ff', borderRadius: '5px'}}>
                  <strong>Wniosek:</strong> Dodanie {cost.added_servers} serwer(ów) 
                  poprawiło wydajność o {cost.improvement_percent.toFixed(2)}%
                </div>
              </div>
            )}

            {/* Szczegółowy breakdown dla profit */}
            {cost && cost.type === 'profit_breakdown' && (
              <div className="investment-card">
                <h3>💰 Analiza ekonomiczna (Profit)</h3>
                <p style={{fontSize: '0.9em', color: '#666', marginBottom: '15px'}}>
                  {cost.description}
                </p>

                <h4 style={{marginTop: '20px', marginBottom: '10px'}}>Przed optymalizacją:</h4>
                <div className="metric-row">
                  <span>💵 Przychód (r·X):</span>
                  <strong style={{color: '#51cf66'}}>{cost.baseline.revenue.toFixed(2)}</strong>
                </div>
                <div className="metric-row">
                  <span>💸 Koszt serwerów (Cₛ·Σμ):</span>
                  <strong style={{color: '#ff6b6b'}}>-{cost.baseline.cost_servers.toFixed(2)}</strong>
                </div>
                <div className="metric-row">
                  <span>💸 Koszt klientów (Cₙ·N):</span>
                  <strong style={{color: '#ff6b6b'}}>-{cost.baseline.cost_customers.toFixed(2)}</strong>
                </div>
                <div className="metric-row" style={{borderTop: '2px solid #ddd', paddingTop: '8px', marginTop: '8px'}}>
                  <span><strong>= Zysk netto:</strong></span>
                  <strong style={{color: cost.baseline.profit >= 0 ? '#51cf66' : '#ff6b6b', fontSize: '1.1em'}}>
                    {cost.baseline.profit.toFixed(2)}
                  </strong>
                </div>

                <h4 style={{marginTop: '20px', marginBottom: '10px'}}>Po optymalizacji:</h4>
                <div className="metric-row">
                  <span>💵 Przychód (r·X):</span>
                  <strong style={{color: '#51cf66'}}>{cost.optimized.revenue.toFixed(2)}</strong>
                </div>
                <div className="metric-row">
                  <span>💸 Koszt serwerów (Cₛ·Σμ):</span>
                  <strong style={{color: '#ff6b6b'}}>-{cost.optimized.cost_servers.toFixed(2)}</strong>
                </div>
                <div className="metric-row">
                  <span>💸 Koszt klientów (Cₙ·N):</span>
                  <strong style={{color: '#ff6b6b'}}>-{cost.optimized.cost_customers.toFixed(2)}</strong>
                </div>
                <div className="metric-row" style={{borderTop: '2px solid #ddd', paddingTop: '8px', marginTop: '8px'}}>
                  <span><strong>= Zysk netto:</strong></span>
                  <strong style={{color: cost.optimized.profit >= 0 ? '#51cf66' : '#ff6b6b', fontSize: '1.1em'}}>
                    {cost.optimized.profit.toFixed(2)}
                  </strong>
                </div>

                <h4 style={{marginTop: '20px', marginBottom: '10px'}}>Wynik inwestycji:</h4>
                <div className="metric-row">
                  <span>💸 Dodatkowy koszt (inwestycja):</span>
                  <strong style={{color: '#ff6b6b'}}>{cost.delta.investment.toFixed(2)}</strong>
                </div>
                <div className="metric-row">
                  <span>💰 Przyrost zysku:</span>
                  <strong style={{color: '#51cf66'}}>+{cost.delta.profit_gain.toFixed(2)}</strong>
                </div>
                <div className="metric-row">
                  <span>📊 ROI (Return on Investment):</span>
                  <strong style={{color: '#4c6ef5', fontSize: '1.1em'}}>{cost.delta.roi_percent.toFixed(1)}%</strong>
                </div>
                <div className="metric-row">
                  <span>🔧 Dodane serwery:</span>
                  <strong>{cost.added_servers}</strong>
                </div>

                <div style={{marginTop: '15px', padding: '10px', background: '#e7f5ff', borderRadius: '5px'}}>
                  <strong>Wniosek:</strong> Inwestycja {cost.delta.investment.toFixed(2)} jednostek 
                  zwiększyła zysk o {cost.delta.profit_gain.toFixed(2)} (ROI: {cost.delta.roi_percent.toFixed(1)}%)
                </div>
              </div>
            )}
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
                 {plots.response_time_percentiles && (
                  <div className="chart-container">
                    <h3>⏱ Percentyle czasów odpowiedzi</h3>
                    <img
                      src={`data:image/png;base64,${plots.response_time_percentiles}`}
                      alt="Percentyle czasów odpowiedzi"
                    />
                  </div>
                )}
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