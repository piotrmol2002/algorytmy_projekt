"""
====================================================================
MVA SOLVER - Mean Value Analysis
====================================================================

CO TO JEST MVA?
---------------
Mean Value Analysis to MATEMATYCZNA METODA do obliczania charakterystyk
sieci kolejkowej bez potrzeby symulacji!

Zamiast symulować miliony zdarzeń, MVA używa równań matematycznych
do DOKŁADNEGO obliczenia:
- Średniego czasu oczekiwania
- Długości kolejek
- Wykorzystania serwerów
- Przepustowości

JAK TO DZIAŁA?
--------------
MVA opiera się na prostej obserwacji:
"Klient wchodzący do stacji widzi średnią kolejkę z poprzedniej iteracji"

ALGORYTM (uproszczone kroki):
------------------------------
1. Zacznij z N=0 klientów (pusta sieć)
2. Dodawaj klientów po kolei (N=1, 2, 3, ..., N)
3. Dla każdego N oblicz:
   - Średni czas obsługi
   - Długość kolejki
   - Wykorzystanie serwerów
4. Po N iteracjach masz DOKŁADNE wyniki!

ZALETY:
-------
- Szybkie (nie trzeba symulować)
- Dokładne (matematycznie ścisłe)
- Sprawdza się dla sieci zamkniętych

====================================================================
"""

import numpy as np
from typing import Dict, Any, List
from models.queueing_network import QueueingNetwork


