"""
====================================================================
OPTYMALIZACJA ZAMKNIETEGO SYSTEMU KOLEJKOWEGO - ALGORYTM FIREFLY
====================================================================

Program optymalizuje zamkniety model terminalowy (1 stacja + delay)
za pomoca algorytmu swietlika (Firefly Algorithm).

Model systemu:
- Z: sredni czas "myslenia" (delay) [s]
- N: liczba uzytkownikow/zadan w systemie (zmienna decyzyjna)
- mu: szybkosc obslugi serwera [zadania/s] (zmienna decyzyjna)
- S = 1/mu: sredni czas obslugi

Funkcje celu:
- THROUGHPUT: maksymalizacja przepustowosci X
- RESPONSE_TIME: minimalizacja czasu odpowiedzi R
- PROFIT: funkcja ekonomiczna r*X - Cs*mu - CN*N

Autor: Firefly Optimizer
====================================================================
"""

import random
import math
import json
import csv
import argparse
from typing import Dict, Any, Tuple, List
from enum import Enum


class ObjectiveType(Enum):
    """Typy funkcji celu."""
    THROUGHPUT = "THROUGHPUT"
    RESPONSE_TIME = "RESPONSE_TIME"
    PROFIT = "PROFIT"


def mva(N: int, mu: float, Z: float) -> Tuple[float, float, float]:
    """
    Mean Value Analysis dla zamknietego modelu terminalowego.

    Model: 1 stacja obslugi + 1 delay (Z)

    Algorytm iteracyjny:
    L(0) = 0
    dla n = 1..N:
        R(n) = S * (1 + L(n-1))
        X(n) = n / (Z + R(n))
        L(n) = X(n) * R(n)

    Args:
        N: Liczba uzytkownikow w systemie (int >= 1)
        mu: Szybkosc obslugi [zadania/s] (float > 0)
        Z: Sredni czas myslenia [s] (float >= 0)

    Returns:
        Tuple (R, X, L):
        - R: Sredni czas odpowiedzi (response time) [s]
        - X: Przepustowosc (throughput) [zadania/s]
        - L: Srednia dlugosc kolejki (queue length)
    """
    if N < 1 or mu <= 0:
        return (float('inf'), 0.0, float('inf'))

    S = 1.0 / mu  # Sredni czas obslugi
    L = 0.0       # L(0) = 0

    for n in range(1, N + 1):
        R = S * (1 + L)           # R(n) = S * (1 + L(n-1))
        X = n / (Z + R)           # X(n) = n / (Z + R(n))
        L = X * R                 # L(n) = X(n) * R(n)

    return (R, X, L)


def evaluate(theta: Tuple[float, float], params: Dict[str, Any], objective: ObjectiveType) -> float:
    """
    Oblicza wartosc funkcji celu dla danego rozwiazania.

    Args:
        theta: Para (N_real, mu_real) - pozycja swietlika
        params: Slownik parametrow:
            - Z: sredni czas myslenia
            - N_min, N_max: zakres N
            - mu_min, mu_max: zakres mu
            - r: zysk z obslugi jednego zadania (dla PROFIT)
            - C_s: koszt jednostkowy mocy serwera (dla PROFIT)
            - C_N: koszt jednego zadania w systemie (dla PROFIT)
        objective: Typ funkcji celu

    Returns:
        Wartosc funkcji celu (do MAKSYMALIZACJI przez algorytm)
    """
    N_real, mu_real = theta

    # Zaokraglij N do int i przytnij do zakresu
    N = int(round(N_real))
    N = max(params['N_min'], min(params['N_max'], N))

    # Przytnij mu do zakresu
    mu = max(params['mu_min'], min(params['mu_max'], mu_real))

    # Oblicz charakterystyki MVA
    R, X, L = mva(N, mu, params['Z'])

    # Oblicz wartosc funkcji celu
    if objective == ObjectiveType.THROUGHPUT:
        # f1(N, mu) = X(N, mu) - maksymalizacja
        return X

    elif objective == ObjectiveType.RESPONSE_TIME:
        # f2(N, mu) = -R(N, mu) - minimalizacja R = maksymalizacja -R
        return -R

    elif objective == ObjectiveType.PROFIT:
        # f3(N, mu) = r*X - C_s*mu - C_N*N
        r = params.get('r', 10.0)
        C_s = params.get('C_s', 1.0)
        C_N = params.get('C_N', 0.5)
        profit = r * X - C_s * mu - C_N * N
        return profit

    else:
        raise ValueError(f"Nieznany typ funkcji celu: {objective}")


