import React, { useState } from 'react';

function NetworkForm({ objectives, onSubmit }) {
  const [numStations, setNumStations] = useState(3);
  const [numCustomers, setNumCustomers] = useState(20);
  const [stations, setStations] = useState([
    { name: 'Stacja 1', serviceRate: 5.0, numServers: 2 },
    { name: 'Stacja 2', serviceRate: 3.0, numServers: 2 },
    { name: 'Stacja 3', serviceRate: 4.0, numServers: 2 }
  ]);
  const [selectedObjective, setSelectedObjective] = useState('mean_response_time');
  const [serverMin, setServerMin] = useState(1);
  const [serverMax, setServerMax] = useState(10);
  const [fireflyParams, setFireflyParams] = useState({
    n_fireflies: 25,
    max_iterations: 100,
    alpha: 0.5,
    beta_0: 1.0,
    gamma: 1.0
  });

  const handleNumStationsChange = (value) => {
    const newNum = parseInt(value);
    setNumStations(newNum);

    // Dostosuj tablicę stacji
    const newStations = [];
    for (let i = 0; i < newNum; i++) {
      if (i < stations.length) {
        newStations.push(stations[i]);
      } else {
        newStations.push({
          name: `Stacja ${i + 1}`,
          serviceRate: 3.0 + Math.random() * 3,
          numServers: 2
        });
      }
    }
    setStations(newStations.slice(0, newNum));
  };

  const handleStationChange = (index, field, value) => {
    const newStations = [...stations];
    newStations[index][field] = field === 'name' ? value : parseFloat(value);
    setStations(newStations);
  };

  const handleFireflyParamChange = (param, value) => {
    setFireflyParams({
      ...fireflyParams,
      [param]: parseFloat(value)
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Przygotuj dane do wysłania
    const formData = {
      num_stations: numStations,
      num_customers: numCustomers,
      objective: selectedObjective,
      optimize_vars: ['num_servers'],
      server_min: serverMin,
      server_max: serverMax,
      ...fireflyParams
    };

    // Dodaj dane stacji
    stations.forEach((station, i) => {
      formData[`station_name_${i}`] = station.name;
      formData[`service_rate_${i}`] = station.serviceRate;
      formData[`num_servers_${i}`] = station.numServers;
    });

    onSubmit(formData);
  };

  return (
    <form className="network-form" onSubmit={handleSubmit}>
      {/* Sekcja 1: Podstawowe parametry */}
      <div className="form-section">
        <h2>1. Definicja sieci kolejkowej</h2>

        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="num_stations">Liczba stacji (K)</label>
            <input
              type="number"
              id="num_stations"
              value={numStations}
              onChange={(e) => handleNumStationsChange(e.target.value)}
              min="2"
              max="10"
              required
            />
            <small>Ile stacji obsługi ma Twoja sieć?</small>
          </div>

          <div className="form-group">
            <label htmlFor="num_customers">Liczba klientów (N)</label>
            <input
              type="number"
              id="num_customers"
              value={numCustomers}
              onChange={(e) => setNumCustomers(parseInt(e.target.value))}
              min="1"
              max="100"
              required
            />
            <small>Ile zadań krąży w systemie?</small>
          </div>
        </div>
      </div>

      {/* Sekcja 2: Konfiguracja stacji */}
      <div className="form-section">
        <h2>2. Konfiguracja stacji</h2>

        <div className="stations-list">
          {stations.map((station, index) => (
            <div key={index} className="station-card">
              <div className="station-header">Stacja {index + 1}</div>

              <div className="form-group">
                <label>Nazwa stacji</label>
                <input
                  type="text"
                  value={station.name}
                  onChange={(e) => handleStationChange(index, 'name', e.target.value)}
                />
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label>Szybkość obsługi μ (zadania/s)</label>
                  <input
                    type="number"
                    value={station.serviceRate}
                    onChange={(e) => handleStationChange(index, 'serviceRate', e.target.value)}
                    min="0.1"
                    step="0.1"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Liczba serwerów (początkowa)</label>
                  <input
                    type="number"
                    value={station.numServers}
                    onChange={(e) => handleStationChange(index, 'numServers', e.target.value)}
                    min="1"
                    max="20"
                    required
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Sekcja 3: Funkcja celu */}
      <div className="form-section">
        <h2>3. Funkcja celu</h2>

        <div className="form-group">
          <label htmlFor="objective">Co chcesz optymalizować?</label>
          <select
            id="objective"
            value={selectedObjective}
            onChange={(e) => setSelectedObjective(e.target.value)}
            required
          >
            {objectives.map(obj => (
              <option key={obj.id} value={obj.id}>
                {obj.name} - {obj.description}
              </option>
            ))}
          </select>
        </div>

        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="server_min">Min. liczba serwerów</label>
            <input
              type="number"
              id="server_min"
              value={serverMin}
              onChange={(e) => setServerMin(parseInt(e.target.value))}
              min="1"
              max="20"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="server_max">Max. liczba serwerów</label>
            <input
              type="number"
              id="server_max"
              value={serverMax}
              onChange={(e) => setServerMax(parseInt(e.target.value))}
              min="1"
              max="20"
              required
            />
          </div>
        </div>
      </div>

      {/* Sekcja 4: Parametry Firefly */}
      <div className="form-section">
        <h2>4. Parametry algorytmu Firefly</h2>

        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="n_fireflies">Liczba świetlików</label>
            <input
              type="number"
              id="n_fireflies"
              value={fireflyParams.n_fireflies}
              onChange={(e) => handleFireflyParamChange('n_fireflies', e.target.value)}
              min="10"
              max="100"
              required
            />
            <small>Więcej = lepsza eksploracja</small>
          </div>

          <div className="form-group">
            <label htmlFor="max_iterations">Liczba iteracji</label>
            <input
              type="number"
              id="max_iterations"
              value={fireflyParams.max_iterations}
              onChange={(e) => handleFireflyParamChange('max_iterations', e.target.value)}
              min="10"
              max="500"
              required
            />
            <small>Więcej = lepsze wyniki</small>
          </div>
        </div>

        <details className="advanced-params">
          <summary>Zaawansowane parametry</summary>

          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="alpha">Alpha (α)</label>
              <input
                type="number"
                id="alpha"
                value={fireflyParams.alpha}
                onChange={(e) => handleFireflyParamChange('alpha', e.target.value)}
                min="0"
                max="1"
                step="0.1"
              />
              <small>Losowość (0-1)</small>
            </div>

            <div className="form-group">
              <label htmlFor="beta_0">Beta₀ (β₀)</label>
              <input
                type="number"
                id="beta_0"
                value={fireflyParams.beta_0}
                onChange={(e) => handleFireflyParamChange('beta_0', e.target.value)}
                min="0"
                max="2"
                step="0.1"
              />
              <small>Atrakcyjność bazowa</small>
            </div>

            <div className="form-group">
              <label htmlFor="gamma">Gamma (γ)</label>
              <input
                type="number"
                id="gamma"
                value={fireflyParams.gamma}
                onChange={(e) => handleFireflyParamChange('gamma', e.target.value)}
                min="0"
                max="5"
                step="0.1"
              />
              <small>Absorpcja światła</small>
            </div>
          </div>
        </details>
      </div>

      <button type="submit" className="btn-primary">
        🚀 Uruchom optymalizację
      </button>
    </form>
  );
}

export default NetworkForm;