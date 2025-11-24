"""
====================================================================
GŁÓWNA APLIKACJA WEBOWA - FLASK
====================================================================

Aplikacja webowa do optymalizacji systemów kolejkowych algorytmem Firefly.

URUCHOMIENIE:
-------------
python app.py

Następnie otwórz przeglądarkę: http://localhost:5000

====================================================================
"""

from flask import Flask, render_template, request, jsonify
import numpy as np
import sys
import traceback

from models.queueing_network import QueueingNetwork
from models.objective_functions import list_available_objectives
from algorithms.optimizer import QueueingOptimizer
from visualization.plots import generate_all_plots


app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.config['SECRET_KEY'] = 'firefly-optimizer-secret-key'


@app.route('/')
def index():
    """
    Strona główna z formularzem do definiowania sieci.
    """
    # Lista dostępnych funkcji celu
    objectives = list_available_objectives()

    return render_template('index.html', objectives=objectives)


@app.route('/optimize', methods=['POST'])
def optimize():
    """
    Endpoint do uruchomienia optymalizacji.

    Przyjmuje dane z formularza, tworzy sieć, uruchamia optymalizację
    i zwraca wyniki z wykresami.
    """
    try:
        # KROK 1: Pobierz dane z formularza
        data = request.get_json()

        num_stations = int(data['num_stations'])
        num_customers = int(data['num_customers'])

        # Parsuj parametry stacji
        service_rates = [float(data[f'service_rate_{i}']) for i in range(num_stations)]
        num_servers = [int(data[f'num_servers_{i}']) for i in range(num_stations)]
        station_names = [data.get(f'station_name_{i}', f'Stacja {i+1}') for i in range(num_stations)]

        # Funkcja celu
        objective = data['objective']

        # Parametry optymalizacji
        optimize_vars = data.get('optimize_vars', ['num_servers'])
        server_min = int(data.get('server_min', 1))
        server_max = int(data.get('server_max', 10))

        # Nowe parametry dla rozszerzonej optymalizacji
        customer_min = int(data.get('customer_min', 1))
        customer_max = int(data.get('customer_max', 100))
        mu_min = float(data.get('mu_min', 0.1))
        mu_max = float(data.get('mu_max', 10.0))

        # Parametry kosztow dla funkcji profit
        cost_params = {
            'r': float(data.get('profit_r', 10.0)),
            'C_s': float(data.get('profit_Cs', 1.0)),
            'C_N': float(data.get('profit_Cn', 0.5))
        }

        # Parametry wag dla weighted_objective
        weights_params = {
            'w1': float(data.get('weight_w1', 0.33)),
            'w2': float(data.get('weight_w2', 0.34)),
            'w3': float(data.get('weight_w3', 0.33))
        }


        # Parametry Firefly
        n_fireflies = int(data.get('n_fireflies', 25))
        max_iterations = int(data.get('max_iterations', 100))
        alpha = float(data.get('alpha', 0.5))
        beta_0 = float(data.get('beta_0', 1.0))
        gamma = float(data.get('gamma', 1.0))

        # KROK 2: Utwórz sieć kolejkową
        network = QueueingNetwork(
            num_stations=num_stations,
            num_customers=num_customers,
            service_rates=service_rates,
            num_servers=num_servers,
            station_names=station_names
        )

        # KROK 3: Utwórz optimizer
        optimizer = QueueingOptimizer(
            network=network,
            objective=objective,
            optimize_vars=optimize_vars,
            server_bounds=(server_min, server_max),
            customer_bounds=(customer_min, customer_max),
            service_rate_bounds=(mu_min, mu_max),
            cost_params=cost_params,
            weights_params=weights_params,
            firefly_params={
                'n_fireflies': n_fireflies,
                'max_iterations': max_iterations,
                'alpha': alpha,
                'beta_0': beta_0,
                'gamma': gamma
            }
        )

        # KROK 4: Uruchom optymalizację
        results = optimizer.optimize(verbose=False)

        # KROK 5: Generuj wykresy
        plots = generate_all_plots(results)

        # KROK 6: Przygotuj odpowiedź
        response = {
            'success': True,
            'results': {
                'baseline': results['baseline'],
                'optimized': results['optimized'],
                'improvement': results['improvement'],
                'optimization_info': results['optimization_info'],
                'cost': results.get('cost')
            },
            'plots': plots
        }

        return jsonify(response)

    except Exception as e:
        # Obsługa błędów
        error_trace = traceback.format_exc()
        print(f"BŁĄD w optymalizacji: {error_trace}")

        return jsonify({
            'success': False,
            'error': str(e),
            'trace': error_trace
        }), 400


@app.route('/api/objectives')
def get_objectives():
    """
    API endpoint zwracający listę dostępnych funkcji celu.
    """
    objectives = list_available_objectives()
    return jsonify(objectives)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("FIREFLY QUEUEING OPTIMIZER - Uruchamianie serwera")
    print("="*70)
    print("Adres: http://localhost:5000")
    print("Otworz ten adres w przegladarce, aby korzystac z aplikacji")
    print("Nacisnij Ctrl+C aby zatrzymac serwer")
    print("="*70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
