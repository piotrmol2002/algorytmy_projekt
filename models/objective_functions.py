"""
====================================================================
FUNKCJE CELU (Objective Functions)
====================================================================

CO TO JEST FUNKCJA CELU?
-------------------------
To funkcja, którą algorytm próbuje ZMINIMALIZOWAĆ (lub zmaksymalizować).
Mówi algorytmowi "co jest ważne" w optymalizacji.

PRZYKŁADY:
----------
1. "Chcę jak NAJKRÓTSZY średni czas oczekiwania"
   → Funkcja celu = średni czas odpowiedzi (minimize)

2. "Chcę jak NAJKRÓTSZE kolejki"
   → Funkcja celu = średnia długość kolejki (minimize)

3. "Chcę równomierne obciążenie serwerów"
   → Funkcja celu = odchylenie standardowe utilizacji (minimize)

4. "Chcę niski czas + niski koszt"
   → Funkcja celu = w1*czas + w2*koszt (minimize)

W UI BĘDZIESZ MÓGŁ WYBRAĆ, KTÓRĄ FUNKCJĘ UŻYWASZ!
====================================================================
"""

import numpy as np
from typing import Dict, Any, List, Callable


class ObjectiveFunctions:
    """
    Zbiór różnych funkcji celu do optymalizacji sieci kolejkowej.

    Każda funkcja przyjmuje wyniki analizy (metrics) i zwraca JEDNĄ LICZBĘ,
    którą algorytm będzie minimalizował.
    """

    @staticmethod
    def mean_response_time(metrics: Dict[str, Any]) -> float:
        """
        FUNKCJA 1: Średni czas odpowiedzi (Mean Response Time)

        CO TO OZNACZA?
        --------------
        Średni czas, jaki klient spędza w całym systemie (oczekiwanie + obsługa)

        PRZYKŁAD:
        ---------
        Jeśli średni czas = 5 sekund, to przeciętnie zadanie potrzebuje
        5 sekund od wejścia do wyjścia z systemu.

        CEL: MINIMALIZOWAĆ (chcemy jak najszybszy system)

        Args:
            metrics: Słownik z metrykami zawierający 'mean_response_time'

        Returns:
            Wartość do minimalizacji
        """
        return metrics['mean_response_time']

    @staticmethod
    def mean_queue_length(metrics: Dict[str, Any]) -> float:
        """
        FUNKCJA 2: Średnia długość kolejki (Mean Queue Length)

        CO TO OZNACZA?
        --------------
        Średnia liczba klientów czekających w kolejkach (we WSZYSTKICH stacjach)

        PRZYKŁAD:
        ---------
        Jeśli średnia długość = 15, to przeciętnie w systemie czeka 15 zadań

        CEL: MINIMALIZOWAĆ (chcemy krótkie kolejki)

        Args:
            metrics: Słownik z metrykami zawierający 'mean_queue_length'

        Returns:
            Wartość do minimalizacji
        """
        return metrics['mean_queue_length']

    @staticmethod
    def max_queue_length(metrics: Dict[str, Any]) -> float:
        """
        FUNKCJA 3: Maksymalna długość kolejki na JEDNEJ stacji

        CO TO OZNACZA?
        --------------
        Długość kolejki na najbardziej obciążonej stacji

        PRZYKŁAD:
        ---------
        Jeśli stacja 2 ma kolejkę 25 zadań, a inne mają 5, to wartość = 25

        CEL: MINIMALIZOWAĆ (chcemy unikać wąskich gardeł)

        Args:
            metrics: Słownik z metrykami zawierający 'queue_lengths'

        Returns:
            Wartość do minimalizacji
        """
        queue_lengths = metrics['queue_lengths']
        return max(queue_lengths)

    @staticmethod
    def utilization_variance(metrics: Dict[str, Any]) -> float:
        """
        FUNKCJA 4: Wariancja wykorzystania serwerów (Utilization Variance)

        CO TO OZNACZA?
        --------------
        Mierzy jak NIERÓWNOMIERNIE obciążone są serwery.
        - Niska wariancja = wszystkie serwery pracują podobnie (DOBRZE)
        - Wysoka wariancja = niektóre serwery przeciążone, inne bezczynne (ŹLE)

        PRZYKŁAD:
        ---------
        Utilizacja [90%, 90%, 85%] → wariancja niska (równomierne)
        Utilizacja [95%, 20%, 10%] → wariancja wysoka (nierównomierne)

        CEL: MINIMALIZOWAĆ (chcemy równomierny load balancing)

        Args:
            metrics: Słownik z metrykami zawierający 'utilizations'

        Returns:
            Wartość do minimalizacji
        """
        utilizations = np.array(metrics['utilizations'])
        return np.var(utilizations)

    @staticmethod
    def throughput_negative(metrics: Dict[str, Any]) -> float:
        """
        FUNKCJA 5: Przepustowość (Throughput) - wersja do minimalizacji

        CO TO OZNACZA?
        --------------
        Przepustowość = ile zadań system przetwarza na jednostkę czasu
        - Wysoka przepustowość = szybki system (DOBRZE)

        UWAGA: Zwracamy UJEMNĄ wartość, bo algorytm minimalizuje,
               a my chcemy MAKSYMALIZOWAĆ przepustowość

        CEL: MINIMALIZOWAĆ ujemną wartość = MAKSYMALIZOWAĆ przepustowość

        Args:
            metrics: Słownik z metrykami zawierający 'throughput'

        Returns:
            Wartość do minimalizacji (ujemna przepustowość)
        """
        return -metrics['throughput']

    @staticmethod
    def weighted_multi_objective(
        metrics: Dict[str, Any],
        weights: Dict[str, float]
    ) -> float:
        """
        FUNKCJA 6: Wielokryterialna funkcja celu (Multi-Objective)

        CO TO OZNACZA?
        --------------
        Możesz optymalizować KILKA rzeczy naraz z różnymi wagami!

        PRZYKŁAD:
        ---------
        Chcesz:
        - 70% wagi na krótki czas oczekiwania
        - 30% wagi na równomierne obciążenie

        weights = {
            'response_time': 0.7,
            'utilization_variance': 0.3
        }

        FORMUŁA:
        --------
        Objective = w1·czas + w2·wariancja + w3·kolejki + ...

        CEL: MINIMALIZOWAĆ ważoną sumę

        Args:
            metrics: Słownik z metrykami
            weights: Słownik z wagami dla różnych metryk
                     np. {'response_time': 0.5, 'queue_length': 0.5}

        Returns:
            Wartość do minimalizacji
        """
        objective = 0.0

        # Dodaj składniki z odpowiednimi wagami
        if 'response_time' in weights:
            objective += weights['response_time'] * metrics['mean_response_time']

        if 'queue_length' in weights:
            objective += weights['queue_length'] * metrics['mean_queue_length']

        if 'utilization_variance' in weights:
            utilizations = np.array(metrics['utilizations'])
            objective += weights['utilization_variance'] * np.var(utilizations)

        if 'max_queue' in weights:
            objective += weights['max_queue'] * max(metrics['queue_lengths'])

        # Możesz dodać koszt (np. koszt serwerów)
        if 'cost' in weights and 'total_servers' in metrics:
            # Załóżmy, że każdy serwer kosztuje jednostkowo 1
            objective += weights['cost'] * metrics['total_servers']

        return objective