def firefly_optimize(
    params: Dict[str, Any],
    objective: ObjectiveType,
    n_fireflies: int = 25,
    n_iterations: int = 100,
    alpha: float = 0.5,
    beta_0: float = 1.0,
    gamma: float = 1.0,
    verbose: bool = True
) -> Tuple[Tuple[int, float], float, List[float]]:
    """
    Algorytm Firefly do maksymalizacji funkcji celu.

    Parametry algorytmu:
    - n_fireflies: liczba swietlikow (rozmiar populacji)
    - n_iterations: liczba iteracji
    - alpha: parametr losowosci (eksploracja)
    - beta_0: atrakcyjnosc bazowa
    - gamma: wspolczynnik absorpcji swiatla

    Args:
        params: Parametry modelu i zakresow
        objective: Typ funkcji celu
        n_fireflies: Liczba swietlikow
        n_iterations: Liczba iteracji
        alpha: Parametr losowosci
        beta_0: Atrakcyjnosc bazowa
        gamma: Wspolczynnik absorpcji
        verbose: Czy wyswietlac postep

    Returns:
        Tuple:
        - best_solution: (N_best, mu_best)
        - best_value: Najlepsza wartosc funkcji celu
        - history: Historia najlepszych wartosci
    """
    # Zakresy zmiennych decyzyjnych
    N_min, N_max = params['N_min'], params['N_max']
    mu_min, mu_max = params['mu_min'], params['mu_max']

    # Inicjalizacja populacji swietlikow
    fireflies = []
    for _ in range(n_fireflies):
        N = random.uniform(N_min, N_max)
        mu = random.uniform(mu_min, mu_max)
        fireflies.append([N, mu])

    # Oblicz jasnosc (wartosc funkcji celu) dla kazdego swietlika
    intensities = [evaluate(tuple(f), params, objective) for f in fireflies]

    # Znajdz najlepszego
    best_idx = intensities.index(max(intensities))
    best_solution = fireflies[best_idx][:]
    best_value = intensities[best_idx]

    # Historia do wykresu
    history = [best_value]

    if verbose:
        print("=" * 70)
        print("FIREFLY ALGORITHM - START OPTYMALIZACJI")
        print("=" * 70)
        print(f"Liczba swietlikow: {n_fireflies}")
        print(f"Liczba iteracji: {n_iterations}")
        print(f"Parametry: alpha={alpha}, beta_0={beta_0}, gamma={gamma}")
        print(f"Funkcja celu: {objective.value}")
        print("=" * 70)

    # Glowna petla optymalizacji
    for iteration in range(n_iterations):
        # Dla kazdego swietlika i
        for i in range(n_fireflies):
            # Porownaj z kazdym innym swietlikiem j
            for j in range(n_fireflies):
                # Jesli swietlik j jest jasniejszy (lepsza wartosc)
                if intensities[j] > intensities[i]:
                    # Oblicz odleglosc euklidesowa
                    r = math.sqrt(
                        (fireflies[i][0] - fireflies[j][0]) ** 2 +
                        (fireflies[i][1] - fireflies[j][1]) ** 2
                    )

                    # Oblicz atrakcyjnosc: beta = beta_0 * exp(-gamma * r^2)
                    beta = beta_0 * math.exp(-gamma * r * r)

                    # Przesun swietlika i w strone j
                    for d in range(2):
                        # Skladnik przyciagania + losowy krok
                        attraction = beta * (fireflies[j][d] - fireflies[i][d])
                        random_step = alpha * (random.random() - 0.5)
                        fireflies[i][d] += attraction + random_step

                    # Przytnij do zakresow
                    fireflies[i][0] = max(N_min, min(N_max, fireflies[i][0]))
                    fireflies[i][1] = max(mu_min, min(mu_max, fireflies[i][1]))

        # Przesun najlepszego swietlika losowo (eksploracja)
        best_idx = intensities.index(max(intensities))
        for d in range(2):
            fireflies[best_idx][d] += alpha * (random.random() - 0.5)
        fireflies[best_idx][0] = max(N_min, min(N_max, fireflies[best_idx][0]))
        fireflies[best_idx][1] = max(mu_min, min(mu_max, fireflies[best_idx][1]))

        # Przelicz jasnosci
        intensities = [evaluate(tuple(f), params, objective) for f in fireflies]

        # Aktualizuj najlepsze rozwiazanie
        current_best_idx = intensities.index(max(intensities))
        current_best_value = intensities[current_best_idx]

        if current_best_value > best_value:
            best_value = current_best_value
            best_solution = fireflies[current_best_idx][:]

        history.append(best_value)

        # Wyswietl postep
        if verbose and (iteration + 1) % 10 == 0:
            N_display = int(round(best_solution[0]))
            print(f"Iteracja {iteration + 1}/{n_iterations}: "
                  f"Najlepsza wartosc = {best_value:.6f}, "
                  f"N = {N_display}, mu = {best_solution[1]:.4f}")

    # Koncowe zaokraglenie N
    N_best = int(round(best_solution[0]))
    N_best = max(params['N_min'], min(params['N_max'], N_best))
    mu_best = max(params['mu_min'], min(params['mu_max'], best_solution[1]))

    if verbose:
        print("=" * 70)
        print("OPTYMALIZACJA ZAKONCZONA")
        print("=" * 70)

    return ((N_best, mu_best), best_value, history)