class MVASolver:
    """
    Solver Mean Value Analysis dla zamkniętych sieci kolejkowych.

    ZASTOSOWANIE:
    -------------
    solver = MVASolver(network)
    metrics = solver.solve()
    print(f"Średni czas odpowiedzi: {metrics['mean_response_time']}")
    """

    def __init__(self, network: QueueingNetwork):
        """
        Inicjalizacja solvera.

        Args:
            network: Obiekt QueueingNetwork do analizy
        """
        self.network = network

    def solve(self) -> Dict[str, Any]:
        """
        Rozwiązuje sieć kolejkową metodą MVA.

        WYNIK:
        ------
        Zwraca słownik z wszystkimi metrykami:
        - mean_response_time: Średni czas odpowiedzi w systemie
        - mean_queue_length: Średnia długość kolejki
        - queue_lengths: Długości kolejek na każdej stacji [Q₁, Q₂, ..., Qₖ]
        - response_times: Czasy odpowiedzi dla każdej stacji [R₁, R₂, ..., Rₖ]
        - utilizations: Wykorzystanie serwerów na każdej stacji [ρ₁, ρ₂, ..., ρₖ]
        - throughput: Przepustowość systemu (zadania/s)
        - total_servers: Łączna liczba serwerów

        Returns:
            Słownik z metrykami wydajności
        """
        K = self.network.K  # Liczba stacji
        N = self.network.N  # Liczba klientów
        mu = self.network.mu  # Service rates
        m = self.network.m  # Liczba serwerów
        e = self.network.e  # Visit ratios

        # Inicjalizacja
        # Q[n][i] = średnia długość kolejki na stacji i przy n klientach
        Q = np.zeros((N + 1, K))

        # R[n][i] = średni czas odpowiedzi na stacji i przy n klientach
        R = np.zeros((N + 1, K))

        # ALGORYTM MVA - iteracja po liczbie klientów
        for n in range(1, N + 1):
            # KROK 1: Oblicz czasy odpowiedzi dla każdej stacji
            for i in range(K):
                # Średni czas obsługi na stacji i
                service_time = 1.0 / mu[i]

                # Oczekiwany czas oczekiwania = czas obsługi × (1 + średnia kolejka)
                # (klient widzi średnią kolejkę z poprzedniej iteracji n-1)
                if m[i] == 1:
                    # Jedna kolejka (M/M/1)
                    R[n, i] = service_time * (1 + Q[n-1, i])
                else:
                    # Wiele serwerów (M/M/m) - przybliżenie
                    # Używamy formuły dla systemu M/M/m
                    avg_service_rate = min(n, m[i]) * mu[i]
                    if avg_service_rate > 0:
                        R[n, i] = service_time * (1 + Q[n-1, i] / m[i])
                    else:
                        R[n, i] = service_time

            # KROK 2: Oblicz średni czas odpowiedzi w całym systemie
            mean_R = np.sum(e * R[n, :])

            # KROK 3: Oblicz przepustowość (throughput)
            # Z prawa Little'a: N = X · R  =>  X = N / R
            if mean_R > 0:
                X = n / mean_R  # System throughput
            else:
                X = 0

            # KROK 4: Oblicz długości kolejek na każdej stacji
            # Z prawa Little'a: Q_i = X_i · R_i
            # gdzie X_i = X · e_i (throughput na stacji i)
            for i in range(K):
                X_i = X * e[i]  # Throughput na stacji i
                Q[n, i] = X_i * R[n, i]

        # WYNIKI DLA PEŁNEJ LICZBY KLIENTÓW (N)
        final_R = R[N, :]  # Czasy odpowiedzi na każdej stacji
        final_Q = Q[N, :]  # Długości kolejek na każdej stacji

        # Średni czas odpowiedzi w systemie
        mean_response_time = np.sum(e * final_R)

        # Przepustowość systemu
        if mean_response_time > 0:
            throughput = N / mean_response_time
        else:
            throughput = 0

        # Średnia długość kolejki (suma na wszystkich stacjach)
        mean_queue_length = np.sum(final_Q)

        # Wykorzystanie serwerów (utilization)
        # ρ_i = X_i / (m_i · μ_i)
        utilizations = []
        for i in range(K):
            X_i = throughput * e[i]
            max_rate = m[i] * mu[i]
            if max_rate > 0:
                rho_i = X_i / max_rate
                utilizations.append(min(rho_i, 1.0))  # Utilization nie może przekroczyć 100%
            else:
                utilizations.append(0.0)

        # Zwróć wszystkie metryki
        return {
            'mean_response_time': float(mean_response_time),
            'mean_queue_length': float(mean_queue_length),
            'queue_lengths': final_Q.tolist(),
            'response_times': final_R.tolist(),
            'utilizations': utilizations,
            'throughput': float(throughput),
            'total_servers': int(np.sum(m)),
            'station_names': self.network.station_names
        }

    def solve_detailed(self) -> Dict[str, Any]:
        """
        Rozwiązuje sieć i zwraca SZCZEGÓŁOWE informacje dla każdej stacji.

        UŻYCIE:
        -------
        Kiedy chcesz zobaczyć dokładne wyniki dla każdej stacji osobno.

        Returns:
            Słownik ze szczegółowymi metrykami dla każdej stacji
        """
        metrics = self.solve()

        # Formatuj szczegółowe wyniki dla każdej stacji
        detailed = {
            'overall': {
                'mean_response_time': metrics['mean_response_time'],
                'mean_queue_length': metrics['mean_queue_length'],
                'throughput': metrics['throughput'],
                'total_servers': metrics['total_servers']
            },
            'stations': []
        }

        for i in range(self.network.K):
            station_info = {
                'name': self.network.station_names[i],
                'id': i,
                'num_servers': int(self.network.m[i]),
                'service_rate': float(self.network.mu[i]),
                'visit_ratio': float(self.network.e[i]),
                'queue_length': float(metrics['queue_lengths'][i]),
                'response_time': float(metrics['response_times'][i]),
                'utilization': float(metrics['utilizations'][i]),
                'utilization_percent': f"{metrics['utilizations'][i] * 100:.1f}%"
            }
            detailed['stations'].append(station_info)

        return detailed


def analyze_network(network: QueueingNetwork) -> Dict[str, Any]:
    """
    Funkcja pomocnicza do szybkiej analizy sieci.

    PRZYKŁAD UŻYCIA:
    ----------------
    network = QueueingNetwork(...)
    results = analyze_network(network)
    print(results)

    Args:
        network: Sieć kolejkowa do analizy

    Returns:
        Słownik z metrykami
    """
    solver = MVASolver(network)
    return solver.solve()
