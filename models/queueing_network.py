"""
====================================================================
MODEL ZAMKNIĘTEJ SIECI KOLEJKOWEJ (Closed Queueing Network)
====================================================================

CO TO JEST SIEĆ KOLEJKOWA?
---------------------------
Wyobraź sobie system, gdzie "klienci" (zadania, procesy) krążą między
różnymi "stacjami obsługi" (serwery, procesory). W sieci ZAMKNIĘTEJ:
- Jest STAŁA liczba klientów (np. 10 zadań)
- Klienci nigdy nie opuszczają systemu
- Po obsłudze na jednej stacji, idą do kolejnej

PRZYKŁAD Z ŻYCIA:
-----------------
System komputerowy z 3 procesorami:
- 20 zadań krąży między procesorami
- Po zakończeniu na CPU1, zadanie idzie do CPU2 lub CPU3
- System nigdy nie ma więcej ani mniej niż 20 zadań

CO CHCEMY OPTYMALIZOWAĆ?
-------------------------
- Liczbę serwerów na każdej stacji (ile CPU przypisać?)
- Routing (jak rozdzielać zadania między stacje?)
- Service rates (jak szybko obsługiwać?)

CEL: Minimalizować czas oczekiwania lub długość kolejek
====================================================================
"""

import numpy as np
from typing import List, Dict, Any, Optional


class QueueingNetwork:
    """
    Klasa reprezentująca zamkniętą sieć kolejkową.

    PARAMETRY WEJŚCIOWE (co musisz podać):
    =======================================
    - num_stations (K): Liczba stacji obsługi (np. 3 procesory)
    - num_customers (N): Liczba klientów w systemie (np. 20 zadań)
    - service_rates: Szybkość obsługi na każdej stacji (np. [5, 3, 4] zadań/s)
    - num_servers: Liczba serwerów na każdej stacji (np. [2, 1, 3])
    - routing_matrix: Macierz prawdopodobieństw przejść między stacjami

    PRZYKŁAD:
    =========
    Sieć z 3 stacjami, 10 klientami:
    - Stacja 1: 2 serwery, obsługa 5 zadań/s
    - Stacja 2: 1 serwer, obsługa 3 zadania/s
    - Stacja 3: 3 serwery, obsługa 4 zadania/s

    network = QueueingNetwork(
        num_stations=3,
        num_customers=10,
        service_rates=[5, 3, 4],
        num_servers=[2, 1, 3]
    )
    """

    def __init__(
        self,
        num_stations: int,
        num_customers: int,
        service_rates: List[float],
        num_servers: List[int],
        routing_matrix: Optional[np.ndarray] = None,
        station_names: Optional[List[str]] = None
    ):
        """
        Inicjalizacja sieci kolejkowej.

        Args:
            num_stations: Liczba stacji w sieci (K)
            num_customers: Liczba klientów krążących w systemie (N)
            service_rates: Lista szybkości obsługi dla każdej stacji [μ₁, μ₂, ..., μₖ]
            num_servers: Lista liczb serwerów na każdej stacji [m₁, m₂, ..., mₖ]
            routing_matrix: Macierz K×K prawdopodobieństw przejść P[i][j]
                           (jeśli None, równomierne rozdzielenie)
            station_names: Opcjonalne nazwy stacji (dla łatwiejszego czytania)
        """
        # Walidacja danych wejściowych
        assert num_stations > 0, "Liczba stacji musi być > 0"
        assert num_customers > 0, "Liczba klientów musi być > 0"
        assert len(service_rates) == num_stations, "Długość service_rates musi równać się liczbie stacji"
        assert len(num_servers) == num_stations, "Długość num_servers musi równać się liczbie stacji"

        self.K = num_stations          # Liczba stacji
        self.N = num_customers         # Liczba klientów
        self.mu = np.array(service_rates)  # Szybkość obsługi
        self.m = np.array(num_servers, dtype=int)  # Liczba serwerów

        # Nazwy stacji (jeśli nie podano, użyj "Stacja 1", "Stacja 2", etc.)
        if station_names is None:
            self.station_names = [f"Stacja {i+1}" for i in range(num_stations)]
        else:
            assert len(station_names) == num_stations
            self.station_names = station_names

        # Macierz routingu (jeśli nie podano, równomierne rozdzielenie)
        if routing_matrix is None:
            # Domyślnie: każda stacja wysyła równomiernie do wszystkich innych
            self.P = np.ones((num_stations, num_stations)) / num_stations
        else:
            assert routing_matrix.shape == (num_stations, num_stations)
            # Sprawdź czy wiersze sumują się do 1 (prawdopodobieństwa)
            assert np.allclose(routing_matrix.sum(axis=1), 1.0), \
                "Każdy wiersz macierzy routingu musi sumować się do 1.0"
            self.P = routing_matrix

        # Oblicz visit ratios (względne częstości odwiedzin stacji)
        self._compute_visit_ratios()

    def _compute_visit_ratios(self):
        """
        Oblicza visit ratios (e_i) - jak często odwiedzamy każdą stację.

        WYJAŚNIENIE:
        ------------
        Visit ratio mówi, ile razy przeciętnie klient odwiedzi daną stację
        podczas jednego "obiegu" przez system.

        MATEMATYKA:
        -----------
        Rozwiązujemy układ równań: e = e·P, gdzie Σe_i = 1
        (e to wektor eigen dla macierzy P^T z wartością własną 1)
        """
        # Znajdujemy stacjonarny rozkład dla łańcucha Markova
        # e·P = e  =>  e·(P - I) = 0
        A = (self.P.T - np.eye(self.K))
        # Dodajemy warunek normalizacji: Σe_i = 1
        A = np.vstack([A, np.ones(self.K)])
        b = np.zeros(self.K + 1)
        b[-1] = 1.0

        # Rozwiązanie metodą najmniejszych kwadratów
        self.e = np.linalg.lstsq(A, b, rcond=None)[0]

        # Upewnij się, że e > 0
        self.e = np.abs(self.e)
        self.e /= self.e.sum()  # Normalizacja

    def get_configuration(self) -> Dict[str, Any]:
        """
        Zwraca pełną konfigurację sieci w czytelnym formacie.

        Returns:
            Słownik z wszystkimi parametrami sieci
        """
        return {
            'num_stations': self.K,
            'num_customers': self.N,
            'station_names': self.station_names,
            'service_rates': self.mu.tolist(),
            'num_servers': self.m.tolist(),
            'routing_matrix': self.P.tolist(),
            'visit_ratios': self.e.tolist()
        }

    def update_parameters(self, **kwargs):
        """
        Aktualizuje parametry sieci (używane przez algorytm optymalizacyjny).

        PRZYKŁAD UŻYCIA:
        ----------------
        network.update_parameters(
            num_servers=[3, 2, 4],  # Zmień liczbę serwerów
            service_rates=[6, 4, 5]  # Zmień szybkość obsługi
        )

        Args:
            **kwargs: Parametry do aktualizacji (num_servers, service_rates, routing_matrix)
        """
        if 'num_servers' in kwargs:
            self.m = np.array(kwargs['num_servers'], dtype=int)

        if 'service_rates' in kwargs:
            self.mu = np.array(kwargs['service_rates'])

        if 'routing_matrix' in kwargs:
            self.P = np.array(kwargs['routing_matrix'])
            self._compute_visit_ratios()

    def __repr__(self):
        """Czytelna reprezentacja sieci."""
        return (f"QueueingNetwork(K={self.K}, N={self.N}, "
                f"μ={self.mu.tolist()}, m={self.m.tolist()})")
