"""
====================================================================
GENERATOR RAPORTOW I WYKRESOW DO SPRAWOZDANIA
====================================================================

Tworzy:
- Wykresy zbieznosci algorytmu
- Tabele porownawcze (CSV)
- Podsumowanie optymalizacji

====================================================================
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from models.queueing_network import QueueingNetwork
from algorithms.optimizer import QueueingOptimizer


def save_results_to_csv(results: dict, filename: str, cost_params: dict = None):
    """
    Zapisuje wyniki optymalizacji do pliku CSV.

    Args:
        results: Wyniki z optimizer.optimize()
        filename: Nazwa pliku wyjsciowego
        cost_params: Parametry kosztow
    """
    if cost_params is None:
        cost_params = {'r': 10.0, 'C_s': 1.0, 'C_N': 0.5}

    baseline = results['baseline']
    optimized = results['optimized']

    # Przygotuj dane
    data = [
        ['Parametr', 'Przed optymalizacja', 'Po optymalizacji', 'Zmiana', 'Zmiana %'],

        # Zmienne decyzyjne
        ['N (liczba uzytkownikow)',
         baseline['network']['num_customers'],
         optimized['network']['num_customers'],
         optimized['network']['num_customers'] - baseline['network']['num_customers'],
         ''],

        ['mu (szybkosc obslugi)',
         f"{baseline['network']['service_rates'][0]:.4f}",
         f"{optimized['network']['service_rates'][0]:.4f}",
         f"{optimized['network']['service_rates'][0] - baseline['network']['service_rates'][0]:.4f}",
         ''],

        ['S (czas obslugi)',
         f"{1/baseline['network']['service_rates'][0]:.4f}",
         f"{1/optimized['network']['service_rates'][0]:.4f}",
         f"{1/optimized['network']['service_rates'][0] - 1/baseline['network']['service_rates'][0]:.4f}",
         ''],

        ['', '', '', '', ''],  # Pusta linia

        # Charakterystyki systemu
        ['R (czas odpowiedzi) [s]',
         f"{baseline['metrics']['mean_response_time']:.4f}",
         f"{optimized['metrics']['mean_response_time']:.4f}",
         f"{optimized['metrics']['mean_response_time'] - baseline['metrics']['mean_response_time']:.4f}",
         f"{((optimized['metrics']['mean_response_time'] - baseline['metrics']['mean_response_time']) / baseline['metrics']['mean_response_time'] * 100):.2f}%"],

        ['X (przepustowosc) [zad/s]',
         f"{baseline['metrics']['throughput']:.4f}",
         f"{optimized['metrics']['throughput']:.4f}",
         f"{optimized['metrics']['throughput'] - baseline['metrics']['throughput']:.4f}",
         f"{((optimized['metrics']['throughput'] - baseline['metrics']['throughput']) / baseline['metrics']['throughput'] * 100):.2f}%"],

        ['L (dlugosc kolejki)',
         f"{baseline['metrics']['mean_queue_length']:.4f}",
         f"{optimized['metrics']['mean_queue_length']:.4f}",
         f"{optimized['metrics']['mean_queue_length'] - baseline['metrics']['mean_queue_length']:.4f}",
         f"{((optimized['metrics']['mean_queue_length'] - baseline['metrics']['mean_queue_length']) / baseline['metrics']['mean_queue_length'] * 100):.2f}%"],

        ['', '', '', '', ''],  # Pusta linia

        # Analiza kosztow
        ['Koszt serwera (C_s*mu)',
         f"{cost_params['C_s'] * baseline['network']['service_rates'][0]:.4f}",
         f"{cost_params['C_s'] * optimized['network']['service_rates'][0]:.4f}",
         f"{cost_params['C_s'] * (optimized['network']['service_rates'][0] - baseline['network']['service_rates'][0]):.4f}",
         ''],

        ['Koszt zadan (C_N*N)',
         f"{cost_params['C_N'] * baseline['network']['num_customers']:.4f}",
         f"{cost_params['C_N'] * optimized['network']['num_customers']:.4f}",
         f"{cost_params['C_N'] * (optimized['network']['num_customers'] - baseline['network']['num_customers']):.4f}",
         ''],

        ['Koszt calkowity',
         f"{cost_params['C_s'] * baseline['network']['service_rates'][0] + cost_params['C_N'] * baseline['network']['num_customers']:.4f}",
         f"{cost_params['C_s'] * optimized['network']['service_rates'][0] + cost_params['C_N'] * optimized['network']['num_customers']:.4f}",
         f"{(cost_params['C_s'] * optimized['network']['service_rates'][0] + cost_params['C_N'] * optimized['network']['num_customers']) - (cost_params['C_s'] * baseline['network']['service_rates'][0] + cost_params['C_N'] * baseline['network']['num_customers']):.4f}",
         ''],

        ['Przychod (r*X)',
         f"{cost_params['r'] * baseline['metrics']['throughput']:.4f}",
         f"{cost_params['r'] * optimized['metrics']['throughput']:.4f}",
         f"{cost_params['r'] * (optimized['metrics']['throughput'] - baseline['metrics']['throughput']):.4f}",
         ''],

        ['Zysk netto',
         f"{cost_params['r'] * baseline['metrics']['throughput'] - cost_params['C_s'] * baseline['network']['service_rates'][0] - cost_params['C_N'] * baseline['network']['num_customers']:.4f}",
         f"{cost_params['r'] * optimized['metrics']['throughput'] - cost_params['C_s'] * optimized['network']['service_rates'][0] - cost_params['C_N'] * optimized['network']['num_customers']:.4f}",
         '',
         ''],
    ]

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)

    print(f"Wyniki zapisane do: {filename}")


def save_history_to_csv(history: dict, filename: str):
    """
    Zapisuje historie optymalizacji do CSV.

    Args:
        history: Historia z results['history']
        filename: Nazwa pliku
    """
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Iteracja', 'Najlepsza wartosc', 'Srednia wartosc', 'Najgorsza wartosc'])

        for i in range(len(history['best_values'])):
            writer.writerow([
                i + 1,
                f"{history['best_values'][i]:.6f}",
                f"{history['mean_values'][i]:.6f}",
                f"{history['worst_values'][i]:.6f}"
            ])

    print(f"Historia zapisana do: {filename}")


def plot_convergence(history: dict, title: str, filename: str):
    """
    Tworzy wykres zbieznosci algorytmu.

    Args:
        history: Historia optymalizacji
        title: Tytul wykresu
        filename: Nazwa pliku wyjsciowego
    """
    plt.figure(figsize=(10, 6))

    iterations = range(1, len(history['best_values']) + 1)

    plt.plot(iterations, history['best_values'], 'b-', linewidth=2, label='Najlepsza wartosc')
    plt.plot(iterations, history['mean_values'], 'g--', linewidth=1, label='Srednia wartosc')
    plt.fill_between(iterations, history['best_values'], history['worst_values'],
                     alpha=0.3, color='blue', label='Zakres wartosci')

    plt.xlabel('Iteracja', fontsize=12)
    plt.ylabel('Wartosc funkcji celu', fontsize=12)
    plt.title(title, fontsize=14)
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Wykres zapisany do: {filename}")


def plot_comparison(baseline: dict, optimized: dict, cost_params: dict, filename: str):
    """
    Tworzy wykres porownawczy przed/po optymalizacji.

    Args:
        baseline: Wyniki przed optymalizacja
        optimized: Wyniki po optymalizacji
        cost_params: Parametry kosztow
        filename: Nazwa pliku
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 1. Porownanie N i mu
    ax1 = axes[0, 0]
    metrics = ['N', 'mu']
    before = [baseline['network']['num_customers'], baseline['network']['service_rates'][0]]
    after = [optimized['network']['num_customers'], optimized['network']['service_rates'][0]]

    x = np.arange(len(metrics))
    width = 0.35

    ax1.bar(x - width/2, before, width, label='Przed', color='#ff7f7f')
    ax1.bar(x + width/2, after, width, label='Po', color='#7fbf7f')
    ax1.set_ylabel('Wartosc')
    ax1.set_title('Zmienne decyzyjne')
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. Porownanie R, X, L
    ax2 = axes[0, 1]
    metrics = ['R [s]', 'X [zad/s]', 'L']
    before = [
        baseline['metrics']['mean_response_time'],
        baseline['metrics']['throughput'],
        baseline['metrics']['mean_queue_length']
    ]
    after = [
        optimized['metrics']['mean_response_time'],
        optimized['metrics']['throughput'],
        optimized['metrics']['mean_queue_length']
    ]

    x = np.arange(len(metrics))
    ax2.bar(x - width/2, before, width, label='Przed', color='#ff7f7f')
    ax2.bar(x + width/2, after, width, label='Po', color='#7fbf7f')
    ax2.set_ylabel('Wartosc')
    ax2.set_title('Charakterystyki systemu')
    ax2.set_xticks(x)
    ax2.set_xticklabels(metrics)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 3. Analiza kosztow
    ax3 = axes[1, 0]

    cost_before = cost_params['C_s'] * baseline['network']['service_rates'][0] + \
                  cost_params['C_N'] * baseline['network']['num_customers']
    cost_after = cost_params['C_s'] * optimized['network']['service_rates'][0] + \
                 cost_params['C_N'] * optimized['network']['num_customers']

    revenue_before = cost_params['r'] * baseline['metrics']['throughput']
    revenue_after = cost_params['r'] * optimized['metrics']['throughput']

    profit_before = revenue_before - cost_before
    profit_after = revenue_after - cost_after

    metrics = ['Koszt', 'Przychod', 'Zysk']
    before = [cost_before, revenue_before, profit_before]
    after = [cost_after, revenue_after, profit_after]

    x = np.arange(len(metrics))
    ax3.bar(x - width/2, before, width, label='Przed', color='#ff7f7f')
    ax3.bar(x + width/2, after, width, label='Po', color='#7fbf7f')
    ax3.set_ylabel('Wartosc')
    ax3.set_title('Analiza ekonomiczna')
    ax3.set_xticks(x)
    ax3.set_xticklabels(metrics)
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 4. Procentowa zmiana
    ax4 = axes[1, 1]

    metrics = ['R', 'X', 'L', 'Zysk']
    changes = [
        ((optimized['metrics']['mean_response_time'] - baseline['metrics']['mean_response_time']) /
         baseline['metrics']['mean_response_time'] * 100),
        ((optimized['metrics']['throughput'] - baseline['metrics']['throughput']) /
         baseline['metrics']['throughput'] * 100),
        ((optimized['metrics']['mean_queue_length'] - baseline['metrics']['mean_queue_length']) /
         baseline['metrics']['mean_queue_length'] * 100),
        ((profit_after - profit_before) / profit_before * 100) if profit_before != 0 else 0
    ]

    colors = ['#7fbf7f' if c > 0 else '#ff7f7f' for c in changes]
    # Dla R i L ujemna zmiana jest dobra
    colors[0] = '#7fbf7f' if changes[0] < 0 else '#ff7f7f'
    colors[2] = '#7fbf7f' if changes[2] < 0 else '#ff7f7f'

    ax4.bar(metrics, changes, color=colors)
    ax4.set_ylabel('Zmiana [%]')
    ax4.set_title('Procentowa zmiana')
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Wykres porownawczy zapisany do: {filename}")