def generate_random_start(params: Dict[str, Any]) -> Tuple[int, float]:
    """
    Generuje losowe rozwiazanie startowe.

    Args:
        params: Parametry z zakresami N i mu

    Returns:
        Tuple (N_start, mu_start)
    """
    N = random.randint(params['N_min'], params['N_max'])
    mu = random.uniform(params['mu_min'], params['mu_max'])
    return (N, mu)


def print_report(
    params: Dict[str, Any],
    objective: ObjectiveType,
    start_solution: Tuple[int, float],
    best_solution: Tuple[int, float],
    firefly_params: Dict[str, Any]
) -> None:
    """
    Wypisuje raport porownawczy w formie tabeli.

    Args:
        params: Parametry modelu
        objective: Typ funkcji celu
        start_solution: (N_start, mu_start)
        best_solution: (N_best, mu_best)
        firefly_params: Parametry algorytmu
    """
    N_start, mu_start = start_solution
    N_best, mu_best = best_solution

    # Oblicz charakterystyki dla obu rozwiazan
    R_start, X_start, L_start = mva(N_start, mu_start, params['Z'])
    R_best, X_best, L_best = mva(N_best, mu_best, params['Z'])

    # Oblicz wartosci funkcji celu
    f_start = evaluate((N_start, mu_start), params, objective)
    f_best = evaluate((N_best, mu_best), params, objective)

    # Oblicz koszty (dla PROFIT)
    r = params.get('r', 10.0)
    C_s = params.get('C_s', 1.0)
    C_N = params.get('C_N', 0.5)

    cost_start = C_s * mu_start + C_N * N_start
    cost_best = C_s * mu_best + C_N * N_best

    revenue_start = r * X_start
    revenue_best = r * X_best

    # Wyswietl raport
    print("\n" + "=" * 80)
    print("RAPORT OPTYMALIZACJI ZAMKNIETEGO SYSTEMU KOLEJKOWEGO")
    print("=" * 80)

    print("\n--- PARAMETRY MODELU ---")
    print(f"Z (sredni czas myslenia): {params['Z']} s")
    print(f"Zakres N: [{params['N_min']}, {params['N_max']}]")
    print(f"Zakres mu: [{params['mu_min']}, {params['mu_max']}]")

    if objective == ObjectiveType.PROFIT:
        print(f"r (zysk/zadanie): {r}")
        print(f"C_s (koszt mocy serwera): {C_s}")
        print(f"C_N (koszt zadania): {C_N}")

    print(f"\nFunkcja celu: {objective.value}")

    print("\n--- PARAMETRY ALGORYTMU FIREFLY ---")
    print(f"Liczba swietlikow: {firefly_params.get('n_fireflies', 25)}")
    print(f"Liczba iteracji: {firefly_params.get('n_iterations', 100)}")
    print(f"Alpha (losowosc): {firefly_params.get('alpha', 0.5)}")
    print(f"Beta_0 (atrakcyjnosc): {firefly_params.get('beta_0', 1.0)}")
    print(f"Gamma (absorpcja): {firefly_params.get('gamma', 1.0)}")

    print("\n--- POROWNANIE WYNIKOW ---")
    print("-" * 80)
    print(f"{'Parametr':<25} {'Przed optymalizacja':>20} {'Po optymalizacji':>20} {'Zmiana':>12}")
    print("-" * 80)

    # Zmienne decyzyjne
    print(f"{'N (liczba uzytkownikow)':<25} {N_start:>20} {N_best:>20} {N_best - N_start:>+12}")
    print(f"{'mu (szybkosc obslugi)':<25} {mu_start:>20.4f} {mu_best:>20.4f} {mu_best - mu_start:>+12.4f}")
    print(f"{'S (czas obslugi)':<25} {1/mu_start:>20.4f} {1/mu_best:>20.4f} {1/mu_best - 1/mu_start:>+12.4f}")

    print("-" * 80)

    # Charakterystyki systemu
    print(f"{'R (czas odpowiedzi)':<25} {R_start:>20.4f} {R_best:>20.4f} {R_best - R_start:>+12.4f}")
    print(f"{'X (przepustowosc)':<25} {X_start:>20.4f} {X_best:>20.4f} {X_best - X_start:>+12.4f}")
    print(f"{'L (dlugosc kolejki)':<25} {L_start:>20.4f} {L_best:>20.4f} {L_best - L_start:>+12.4f}")

    print("-" * 80)

    # Funkcja celu
    print(f"{'Wartosc f. celu':<25} {f_start:>20.6f} {f_best:>20.6f} {f_best - f_start:>+12.6f}")

    # Poprawa procentowa
    if f_start != 0:
        if objective == ObjectiveType.RESPONSE_TIME:
            # Dla czasu odpowiedzi mniejsza wartosc jest lepsza
            improvement = ((-f_best) - (-f_start)) / (-f_start) * 100 if f_start != 0 else 0
            improvement = -improvement  # odwracamy znak
        else:
            improvement = (f_best - f_start) / abs(f_start) * 100
        print(f"{'Poprawa procentowa':<25} {'':>20} {'':>20} {improvement:>+11.2f}%")

    print("-" * 80)

    # Analiza kosztow
    print("\n--- ANALIZA KOSZTOW ---")
    print("-" * 80)
    print(f"{'Skladnik':<25} {'Przed optymalizacja':>20} {'Po optymalizacji':>20} {'Zmiana':>12}")
    print("-" * 80)
    print(f"{'Koszt serwera (C_s*mu)':<25} {C_s * mu_start:>20.4f} {C_s * mu_best:>20.4f} {C_s * (mu_best - mu_start):>+12.4f}")
    print(f"{'Koszt zadan (C_N*N)':<25} {C_N * N_start:>20.4f} {C_N * N_best:>20.4f} {C_N * (N_best - N_start):>+12.4f}")
    print(f"{'Koszt calkowity':<25} {cost_start:>20.4f} {cost_best:>20.4f} {cost_best - cost_start:>+12.4f}")
    print("-" * 80)
    print(f"{'Przychod (r*X)':<25} {revenue_start:>20.4f} {revenue_best:>20.4f} {revenue_best - revenue_start:>+12.4f}")
    print(f"{'Zysk (przychod-koszt)':<25} {revenue_start - cost_start:>20.4f} {revenue_best - cost_best:>20.4f} {(revenue_best - cost_best) - (revenue_start - cost_start):>+12.4f}")
    print("-" * 80)

    # Wnioski
    print("\n--- WNIOSKI ---")
    if objective == ObjectiveType.THROUGHPUT:
        delta_X = X_best - X_start
        if delta_X > 0:
            print(f"Przepustowosc wzrosla o {delta_X:.4f} zadan/s ({delta_X/X_start*100:.2f}%)")
        else:
            print(f"Przepustowosc nie ulegla poprawie.")

    elif objective == ObjectiveType.RESPONSE_TIME:
        delta_R = R_start - R_best
        if delta_R > 0:
            print(f"Czas odpowiedzi zmniejszyl sie o {delta_R:.4f} s ({delta_R/R_start*100:.2f}%)")
        else:
            print(f"Czas odpowiedzi nie ulegl poprawie.")

    elif objective == ObjectiveType.PROFIT:
        delta_profit = f_best - f_start
        if delta_profit > 0:
            print(f"Zysk wzrosl o {delta_profit:.4f}")
        else:
            print(f"Zysk nie ulegl poprawie.")

    print(f"\nInwestycja w serwer (delta C_s*mu): {C_s * (mu_best - mu_start):+.4f}")
    print(f"Zmiana kosztu zadan (delta C_N*N): {C_N * (N_best - N_start):+.4f}")
    print(f"Dodatkowy przychod: {revenue_best - revenue_start:+.4f}")

    print("\n" + "=" * 80)