# =============================================================================
# KATALOG DOSTĘPNYCH FUNKCJI CELU (dla UI)
# =============================================================================

OBJECTIVE_CATALOG = {
    'mean_response_time': {
        'name': 'Średni czas odpowiedzi',
        'description': 'Minimalizuj średni czas, jaki klient spędza w systemie (oczekiwanie + obsługa)',
        'function': ObjectiveFunctions.mean_response_time,
        'unit': 'sekundy',
        'goal': 'minimize'
    },
    'mean_queue_length': {
        'name': 'Średnia długość kolejki',
        'description': 'Minimalizuj średnią liczbę klientów czekających w kolejkach',
        'function': ObjectiveFunctions.mean_queue_length,
        'unit': 'klienci',
        'goal': 'minimize'
    },
    'max_queue_length': {
        'name': 'Maksymalna długość kolejki',
        'description': 'Minimalizuj największą kolejkę w systemie (unikaj wąskich gardeł)',
        'function': ObjectiveFunctions.max_queue_length,
        'unit': 'klienci',
        'goal': 'minimize'
    },
    'utilization_variance': {
        'name': 'Równomierność obciążenia',
        'description': 'Minimalizuj różnice w wykorzystaniu serwerów (load balancing)',
        'function': ObjectiveFunctions.utilization_variance,
        'unit': 'bezwymiarowe',
        'goal': 'minimize'
    },
    'throughput': {
        'name': 'Przepustowość systemu',
        'description': 'Maksymalizuj liczbę zadań przetwarzanych na jednostkę czasu',
        'function': ObjectiveFunctions.throughput_negative,
        'unit': 'zadania/s',
        'goal': 'maximize'
    }
}


def get_objective_function(objective_name: str) -> Callable:
    """
    Pobiera funkcję celu na podstawie nazwy.

    UŻYCIE W UI:
    ------------
    Użytkownik wybiera z listy "Średni czas odpowiedzi"
    → funkcja zwraca odpowiednią funkcję do użycia w optymalizacji

    Args:
        objective_name: Nazwa funkcji z OBJECTIVE_CATALOG

    Returns:
        Funkcja celu gotowa do użycia
    """
    if objective_name not in OBJECTIVE_CATALOG:
        raise ValueError(f"Nieznana funkcja celu: {objective_name}. "
                         f"Dostępne: {list(OBJECTIVE_CATALOG.keys())}")

    return OBJECTIVE_CATALOG[objective_name]['function']


def list_available_objectives() -> List[Dict[str, Any]]:
    """
    Zwraca listę wszystkich dostępnych funkcji celu (dla UI).

    UŻYCIE:
    -------
    W interfejsie webowym wyświetl tę listę jako opcje do wyboru

    Returns:
        Lista słowników z informacjami o funkcjach celu
    """
    return [
        {
            'id': key,
            'name': info['name'],
            'description': info['description'],
            'unit': info['unit'],
            'goal': info['goal']
        }
        for key, info in OBJECTIVE_CATALOG.items()
    ]
