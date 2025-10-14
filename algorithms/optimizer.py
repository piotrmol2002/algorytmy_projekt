"""
====================================================================
OPTIMIZER - MODUŁ ŁĄCZĄCY WSZYSTKO
====================================================================

CO ROBI TEN MODUŁ?
-------------------
Łączy:
1. Model sieci kolejkowej (QueueingNetwork)
2. Solver MVA (obliczanie metryk)
3. Funkcje celu (ObjectiveFunctions)
4. Algorytm Firefly (optymalizacja)

REZULTAT:
---------
Prosty interfejs do optymalizacji:
optimizer = QueueingOptimizer(network, objective='mean_response_time')
result = optimizer.optimize()

====================================================================
"""

import numpy as np
from typing import Dict, Any, List, Callable, Optional, Tuple
import copy

from models.queueing_network import QueueingNetwork
from models.objective_functions import get_objective_function, OBJECTIVE_CATALOG
from simulation.mva_solver import MVASolver
from algorithms.firefly import FireflyAlgorithm


class QueueingOptimizer:
    """
    Główna klasa do optymalizacji sieci kolejkowych algorytmem Firefly.

    UŻYCIE (3 KROKI):
    =================
    # 1. Stwórz sieć bazową
    network = QueueingNetwork(...)

    # 2. Stwórz optimizer
    optimizer = QueueingOptimizer(
        network=network,
        objective='mean_response_time',
        optimize_vars=['num_servers']  # Co optymalizujemy
    )

    # 3. Uruchom optymalizację
    result = optimizer.optimize()
    """

    def __init__(
        self,
        network: QueueingNetwork,
        objective: str = 'mean_response_time',
        optimize_vars: List[str] = ['num_servers'],
        server_bounds: Optional[Tuple[int, int]] = (1, 10),
        firefly_params: Optional[Dict[str, Any]] = None
    ):
        """
        Inicjalizacja optymizera.

        Args:
            network: Bazowa sieć kolejkowa
            objective: Nazwa funkcji celu (z OBJECTIVE_CATALOG)
                      Opcje:
                      - 'mean_response_time': minimalizuj średni czas odpowiedzi
                      - 'mean_queue_length': minimalizuj długość kolejek
                      - 'max_queue_length': minimalizuj najdłuższą kolejkę
                      - 'utilization_variance': minimalizuj nierównomierność obciążenia
                      - 'throughput': maksymalizuj przepustowość
            optimize_vars: Lista zmiennych do optymalizacji
                          Opcje:
                          - 'num_servers': liczba serwerów na każdej stacji
                          - 'service_rates': szybkość obsługi
                          - 'routing': macierz routingu (TODO)
            server_bounds: Zakres liczby serwerów (min, max)
                          np. (1, 10) = od 1 do 10 serwerów
            firefly_params: Parametry algorytmu Firefly
                           np. {'n_fireflies': 30, 'max_iterations': 150}
        """
        self.base_network = network
        self.objective_name = objective
        self.optimize_vars = optimize_vars
        self.server_bounds = server_bounds

        # Parametry Firefly (domyślne lub podane)
        default_params = {
            'n_fireflies': 25,
            'max_iterations': 100,
            'alpha': 0.5,
            'beta_0': 1.0,
            'gamma': 1.0
        }
        if firefly_params:
            default_params.update(firefly_params)
        self.firefly_params = default_params

        # Pobierz funkcję celu
        self.objective_function_raw = get_objective_function(objective)

        # Przygotuj bounds i integer_vars dla algorytmu
        self._prepare_optimization_space()

    def _prepare_optimization_space(self):
        """
        Przygotuj przestrzeń poszukiwań dla algorytmu Firefly.

        WYJAŚNIENIE:
        ------------
        Algorytm Firefly działa na wektorach liczb. Musimy przekształcić
        parametry sieci (np. liczba serwerów) na wektor i bounds.

        PRZYKŁAD:
        ---------
        Sieć z 3 stacjami, optymalizujemy num_servers:
        → bounds = [(1, 10), (1, 10), (1, 10)]
        → integer_vars = [0, 1, 2] (bo liczba serwerów musi być int)
        """
        self.bounds = []
        self.integer_vars = []
        self.var_map = []  # Mapowanie: index → (zmienna, stacja)

        idx = 0

        if 'num_servers' in self.optimize_vars:
            # Dla każdej stacji dodaj bounds dla liczby serwerów
            for i in range(self.base_network.K):
                self.bounds.append(self.server_bounds)
                self.integer_vars.append(idx)
                self.var_map.append(('num_servers', i))
                idx += 1

        if 'service_rates' in self.optimize_vars:
            # Dla każdej stacji dodaj bounds dla service rate
            for i in range(self.base_network.K):
                # Zakres: 50%-200% wartości bazowej
                base_rate = self.base_network.mu[i]
                self.bounds.append((0.5 * base_rate, 2.0 * base_rate))
                self.var_map.append(('service_rates', i))
                idx += 1

        # TODO: Dodaj support dla optymalizacji routingu

    def _vector_to_network(self, vector: np.ndarray) -> QueueingNetwork:
        """
        Przekształć wektor rozwiązania na sieć kolejkową.

        PRZYKŁAD:
        ---------
        vector = [4, 3, 5]  # Liczba serwerów dla 3 stacji
        → Stwórz nową sieć z tymi parametrami

        Args:
            vector: Wektor rozwiązania z algorytmu Firefly

        Returns:
            Nowa sieć kolejkowa z parametrami z wektora
        """
        # Skopiuj bazową sieć
        network = copy.deepcopy(self.base_network)

        # Zaktualizuj parametry na podstawie wektora
        updates = {}

        for idx, (var_type, station_idx) in enumerate(self.var_map):
            if var_type == 'num_servers':
                if 'num_servers' not in updates:
                    updates['num_servers'] = network.m.copy()
                updates['num_servers'][station_idx] = int(vector[idx])

            elif var_type == 'service_rates':
                if 'service_rates' not in updates:
                    updates['service_rates'] = network.mu.copy()
                updates['service_rates'][station_idx] = float(vector[idx])

        # Zastosuj aktualizacje
        network.update_parameters(**updates)

        return network

    def _objective_wrapper(self, vector: np.ndarray) -> float:
        """
        Wrapper funkcji celu dla algorytmu Firefly.

        PRZEBIEG:
        ---------
        1. Przekształć wektor → sieć kolejkowa
        2. Uruchom MVA solver → oblicz metryki
        3. Zastosuj funkcję celu → oblicz wartość do minimalizacji

        Args:
            vector: Wektor rozwiązania

        Returns:
            Wartość funkcji celu (do minimalizacji)
        """
        try:
            # 1. Stwórz sieć z parametrów
            network = self._vector_to_network(vector)

            # 2. Uruchom MVA solver
            solver = MVASolver(network)
            metrics = solver.solve()

            # 3. Oblicz wartość funkcji celu
            objective_value = self.objective_function_raw(metrics)

            return objective_value

        except Exception as e:
            # Jeśli coś pójdzie nie tak, zwróć bardzo wysoką wartość
            print(f"Błąd w ocenie rozwiązania: {e}")
            return 1e10

    def optimize(self, verbose: bool = True) -> Dict[str, Any]:
        """
        URUCHOM OPTYMALIZACJĘ!

        GŁÓWNA FUNKCJA do wywołania przez użytkownika.

        Returns:
            Słownik z wynikami:
            - 'baseline': Metryki PRZED optymalizacją
            - 'optimized': Metryki PO optymalizacji
            - 'improvement': Procentowa poprawa
            - 'best_solution': Najlepsza znaleziona konfiguracja
            - 'history': Historia optymalizacji (do wykresów)
        """
        if verbose:
            print("\n" + "=" * 70)
            print("ROZPOCZYNAM OPTYMALIZACJĘ SIECI KOLEJKOWEJ")
            print("=" * 70)
            print(f"Funkcja celu: {OBJECTIVE_CATALOG[self.objective_name]['name']}")
            print(f"Optymalizowane zmienne: {', '.join(self.optimize_vars)}")
            print(f"Liczba stacji: {self.base_network.K}")
            print(f"Liczba klientów: {self.base_network.N}")
            print("=" * 70)

        # KROK 1: Oceń sieć PRZED optymalizacją (baseline)
        if verbose:
            print("\n📊 KROK 1: Analiza sieci PRZED optymalizacją...")

        baseline_solver = MVASolver(self.base_network)
        baseline_metrics = baseline_solver.solve()
        baseline_objective = self.objective_function_raw(baseline_metrics)

        if verbose:
            print(f"   Wartość funkcji celu (PRZED): {baseline_objective:.4f}")
            print(f"   Średni czas odpowiedzi: {baseline_metrics['mean_response_time']:.4f} s")
            print(f"   Średnia długość kolejki: {baseline_metrics['mean_queue_length']:.2f}")
            print(f"   Przepustowość: {baseline_metrics['throughput']:.4f} zadań/s")

        # KROK 2: Uruchom algorytm Firefly
        if verbose:
            print(f"\n🔥 KROK 2: Uruchamiam Firefly Algorithm...")

        firefly = FireflyAlgorithm(
            objective_function=self._objective_wrapper,
            bounds=self.bounds,
            integer_vars=self.integer_vars,
            verbose=verbose,
            **self.firefly_params
        )

        best_vector, best_value, history = firefly.optimize()

        # KROK 3: Oceń najlepsze rozwiązanie
        if verbose:
            print(f"\n📊 KROK 3: Analiza sieci PO optymalizacji...")

        optimized_network = self._vector_to_network(best_vector)
        optimized_solver = MVASolver(optimized_network)
        optimized_metrics = optimized_solver.solve()

        if verbose:
            print(f"   Wartość funkcji celu (PO): {best_value:.4f}")
            print(f"   Średni czas odpowiedzi: {optimized_metrics['mean_response_time']:.4f} s")
            print(f"   Średnia długość kolejki: {optimized_metrics['mean_queue_length']:.2f}")
            print(f"   Przepustowość: {optimized_metrics['throughput']:.4f} zadań/s")

        # KROK 4: Oblicz poprawę
        improvement_percent = ((baseline_objective - best_value) / baseline_objective) * 100

        if verbose:
            print("\n" + "=" * 70)
            print("✅ OPTYMALIZACJA ZAKOŃCZONA")
            print("=" * 70)
            print(f"Poprawa: {improvement_percent:.2f}%")
            print("=" * 70)

        # Zwróć wszystkie wyniki
        return {
            'baseline': {
                'network': self.base_network.get_configuration(),
                'metrics': baseline_metrics,
                'objective_value': baseline_objective
            },
            'optimized': {
                'network': optimized_network.get_configuration(),
                'metrics': optimized_metrics,
                'objective_value': best_value,
                'solution_vector': best_vector.tolist()
            },
            'improvement': {
                'absolute': baseline_objective - best_value,
                'percent': improvement_percent
            },
            'optimization_info': {
                'objective_name': self.objective_name,
                'objective_description': OBJECTIVE_CATALOG[self.objective_name]['description'],
                'optimized_variables': self.optimize_vars,
                'firefly_params': self.firefly_params
            },
            'history': history
        }
