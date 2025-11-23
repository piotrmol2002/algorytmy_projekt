"""
====================================================================
PRZYKLAD: Optymalizacja zamknietego systemu terminalowego
====================================================================

Model: 1 stacja obslugi + opóznienie (delay/think time)

Zmienne decyzyjne:
- N: liczba uzytkowników w systemie
- mu: szybkosc obslugi serwera [zadania/s]

Funkcje celu:
- THROUGHPUT: maksymalizacja przepustowosci X
- RESPONSE_TIME: minimalizacja czasu odpowiedzi R
- PROFIT: r*X - C_s*mu - C_N*N

====================================================================
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from models.queueing_network import QueueingNetwork
from algorithms.optimizer import QueueingOptimizer


def run_terminal_optimization(
    objective: str = 'throughput',
    Z: float = 5.0,
    N_init: int = 10,
    mu_init: float = 2.0,
    N_bounds: tuple = (1, 50),
    mu_bounds: tuple = (0.1, 10.0),
    cost_params: dict = None,
    firefly_params: dict = None
):
    """
    Optymalizacja zamknietego systemu terminalowego.

    Args:
        objective: Funkcja celu ('throughput', 'mean_response_time', 'profit')
        Z: Sredni czas myslenia/opoznienia [s]
        N_init: Poczatkowa liczba uzytkowników
        mu_init: Poczatkowa szybkosc obslugi
        N_bounds: Zakres liczby uzytkowników (min, max)
        mu_bounds: Zakres szybkosci obslugi (min, max)
        cost_params: Parametry kosztów dla profit {'r': 10, 'C_s': 1, 'C_N': 0.5}
        firefly_params: Parametry algorytmu Firefly

    Returns:
        Slownik z wynikami optymalizacji
    """

    print("\n" + "=" * 70)
    print("OPTYMALIZACJA ZAMKNIETEGO SYSTEMU TERMINALOWEGO")
    print("=" * 70)

    # Domyslne parametry kosztów
    if cost_params is None:
        cost_params = {'r': 10.0, 'C_s': 1.0, 'C_N': 0.5}

    # Domyslne parametry Firefly
    if firefly_params is None:
        firefly_params = {
            'n_fireflies': 25,
            'max_iterations': 100,
            'alpha': 0.5,
            'beta_0': 1.0,
            'gamma': 1.0
        }

    # Model terminalowy: 1 stacja + delay
    # Delay modelujemy jako bardzo szybka stacje z visit ratio = Z/(Z+S)
    # Ale prostsze: uzywamy jednej stacji i dodajemy Z do czasu odpowiedzi

    # Tworzymy siec z 1 stacja
    # Visit ratio = 1 (kazdy klient odwiedza stacje)
    network = QueueingNetwork(
        num_stations=1,
        num_customers=N_init,
        service_rates=[mu_init],
        num_servers=[1],  # 1 serwer
        station_names=['Serwer']
    )

    print(f"\nParametry modelu:")
    print(f"  Z (czas myslenia): {Z} s")
    print(f"  N poczatkowe: {N_init}")
    print(f"  mu poczatkowe: {mu_init}")
    print(f"  Zakres N: {N_bounds}")
    print(f"  Zakres mu: {mu_bounds}")

    if objective == 'profit':
        print(f"\nParametry ekonomiczne:")
        print(f"  r (zysk/zadanie): {cost_params['r']}")
        print(f"  C_s (koszt serwera): {cost_params['C_s']}")
        print(f"  C_N (koszt zadania): {cost_params['C_N']}")

    print(f"\nFunkcja celu: {objective}")

    # Tworzymy optimizer
    optimizer = QueueingOptimizer(
        network=network,
        objective=objective,
        optimize_vars=['num_customers', 'service_rates'],  # Optymalizujemy N i mu
        customer_bounds=N_bounds,
        service_rate_bounds=mu_bounds,
        cost_params=cost_params,
        firefly_params=firefly_params
    )

    # Uruchamiamy optymalizacje
    results = optimizer.optimize(verbose=True)

    # Wyswietl szczegolowe porownanie
    print("\n" + "=" * 70)
    print("SZCZEGOLOWE POROWNANIE")
    print("=" * 70)

    baseline = results['baseline']
    optimized = results['optimized']

    print("\n{:<30} {:>15} {:>15} {:>15}".format(
        "Parametr", "Przed", "Po", "Zmiana"
    ))
    print("-" * 75)

    # N
    N_before = baseline['network']['num_customers']
    N_after = optimized['network']['num_customers']
    print("{:<30} {:>15} {:>15} {:>+15}".format(
        "N (liczba uzytkowników)", N_before, N_after, N_after - N_before
    ))

    # mu
    mu_before = baseline['network']['service_rates'][0]
    mu_after = optimized['network']['service_rates'][0]
    print("{:<30} {:>15.4f} {:>15.4f} {:>+15.4f}".format(
        "mu (szybkosc obslugi)", mu_before, mu_after, mu_after - mu_before
    ))

    # S = 1/mu
    S_before = 1.0 / mu_before
    S_after = 1.0 / mu_after
    print("{:<30} {:>15.4f} {:>15.4f} {:>+15.4f}".format(
        "S (czas obslugi)", S_before, S_after, S_after - S_before
    ))

    print("-" * 75)

    # R (+ Z dla modelu terminalowego)
    R_before = baseline['metrics']['mean_response_time']
    R_after = optimized['metrics']['mean_response_time']
    print("{:<30} {:>15.4f} {:>15.4f} {:>+15.4f}".format(
        "R (czas odpowiedzi)", R_before, R_after, R_after - R_before
    ))

    # X
    X_before = baseline['metrics']['throughput']
    X_after = optimized['metrics']['throughput']
    print("{:<30} {:>15.4f} {:>15.4f} {:>+15.4f}".format(
        "X (przepustowosc)", X_before, X_after, X_after - X_before
    ))

    # L
    L_before = baseline['metrics']['mean_queue_length']
    L_after = optimized['metrics']['mean_queue_length']
    print("{:<30} {:>15.4f} {:>15.4f} {:>+15.4f}".format(
        "L (dlugosc kolejki)", L_before, L_after, L_after - L_before
    ))

    print("-" * 75)

    # Koszty
    cost_before = cost_params['C_s'] * mu_before + cost_params['C_N'] * N_before
    cost_after = cost_params['C_s'] * mu_after + cost_params['C_N'] * N_after
    print("{:<30} {:>15.4f} {:>15.4f} {:>+15.4f}".format(
        "Koszt calkowity", cost_before, cost_after, cost_after - cost_before
    ))

    # Przychod
    revenue_before = cost_params['r'] * X_before
    revenue_after = cost_params['r'] * X_after
    print("{:<30} {:>15.4f} {:>15.4f} {:>+15.4f}".format(
        "Przychod (r*X)", revenue_before, revenue_after, revenue_after - revenue_before
    ))

    # Zysk
    profit_before = revenue_before - cost_before
    profit_after = revenue_after - cost_after
    print("{:<30} {:>15.4f} {:>15.4f} {:>+15.4f}".format(
        "Zysk", profit_before, profit_after, profit_after - profit_before
    ))

    print("-" * 75)

    # Wartosc funkcji celu
    obj_before = baseline['objective_value']
    obj_after = optimized['objective_value']
    print("{:<30} {:>15.4f} {:>15.4f} {:>+15.4f}".format(
        "Wartosc f. celu", obj_before, obj_after, obj_after - obj_before
    ))

    print("\n" + "=" * 70)

    return results


def main():
    """Przyklad uzycia."""

    # Przyklad 1: Maksymalizacja przepustowosci
    print("\n" + "#" * 70)
    print("# PRZYKLAD 1: Maksymalizacja przepustowosci (THROUGHPUT)")
    print("#" * 70)

    results_throughput = run_terminal_optimization(
        objective='throughput',
        Z=5.0,
        N_init=10,
        mu_init=2.0,
        N_bounds=(1, 50),
        mu_bounds=(0.1, 10.0)
    )

    # Przyklad 2: Minimalizacja czasu odpowiedzi
    print("\n" + "#" * 70)
    print("# PRZYKLAD 2: Minimalizacja czasu odpowiedzi (RESPONSE_TIME)")
    print("#" * 70)

    results_response = run_terminal_optimization(
        objective='mean_response_time',
        Z=5.0,
        N_init=10,
        mu_init=2.0,
        N_bounds=(1, 50),
        mu_bounds=(0.1, 10.0)
    )

    # Przyklad 3: Maksymalizacja zysku
    print("\n" + "#" * 70)
    print("# PRZYKLAD 3: Maksymalizacja zysku (PROFIT)")
    print("#" * 70)

    results_profit = run_terminal_optimization(
        objective='profit',
        Z=5.0,
        N_init=10,
        mu_init=2.0,
        N_bounds=(1, 50),
        mu_bounds=(0.1, 10.0),
        cost_params={'r': 10.0, 'C_s': 1.0, 'C_N': 0.5}
    )


if __name__ == '__main__':
    main()
