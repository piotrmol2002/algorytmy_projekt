import React, { useState, useEffect } from 'react';

// Wzory matematyczne dla wybranych funkcji celu
const OBJECTIVE_FORMULAS = {
  mean_response_time: {
    title: 'Średni czas odpowiedzi',
    formula: (
      <>
        R = W + S = L/X + 1/μ
      </>
    ),
    legend: [
      'R - średni czas odpowiedzi (czas w systemie)',
      'W - średni czas oczekiwania w kolejce',
      'S - średni czas obsługi',
      'L - średnia długość kolejki',
      'X - przepustowość systemu',
      'μ - szybkość obsługi',
      'Cel: minimalizacja (krótszy czas = lepiej)'
    ]
  },
  mean_queue_length: {
    title: 'Średnia długość kolejki',
    formula: (
      <>
        L = λ * W
      </>
    ),
    legend: [
      'L – średnia liczba klientów w kolejce',
      'λ – średnia intensywność napływu zgłoszeń',
      'W – średni czas oczekiwania w kolejce',
      'Cel: minimalizacja → krótsze kolejki'
    ]
  },
  max_queue_length: {
    title: 'Maksymalna długość kolejki',
    formula: (
      <>
        L<sub>max</sub> = max(L₁, L₂, ..., Lₖ)
      </>
    ),
    legend: [
      'Lₖ – średnia długość kolejki na stacji k',
      'Cel: minimalizacja → unikanie wąskich gardeł'
    ]
  },
  utilization_variance: {
    title: 'Równomierność obciążenia (Wariancja wykorzystania)',
    formula: (
      <>
        σ²(ρ) = Var(ρ₁, ρ₂, ..., ρₖ)
      </>
    ),
    legend: [
      'ρᵢ - wykorzystanie serwera na stacji i (wartość 0-1)',
      'σ²(ρ) - wariancja wykorzystania',
      'Cel: minimalizacja → równomierne obciążenie wszystkich serwerów'
    ]
  },
  throughput: {
    title: 'Przepustowość systemu',
    formula: (
      <>
        X = N / R
      </>
    ),
    legend: [
      'X - przepustowość (throughput) [zadania/s]',
      'N - liczba klientów w systemie',
      'R - średni czas odpowiedzi',
      'Cel: maksymalizacja (większa przepustowość = lepiej)'
    ]
  },
  profit: {
    title: 'Zysk ekonomiczny',
    formula: (
      <>
        Profit = r·X - Cₛ·∑μᵢ - Cₙ·N
      </>
    ),
    legend: [
      'r – przychód z jednego zadania',
      'X – przepustowość systemu',
      'Cₛ – koszt jednostkowy mocy obliczeniowej',
      'μᵢ – szybkość obsługi na stacji i',
      'Cₙ – koszt utrzymania zadania w systemie',
      'N – średnia liczba zadań w systemie',
      'Cel: maksymalizacja'
    ]
  },
  response_time_percentile: {
    title: 'Percentyl czasu odpowiedzi (np. 95-ty)',
    formula: (
      <>
        Rₚ = Percentile(R, p)
      </>
    ),
    legend: [
      'Rₚ - p-ty percentyl czasu odpowiedzi',
      'R - zbiór czasów odpowiedzi',
      'p - próg percentyla (np. 95)',
      'Cel: minimalizacja → ograniczenie skrajnie długich czasów'
    ]
  },
  generic_weighted_objective: {
    title: 'Generyczna funkcja ważona',
    formula: (
      <>
        f = w₁·R + w₂·L + w₃·σ²(ρ) + ...
      </>
    ),
    legend: [
        'f - wartość funkcji celu',
        'wᵢ - waga dla i-tego kryterium',
        'R - średni czas odpowiedzi',
        'L - średnia długość kolejki',
        'σ²(ρ) - wariancja wykorzystania',
        'Cel: minimalizacja (wymaga zdefiniowania wag)'
    ]
  },
  weighted_objective: {
    title: 'Kompromisowa wielokryterialna',
    formula: (
      <>
        f = w₁(-R) + w₂X + w₃(-L)
      </>
    ),
    legend: [
      'f – wartość funkcji celu',
      'w₁, w₂, w₃ – wagi dla kryteriów',
      'R – średni czas odpowiedzi (minimalizacja)',
      'X – przepustowość (maksymalizacja)',
      'L – średnia długość kolejki (minimalizacja)',
      'Cel: maksymalizacja'
    ]
  }
};