def save_history_to_csv(history: List[float], filename: str = "optimization_history.csv") -> None:
    """
    Zapisuje historie optymalizacji do pliku CSV.

    Args:
        history: Lista wartosci funkcji celu w kolejnych iteracjach
        filename: Nazwa pliku wyjsciowego
    """
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['iteration', 'best_value'])
        for i, value in enumerate(history):
            writer.writerow([i, value])
    print(f"\nHistoria zapisana do: {filename}")


def load_config_from_json(filename: str) -> Dict[str, Any]:
    """
    Wczytuje konfiguracje z pliku JSON.

    Args:
        filename: Sciezka do pliku JSON

    Returns:
        Slownik z konfiguracja
    """
    with open(filename, 'r') as f:
        return json.load(f)


def main():
    """Glowna funkcja programu."""

    # Parser argumentow
    parser = argparse.ArgumentParser(
        description='Optymalizacja zamknietego systemu kolejkowego algorytmem Firefly'
    )
    parser.add_argument('--config', type=str, help='Sciezka do pliku konfiguracyjnego JSON')
    parser.add_argument('--objective', type=str,
                       choices=['THROUGHPUT', 'RESPONSE_TIME', 'PROFIT'],
                       default='THROUGHPUT',
                       help='Funkcja celu')
    parser.add_argument('--no-verbose', action='store_true', help='Wylacz wyswietlanie postepu')
    parser.add_argument('--save-history', type=str, help='Zapisz historie do pliku CSV')

    args = parser.parse_args()

    # Domyslna konfiguracja
    if args.config:
        config = load_config_from_json(args.config)
    else:
        config = {
            # Parametry modelu
            'Z': 5.0,           # Sredni czas myslenia [s]
            'N_min': 1,         # Minimalna liczba uzytkownikow
            'N_max': 50,        # Maksymalna liczba uzytkownikow
            'mu_min': 0.1,      # Minimalna szybkosc obslugi
            'mu_max': 10.0,     # Maksymalna szybkosc obslugi

            # Parametry ekonomiczne (dla PROFIT)
            'r': 10.0,          # Zysk z obslugi jednego zadania
            'C_s': 1.0,         # Koszt jednostkowy mocy serwera
            'C_N': 0.5,         # Koszt jednego zadania w systemie

            # Parametry algorytmu Firefly
            'firefly': {
                'n_fireflies': 25,
                'n_iterations': 100,
                'alpha': 0.5,
                'beta_0': 1.0,
                'gamma': 1.0
            }
        }

    # Pobierz parametry
    params = {
        'Z': config['Z'],
        'N_min': config['N_min'],
        'N_max': config['N_max'],
        'mu_min': config['mu_min'],
        'mu_max': config['mu_max'],
        'r': config.get('r', 10.0),
        'C_s': config.get('C_s', 1.0),
        'C_N': config.get('C_N', 0.5)
    }

    firefly_params = config.get('firefly', {
        'n_fireflies': 25,
        'n_iterations': 100,
        'alpha': 0.5,
        'beta_0': 1.0,
        'gamma': 1.0
    })

    # Wybierz funkcje celu
    objective = ObjectiveType(args.objective)

    # Wygeneruj losowe rozwiazanie startowe
    start_solution = generate_random_start(params)
    N_start, mu_start = start_solution

    # Oblicz charakterystyki startowe
    R_start, X_start, L_start = mva(N_start, mu_start, params['Z'])
    f_start = evaluate(start_solution, params, objective)

    print("\n" + "=" * 70)
    print("ROZWIAZANIE STARTOWE (losowe)")
    print("=" * 70)
    print(f"N = {N_start}, mu = {mu_start:.4f}")
    print(f"R = {R_start:.4f} s, X = {X_start:.4f} zadan/s, L = {L_start:.4f}")
    print(f"Wartosc funkcji celu ({objective.value}): {f_start:.6f}")
    print("=" * 70)

    # Uruchom optymalizacje Firefly
    verbose = not args.no_verbose
    best_solution, best_value, history = firefly_optimize(
        params=params,
        objective=objective,
        n_fireflies=firefly_params.get('n_fireflies', 25),
        n_iterations=firefly_params.get('n_iterations', 100),
        alpha=firefly_params.get('alpha', 0.5),
        beta_0=firefly_params.get('beta_0', 1.0),
        gamma=firefly_params.get('gamma', 1.0),
        verbose=verbose
    )

    # Wyswietl raport
    print_report(params, objective, start_solution, best_solution, firefly_params)

    # Zapisz historie
    if args.save_history:
        save_history_to_csv(history, args.save_history)
    else:
        save_history_to_csv(history)

    return best_solution, best_value, history


if __name__ == '__main__':
    main()