def run_example_for_report():
    """
    Uruchamia przykladowa optymalizacje i generuje materialy do sprawozdania.
    """

    print("\n" + "=" * 70)
    print("GENEROWANIE MATERIALOW DO SPRAWOZDANIA")
    print("=" * 70)

    # Katalog wyjsciowy
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
    os.makedirs(output_dir, exist_ok=True)

    # Parametry przykladowego problemu
    # ================================
    # Scenariusz: System bankomatow
    # - Z = 30s (sredni czas myslenia klienta)
    # - Poczatkowo: N=5 klientow, mu=0.5 (obsluga 2 min/klient)
    # - Cel: Maksymalizacja zysku
    # ================================

    Z = 30.0  # czas myslenia [s]
    N_init = 5
    mu_init = 0.5
    N_bounds = (1, 30)
    mu_bounds = (0.1, 2.0)
    cost_params = {
        'r': 50.0,    # zysk z obslugi klienta
        'C_s': 10.0,  # koszt mocy serwera
        'C_N': 2.0    # koszt klienta w systemie
    }

    print("\nPRZYKLADOWY PROBLEM: System bankomatow")
    print("-" * 70)
    print(f"Z (czas myslenia): {Z} s")
    print(f"N poczatkowe: {N_init}")
    print(f"mu poczatkowe: {mu_init} (czas obslugi: {1/mu_init:.1f} s)")
    print(f"Zakres N: {N_bounds}")
    print(f"Zakres mu: {mu_bounds}")
    print(f"r (zysk/klient): {cost_params['r']}")
    print(f"C_s (koszt serwera): {cost_params['C_s']}")
    print(f"C_N (koszt klienta): {cost_params['C_N']}")

    # Utworz siec
    network = QueueingNetwork(
        num_stations=1,
        num_customers=N_init,
        service_rates=[mu_init],
        num_servers=[1],
        station_names=['Bankomat']
    )

    # Optymalizuj dla PROFIT
    print("\n" + "=" * 70)
    print("OPTYMALIZACJA DLA FUNKCJI CELU: PROFIT")
    print("=" * 70)

    optimizer = QueueingOptimizer(
        network=network,
        objective='profit',
        optimize_vars=['num_customers', 'service_rates'],
        customer_bounds=N_bounds,
        service_rate_bounds=mu_bounds,
        cost_params=cost_params,
        firefly_params={
            'n_fireflies': 30,
            'max_iterations': 150,
            'alpha': 0.5,
            'beta_0': 1.0,
            'gamma': 1.0
        }
    )

    results = optimizer.optimize(verbose=True)

    # Zapisz wyniki
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Tabela wynikow CSV
    csv_results = os.path.join(output_dir, f'wyniki_optymalizacji_{timestamp}.csv')
    save_results_to_csv(results, csv_results, cost_params)

    # 2. Historia optymalizacji CSV
    csv_history = os.path.join(output_dir, f'historia_optymalizacji_{timestamp}.csv')
    save_history_to_csv(results['history'], csv_history)

    # 3. Wykres zbieznosci
    plot_convergence(
        results['history'],
        'Zbieznosc algorytmu Firefly - Maksymalizacja zysku',
        os.path.join(output_dir, f'wykres_zbieznosci_{timestamp}.png')
    )

    # 4. Wykres porownawczy
    plot_comparison(
        results['baseline'],
        results['optimized'],
        cost_params,
        os.path.join(output_dir, f'wykres_porownanie_{timestamp}.png')
    )

    # Podsumowanie
    print("\n" + "=" * 70)
    print("PODSUMOWANIE")
    print("=" * 70)

    baseline = results['baseline']
    optimized = results['optimized']

    profit_before = cost_params['r'] * baseline['metrics']['throughput'] - \
                    cost_params['C_s'] * baseline['network']['service_rates'][0] - \
                    cost_params['C_N'] * baseline['network']['num_customers']

    profit_after = cost_params['r'] * optimized['metrics']['throughput'] - \
                   cost_params['C_s'] * optimized['network']['service_rates'][0] - \
                   cost_params['C_N'] * optimized['network']['num_customers']

    print(f"\nZysk przed optymalizacja: {profit_before:.2f}")
    print(f"Zysk po optymalizacji: {profit_after:.2f}")
    print(f"Poprawa: {profit_after - profit_before:.2f} ({(profit_after - profit_before) / profit_before * 100:.1f}%)")

    print(f"\nPliki zapisane w: {output_dir}")
    print("=" * 70)

    return results


if __name__ == '__main__':
    run_example_for_report()
