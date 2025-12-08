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
from models.objective_functions import (
    get_objective_function,
    OBJECTIVE_CATALOG,
    ObjectiveFunctions,
)
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
        customer_bounds: Optional[Tuple[int, int]] = None,
        service_rate_bounds: Optional[Tuple[float, float]] = None,
        cost_params: Optional[Dict[str, float]] = None,
        weights_params: Optional[Dict[str, float]] = None,
        multi_objective_weights: Optional[Dict[str, float]] = None,
        firefly_params: Optional[Dict[str, Any]] = None,
        erlang_cost_params: Optional[Dict[str, float]] = None,
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
                      - 'profit': maksymalizuj zysk ekonomiczny
                      - 'weighted_objective': kompromis wielokryterialny
                      - 'generic_weighted_objective': wielokryterialna generyczna
                      - 'erlang_cost_4_208': koszt wg wzoru Erlang 4-208 (minimalizacja)
            optimize_vars: Lista zmiennych do optymalizacji
                          Opcje:
                          - 'num_servers': liczba serwerów na każdej stacji
                          - 'service_rates': szybkość obsługi
                          - 'num_customers': liczba klientów w systemie
            server_bounds: Zakres liczby serwerów (min, max)
                          np. (1, 10) = od 1 do 10 serwerów
            customer_bounds: Zakres liczby klientów (min, max)
                            np. (1, 100) = od 1 do 100 klientów
            service_rate_bounds: Zakres szybkości obsługi (min, max)
                                np. (0.1, 10.0)
            cost_params: Parametry kosztów dla funkcji profit
                        {'r': 10.0, 'C_s': 1.0, 'C_N': 0.5}
            weights_params: Parametry wag dla funkcji weighted_objective
                           {'w1': 0.33, 'w2': 0.34, 'w3': 0.33}
            multi_objective_weights: Wagi dla generic_weighted_objective
            firefly_params: Parametry algorytmu Firefly
                           np. {'n_fireflies': 30, 'max_iterations': 150}
            erlang_cost_params: Parametry kosztu dla funkcji 'erlang_cost_4_208'
                               {'c1': ..., 'c2': ...}
        """
        self.base_network = network
        self.objective_name = objective
        self.optimize_vars = optimize_vars
        self.server_bounds = server_bounds
        self.customer_bounds = customer_bounds if customer_bounds else (1, 100)
        self.service_rate_bounds = service_rate_bounds
        self.cost_params = cost_params if cost_params else {'r': 10.0, 'C_s': 1.0, 'C_N': 0.5}
        self.weights_params = weights_params if weights_params else {'w1': 0.33, 'w2': 0.34, 'w3': 0.33}
        self.multi_objective_weights = multi_objective_weights if multi_objective_weights else {}
        self.erlang_cost_params = erlang_cost_params if erlang_cost_params else {'c1': 1.0, 'c2': 1.0}

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

        # Pobierz funkcję celu (bazową)
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
        """
        self.bounds = []
        self.integer_vars = []
        self.var_map = []  # Mapowanie: index → (zmienna, stacja)

        idx = 0

        if 'num_customers' in self.optimize_vars:
            self.bounds.append(self.customer_bounds)
            self.integer_vars.append(idx)
            self.var_map.append(('num_customers', None))
            idx += 1

        if 'num_servers' in self.optimize_vars:
            for i in range(self.base_network.K):
                self.bounds.append(self.server_bounds)
                self.integer_vars.append(idx)
                self.var_map.append(('num_servers', i))
                idx += 1

        if 'service_rates' in self.optimize_vars:
            for i in range(self.base_network.K):
                if self.service_rate_bounds:
                    self.bounds.append(self.service_rate_bounds)
                else:
                    base_rate = self.base_network.mu[i]
                    self.bounds.append((0.5 * base_rate, 2.0 * base_rate))
                self.var_map.append(('service_rates', i))
                idx += 1

    def _vector_to_network(self, vector: np.ndarray) -> QueueingNetwork:
        """
        Przekształć wektor rozwiązania na sieć kolejkową.
        """
        network = copy.deepcopy(self.base_network)
        updates = {}

        for idx, (var_type, station_idx) in enumerate(self.var_map):
            if var_type == 'num_customers':
                network.N = int(vector[idx])

            elif var_type == 'num_servers':
                if 'num_servers' not in updates:
                    updates['num_servers'] = network.m.copy()
                updates['num_servers'][station_idx] = int(vector[idx])

            elif var_type == 'service_rates':
                if 'service_rates' not in updates:
                    updates['service_rates'] = network.mu.copy()
                updates['service_rates'][station_idx] = float(vector[idx])

        if updates:
            network.update_parameters(**updates)

        return network

    def _objective_wrapper(self, vector: np.ndarray) -> float:
        """
        Wrapper funkcji celu dla algorytmu Firefly.

        1. wektor → sieć kolejkowa
        2. MVA → metryki
        3. funkcja celu → wartość do minimalizacji
        """
        try:
            network = self._vector_to_network(vector)
            solver = MVASolver(network)
            metrics = solver.solve()

            # Specjalne przypadki funkcji celu
            if self.objective_name == 'profit':
                objective_value = ObjectiveFunctions.profit(metrics, self.cost_params)

            elif self.objective_name == 'weighted_objective':
                objective_value = ObjectiveFunctions.weighted_objective(metrics, self.weights_params)

            elif self.objective_name == 'generic_weighted_objective':
                objective_value = ObjectiveFunctions.weighted_multi_objective(
                    metrics, self.multi_objective_weights
                )

            elif self.objective_name == 'erlang_cost_4_208':
                # Koszt wg wzoru 4-208 – wykorzystuje erlang_cost_params (c1, c2)
                objective_value = ObjectiveFunctions.erlang_cost_function(
                    metrics, self.erlang_cost_params
                )

            else:
                objective_value = self.objective_function_raw(metrics)

            return objective_value

        except Exception as e:
            print(f"Błąd w ocenie rozwiązania: {e}")
            return 1e10

    def optimize(self, verbose: bool = True) -> Dict[str, Any]:
        """
        URUCHOM OPTYMALIZACJĘ!

        GŁÓWNA FUNKCJA do wywołania przez użytkownika.
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

        # ------------------------------------------------------------------
        # KROK 1: baseline (przed optymalizacją)
        # ------------------------------------------------------------------
        if verbose:
            print("\n[KROK 1] Analiza sieci PRZED optymalizacja...")

        baseline_solver = MVASolver(self.base_network)
        baseline_metrics = baseline_solver.solve()

        if self.objective_name == 'profit':
            baseline_objective = ObjectiveFunctions.profit(
                baseline_metrics, self.cost_params
            )
        elif self.objective_name == 'weighted_objective':
            baseline_objective = ObjectiveFunctions.weighted_objective(
                baseline_metrics, self.weights_params
            )
        elif self.objective_name == 'generic_weighted_objective':
            baseline_objective = ObjectiveFunctions.weighted_multi_objective(
                baseline_metrics, self.multi_objective_weights
            )
        elif self.objective_name == 'erlang_cost_4_208':
            baseline_objective = ObjectiveFunctions.erlang_cost_function(
                baseline_metrics, self.erlang_cost_params
            )
        else:
            baseline_objective = self.objective_function_raw(baseline_metrics)

        if verbose:
            print(f"   Wartość funkcji celu (PRZED): {baseline_objective:.4f}")
            print(f"   Średni czas odpowiedzi: {baseline_metrics['mean_response_time']:.4f} s")
            print(f"   Średnia długość kolejki: {baseline_metrics['mean_queue_length']:.2f}")
            print(f"   Przepustowość: {baseline_metrics['throughput']:.4f} zadań/s")

        # ------------------------------------------------------------------
        # KROK 2: Firefly
        # ------------------------------------------------------------------
        if verbose:
            print(f"\n[KROK 2] Uruchamiam Firefly Algorithm...")

        firefly = FireflyAlgorithm(
            objective_function=self._objective_wrapper,
            bounds=self.bounds,
            integer_vars=self.integer_vars,
            verbose=verbose,
            **self.firefly_params
        )

        best_vector, best_value, history = firefly.optimize()

        # ------------------------------------------------------------------
        # KROK 3: ocena najlepszego rozwiązania
        # ------------------------------------------------------------------
        if verbose:
            print(f"\n[KROK 3] Analiza sieci PO optymalizacji...")

        optimized_network = self._vector_to_network(best_vector)
        optimized_solver = MVASolver(optimized_network)
        optimized_metrics = optimized_solver.solve()

        if verbose:
            print(f"   Wartość funkcji celu (PO): {best_value:.4f}")
            print(f"   Średni czas odpowiedzi: {optimized_metrics['mean_response_time']:.4f} s")
            print(f"   Średnia długość kolejki: {optimized_metrics['mean_queue_length']:.2f}")
            print(f"   Przepustowość: {optimized_metrics['throughput']:.4f} zadań/s")

        # KROK 3.5: koszt w serwerach
        baseline_servers = baseline_metrics.get('total_servers', 0)
        optimized_servers = optimized_metrics.get('total_servers', 0)
        added_servers = max(0, optimized_servers - baseline_servers)

        # ------------------------------------------------------------------
        # Oblicz improvement_percent
        # ------------------------------------------------------------------
        if abs(baseline_objective) > 0:
            if self.objective_name in ('profit', 'throughput', 'weighted_objective'):
                real_baseline = -baseline_objective
                real_best = -best_value
                improvement_percent = (
                    (real_best - real_baseline) / abs(real_baseline) * 100
                    if real_baseline != 0
                    else 0.0
                )
            else:
                improvement_percent = (
                    (baseline_objective - best_value) / abs(baseline_objective) * 100
                )
        else:
            improvement_percent = 0.0

        cost = None

        # Dla funkcji wykorzystujących dodane serwery jako "koszt inwestycji"
        if self.objective_name in (
            'mean_queue_length',
            'max_queue_length',
            'response_time_percentile',
            'utilization_variance',
            'weighted_objective',
            'mean_response_time',
            'throughput',
            'erlang_cost_4_208',
        ):
            if self.objective_name in ('throughput', 'weighted_objective'):
                improvement_value = float(-best_value - (-baseline_objective))
            else:
                improvement_value = float(baseline_objective - best_value)

            cost = {
                'type': 'added_servers',
                'description': 'Liczba dodanych serwerow (inwestycja)',
                'baseline_servers': int(baseline_servers),
                'optimized_servers': int(optimized_servers),
                'added_servers': int(added_servers),
                'improvement_value': improvement_value,
                'improvement_percent': float(improvement_percent),
            }

        elif self.objective_name == 'profit':
            r = self.cost_params['r']
            C_s = self.cost_params['C_s']
            C_N = self.cost_params['C_N']

            X_before = baseline_metrics['throughput']
            mu_before = baseline_metrics.get('total_service_rate', 0)
            N = baseline_metrics.get('num_customers', 0)

            revenue_before = r * X_before
            cost_servers_before = C_s * mu_before
            cost_customers_before = C_N * N
            profit_before = revenue_before - cost_servers_before - cost_customers_before

            X_after = optimized_metrics['throughput']
            mu_after = optimized_metrics.get('total_service_rate', 0)

            revenue_after = r * X_after
            cost_servers_after = C_s * mu_after
            cost_customers_after = C_N * N
            profit_after = revenue_after - cost_servers_after - cost_customers_after

            delta_cost_servers = cost_servers_after - cost_servers_before
            delta_cost_customers = cost_customers_after - cost_customers_before
            total_investment = delta_cost_servers + delta_cost_customers
            profit_gain = profit_after - profit_before

            cost = {
                'type': 'profit_breakdown',
                'description': 'Analiza ekonomiczna optymalizacji',
                'baseline': {
                    'revenue': float(revenue_before),
                    'cost_servers': float(cost_servers_before),
                    'cost_customers': float(cost_customers_before),
                    'profit': float(profit_before),
                },
                'optimized': {
                    'revenue': float(revenue_after),
                    'cost_servers': float(cost_servers_after),
                    'cost_customers': float(cost_customers_after),
                    'profit': float(profit_after),
                },
                'delta': {
                    'investment': float(total_investment),
                    'profit_gain': float(profit_gain),
                    'roi_percent': float(
                        (profit_gain / total_investment * 100)
                        if total_investment > 0
                        else 0
                    ),
                },
                'added_servers': int(added_servers),
            }

        if verbose:
            print("\n" + "=" * 70)
            print("OPTYMALIZACJA ZAKONCZONA")
            print("=" * 70)
            print(f"Poprawa: {improvement_percent:.2f}%")
            print("=" * 70)

        return {
            'baseline': {
                'network': self.base_network.get_configuration(),
                'metrics': baseline_metrics,
                'objective_value': baseline_objective,
            },
            'optimized': {
                'network': optimized_network.get_configuration(),
                'metrics': optimized_metrics,
                'objective_value': best_value,
                'solution_vector': best_vector.tolist(),
            },
            'improvement': {
                'absolute': float(
                    -best_value - (-baseline_objective)
                )
                if self.objective_name in ('profit', 'throughput', 'weighted_objective')
                else float(baseline_objective - best_value),
                'percent': improvement_percent,
            },
            'optimization_info': {
                'objective_name': self.objective_name,
                'objective_description': OBJECTIVE_CATALOG[self.objective_name]['description'],
                'optimized_variables': self.optimize_vars,
                'firefly_params': self.firefly_params,
            },
            'cost': cost,
            'history': history,
        }