const WEIGHT_CRITERIA = {
  response_time: 'Średni czas odpowiedzi',
  queue_length: 'Średnia długość kolejki',
  utilization_variance: 'Wariancja wykorzystania',
  max_queue: 'Maksymalna długość kolejki',
  cost: 'Koszt (liczba serwerów)'
};

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

  const [costParams, setCostParams] = useState({
    profit_r: 10.0,
    profit_Cs: 1.0,
    profit_Cn: 0.5
  });

  const [weightParams, setWeightParams] = useState({
    weight_w1: 0.33,
    weight_w2: 0.34,
    weight_w3: 0.33
  });

  const [weights, setWeights] = useState({
    response_time: 0.5,
    queue_length: 0.5,
    utilization_variance: 0.0,
    max_queue: 0.0,
    cost: 0.0
  });

  const [totalWeight, setTotalWeight] = useState(1.0);
  const [weightError, setWeightError] = useState(false);

  useEffect(() => {
    const sum = Object.values(weights).reduce((acc, w) => acc + w, 0);
    setTotalWeight(sum);
    setWeightError(Math.abs(sum - 1.0) > 1e-9);
  }, [weights]);

  const handleWeightChange = (criterion, value) => {
    setWeights(prev => ({
      ...prev,
      [criterion]: parseFloat(value) || 0
    }));
  };

  const handleAutoAdjustWeights = () => {
    if (totalWeight === 0) return;
    const adjusted = {};
    for (const key in weights) {
      adjusted[key] = weights[key] / totalWeight;
    }
    setWeights(adjusted);
  };


  const handleNumStationsChange = (value) => {
    const newNum = parseInt(value);
    setNumStations(newNum);

    const newStations = [];
    for (let i = 0; i < newNum; i++) {
      if (i < stations.length) newStations.push(stations[i]);
      else
        newStations.push({
          name: `Stacja ${i + 1}`,
          serviceRate: 3.0 + Math.random() * 3,
          numServers: 2
        });
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

    const formData = {
      profit_r: costParams.profit_r,
      profit_Cs: costParams.profit_Cs,
      profit_Cn: costParams.profit_Cn,
      weight_w1: weightParams.weight_w1,
      weight_w2: weightParams.weight_w2,
      weight_w3: weightParams.weight_w3,
      weights: weights,
      num_stations: numStations,
      num_customers: numCustomers,
      objective: selectedObjective,
      optimize_vars: ['num_servers'],
      server_min: serverMin,
      server_max: serverMax,
      ...fireflyParams
    };

    stations.forEach((station, i) => {
      formData[`station_name_${i}`] = station.name;
      formData[`service_rate_${i}`] = station.serviceRate;
      formData[`num_servers_${i}`] = station.numServers;
    });

    onSubmit(formData);
  };

  return (
    <form className="network-form" onSubmit={handleSubmit}>
      {/* === 1. Definicja sieci kolejkowej === */}
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

      {/* === 2. Konfiguracja stacji === */}
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

      {/* === 3. Funkcja celu === */}
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
            {objectives.map((obj) => (
              <option key={obj.id} value={obj.id}>
                {obj.name} – {obj.description}
              </option>
            ))}
          </select>
        </div>

        {/* 📐 Sekcja ze wzorem funkcji celu */}
        {OBJECTIVE_FORMULAS[selectedObjective] && (
          <div className="objective-math-card">
            <h3>📐 Wzór funkcji celu</h3>
            <p className="objective-math-title">
              {OBJECTIVE_FORMULAS[selectedObjective].title}
            </p>
            <p className="objective-math-formula">
              {OBJECTIVE_FORMULAS[selectedObjective].formula}
            </p>
            <ul className="objective-math-legend">
              {OBJECTIVE_FORMULAS[selectedObjective].legend.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        )}

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

        {/* Parametry kosztów dla funkcji "profit" */}
        {selectedObjective === 'profit' && (
          <div className="cost-params-section">
            <h3>Parametry kosztów</h3>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="profit_r">r (zysk z zadania)</label>
                <input
                  type="number"
                  id="profit_r"
                  step="0.1"
                  value={costParams.profit_r}
                  onChange={(e) => setCostParams({...costParams, profit_r: parseFloat(e.target.value)})}
                  min="0"
                />
                <small>Przychód z każdego przetworzonego zadania</small>
              </div>

              <div className="form-group">
                <label htmlFor="profit_Cs">C_s (koszt serwera)</label>
                <input
                  type="number"
                  id="profit_Cs"
                  step="0.1"
                  value={costParams.profit_Cs}
                  onChange={(e) => setCostParams({...costParams, profit_Cs: parseFloat(e.target.value)})}
                  min="0"
                />
                <small>Koszt jednostkowy mocy serwera</small>
              </div>

              <div className="form-group">
                <label htmlFor="profit_Cn">C_N (koszt klienta)</label>
                <input
                  type="number"
                  id="profit_Cn"
                  step="0.1"
                  value={costParams.profit_Cn}
                  onChange={(e) => setCostParams({...costParams, profit_Cn: parseFloat(e.target.value)})}
                  min="0"
                />
                <small>Koszt utrzymania klienta w systemie</small>
              </div>
            </div>
          </div>
        )}

        {/* Parametry wag dla funkcji "weighted_objective" */}
        {selectedObjective === 'weighted_objective' && (
          <div className="weight-params-section">
            <h3>Wagi funkcji wielokryterialnej</h3>
            <p style={{fontSize: '0.9em', color: '#666', marginBottom: '15px'}}>
              Formula: f = w1*(-R) + w2*X + w3*(-L)
            </p>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="weight_w1">w1 (waga czasu odpowiedzi)</label>
                <input
                  type="number"
                  id="weight_w1"
                  step="0.01"
                  value={weightParams.weight_w1}
                  onChange={(e) => setWeightParams({...weightParams, weight_w1: parseFloat(e.target.value)})}
                  min="0"
                  max="1"
                />
                <small>Im wieksze w1, tym wiekszy wplyw czasu odpowiedzi</small>
              </div>

              <div className="form-group">
                <label htmlFor="weight_w2">w2 (waga przepustowosci)</label>
                <input
                  type="number"
                  id="weight_w2"
                  step="0.01"
                  value={weightParams.weight_w2}
                  onChange={(e) => setWeightParams({...weightParams, weight_w2: parseFloat(e.target.value)})}
                  min="0"
                  max="1"
                />
                <small>Im wieksze w2, tym wiekszy wplyw przepustowosci</small>
              </div>

              <div className="form-group">
                <label htmlFor="weight_w3">w3 (waga dlugosci kolejki)</label>
                <input
                  type="number"
                  id="weight_w3"
                  step="0.01"
                  value={weightParams.weight_w3}
                  onChange={(e) => setWeightParams({...weightParams, weight_w3: parseFloat(e.target.value)})}
                  min="0"
                  max="1"
                />
                <small>Im wieksze w3, tym wiekszy wplyw dlugosci kolejki</small>
              </div>
            </div>
            <p style={{fontSize: '0.85em', color: '#888', marginTop: '10px'}}>
              Sugerowane: w1 + w2 + w3 = 1.0
            </p>
          </div>
        )}

        {/* Parametry wag dla funkcji "generic_weighted_objective" */}
        {selectedObjective === 'generic_weighted_objective' && (
          <div className="weight-params-section">
            <h3>Ustawienia wag dla kryteriów</h3>
            <p style={{fontSize: '0.9em', color: '#666', marginBottom: '15px'}}>
              Zdefiniuj, jak ważne jest dla Ciebie każde z kryteriów. Suma wszystkich wag musi wynosić 1.0.
            </p>
            <div className="form-grid">
              {Object.entries(WEIGHT_CRITERIA).map(([key, name]) => (
                <div className="form-group" key={key}>
                  <label htmlFor={`weight_${key}`}>{name}</label>
                  <input
                    type="number"
                    id={`weight_${key}`}
                    step="0.01"
                    min="0"
                    max="1"
                    value={weights[key]}
                    onChange={(e) => handleWeightChange(key, e.target.value)}
                  />
                </div>
              ))}
            </div>
            <div className="weight-validation">
              {weightError ? (
                <div className="weight-validation-error">
                  <strong>⚠️ Suma wag ({totalWeight.toFixed(2)}) nie wynosi 1.0.</strong> Różnica: {(totalWeight - 1.0).toFixed(2)}.
                  <button type="button" onClick={handleAutoAdjustWeights} className="btn-secondary" style={{marginLeft: '15px'}} disabled={totalWeight === 0}>
                    Auto-dopasuj
                  </button>
                </div>
              ) : (
                <div className="weight-validation-ok">
                  <strong>✅ Suma wag wynosi {totalWeight.toFixed(2)}.</strong>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* === 4. Parametry Firefly === */}
      <div className="form-section">
        <h2>4. Parametry algorytmu Firefly</h2>

        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="n_fireflies" title="Liczba agentow przeszukujacych przestrzen rozwiazan. Kazdy swietlik reprezentuje jedno potencjalne rozwiazanie. Wieksza liczba = lepsze pokrycie przestrzeni, ale dluzszy czas obliczen.">
              Liczba swietlikow
              <span className="tooltip-icon" title="Liczba agentow przeszukujacych przestrzen rozwiazan. Kazdy swietlik reprezentuje jedno potencjalne rozwiazanie. Wieksza liczba = lepsze pokrycie przestrzeni, ale dluzszy czas obliczen.">?</span>
            </label>
            <input
              type="number"
              id="n_fireflies"
              value={fireflyParams.n_fireflies}
              onChange={(e) => handleFireflyParamChange('n_fireflies', e.target.value)}
              min="10"
              max="100"
              required
            />
            <small>Wiecej = lepsza eksploracja (10-100)</small>
          </div>

          <div className="form-group">
            <label htmlFor="max_iterations" title="Liczba cykli optymalizacji. W kazdej iteracji swietliki poruszaja sie w kierunku lepszych rozwiazan. Wiecej iteracji = lepsze wyniki, ale dluzszy czas.">
              Liczba iteracji
              <span className="tooltip-icon" title="Liczba cykli optymalizacji. W kazdej iteracji swietliki poruszaja sie w kierunku lepszych rozwiazan. Wiecej iteracji = lepsze wyniki, ale dluzszy czas.">?</span>
            </label>
            <input
              type="number"
              id="max_iterations"
              value={fireflyParams.max_iterations}
              onChange={(e) => handleFireflyParamChange('max_iterations', e.target.value)}
              min="10"
              max="500"
              required
            />
            <small>Wiecej = lepsze wyniki (10-500)</small>
          </div>
        </div>

        <details className="advanced-params">
          <summary>Zaawansowane parametry</summary>

          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="alpha" title="Wspolczynnik losowosci ruchu. Kontroluje eksploracje vs eksploatacje. Alpha=0: tylko ruch do lepszych, Alpha=1: duzo losowosci. Typowo: 0.2-0.5">
                Alpha (α)
                <span className="tooltip-icon" title="Wspolczynnik losowosci ruchu. Kontroluje eksploracje vs eksploatacje. Alpha=0: tylko ruch do lepszych rozwiazan, Alpha=1: duzo losowego przeszukiwania. Typowo: 0.2-0.5">?</span>
              </label>
              <input
                type="number"
                id="alpha"
                value={fireflyParams.alpha}
                onChange={(e) => handleFireflyParamChange('alpha', e.target.value)}
                min="0"
                max="1"
                step="0.1"
              />
              <small>Losowosc ruchu (0=brak, 1=max)</small>
            </div>

            <div className="form-group">
              <label htmlFor="beta_0" title="Bazowa atrakcyjnosc swietlika przy zerowej odleglosci. Okreslajak silnie swietliki przyciagaja sie nawzajem. Wyzsze wartosci = silniejsze przyciaganie do lepszych rozwiazan.">
                Beta0 (β0)
                <span className="tooltip-icon" title="Bazowa atrakcyjnosc swietlika przy zerowej odleglosci. Okresla jak silnie swietliki przyciagaja sie nawzajem. Wyzsze wartosci = silniejsze przyciaganie do lepszych rozwiazan. Typowo: 0.5-2.0">?</span>
              </label>
              <input
                type="number"
                id="beta_0"
                value={fireflyParams.beta_0}
                onChange={(e) => handleFireflyParamChange('beta_0', e.target.value)}
                min="0"
                max="2"
                step="0.1"
              />
              <small>Sila przyciagania (0.5-2.0)</small>
            </div>

            <div className="form-group">
              <label htmlFor="gamma" title="Wspolczynnik absorpcji swiatla. Okresla jak szybko atrakcyjnosc maleje z odlegloscia. Gamma=0: atrakcyjnosc stala, Gamma wysoka: tylko bliskie swietliki przyciagaja.">
                Gamma (γ)
                <span className="tooltip-icon" title="Wspolczynnik absorpcji swiatla. Okresla jak szybko atrakcyjnosc maleje z odlegloscia. Gamma=0: atrakcyjnosc stala niezaleznie od odleglosci, Gamma wysoka: tylko bliskie swietliki sie przyciagaja. Typowo: 0.1-2.0">?</span>
              </label>
              <input
                type="number"
                id="gamma"
                value={fireflyParams.gamma}
                onChange={(e) => handleFireflyParamChange('gamma', e.target.value)}
                min="0"
                max="5"
                step="0.1"
              />
              <small>Spadek atrakcyjnosci z odlegloscia</small>
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
