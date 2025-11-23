"""
====================================================================
FIREFLY ALGORITHM (Algorytm Świetlika)
====================================================================

CO TO JEST ALGORYTM ŚWIETLIKA?
-------------------------------
To metaheurystyczny algorytm optymalizacyjny inspirowany zachowaniem
świetlików w naturze.

JAK DZIAŁAJĄ ŚWIETLIKI W NATURZE?
----------------------------------
1. Świetliki świecą, aby przyciągać partnerów
2. Im jaśniejszy świetlik, tym bardziej atrakcyjny
3. Świetlik porusza się w stronę jaśniejszego świetlika
4. Im dalej, tym słabsze światło (absorpcja przez powietrze)
5. Najjaśniejszy świetlik porusza się losowo

JAK TO PRZEKŁADAMY NA OPTYMALIZACJĘ?
-------------------------------------
1. Każdy świetlik = jedno ROZWIĄZANIE problemu
   (np. konfiguracja liczby serwerów [3, 2, 4])

2. Jasność świetlika = JAKOŚĆ rozwiązania
   (im niższa wartość funkcji celu, tym jaśniejszy)

3. Świetliki poruszają się = MODYFIKACJA rozwiązań
   (zmiana liczby serwerów, routing, etc.)

4. Najlepszy świetlik = OPTIMUM
   (najlepsza znaleziona konfiguracja)

PARAMETRY ALGORYTMU:
--------------------
- n: Liczba świetlików (np. 20) = rozmiar populacji rozwiązań
- α (alpha): Parametr losowości (0-1) = jak bardzo eksplorujemy
- β₀ (beta_0): Atrakcyjność bazowa (0-1) = siła przyciągania
- γ (gamma): Współczynnik absorpcji (0-∞) = jak szybko maleje światło
- max_iter: Liczba iteracji (np. 100)

ALGORYTM (uproszczone kroki):
------------------------------
1. Wygeneruj n losowych świetlików (rozwiązań)
2. Oceń jasność każdego (oblicz funkcję celu)
3. Dla każdej iteracji:
   a) Dla każdego świetlika i:
      - Porównaj z każdym innym świetlikiem j
      - Jeśli j jest jaśniejszy, rusz i w stronę j
   b) Przesuń najlepszego świetlika losowo
   c) Oceń nowe pozycje
4. Zwróć najlepsze rozwiązanie

====================================================================
"""

import numpy as np
from typing import Dict, Any, List, Callable, Optional, Tuple
import copy


class FireflyAlgorithm:
    """
    Implementacja Firefly Algorithm dla problemów optymalizacyjnych.

    ZASTOSOWANIE:
    -------------
    optimizer = FireflyAlgorithm(
        objective_function=my_objective,
        bounds=[(1, 10), (1, 10), (1, 10)],  # Ograniczenia dla 3 zmiennych
        n_fireflies=20,
        max_iterations=100
    )
    best_solution, best_value, history = optimizer.optimize()
    """

    def __init__(
        self,
        objective_function: Callable,
        bounds: List[Tuple[float, float]],
        n_fireflies: int = 25,
        max_iterations: int = 100,
        alpha: float = 0.5,
        beta_0: float = 1.0,
        gamma: float = 1.0,
        integer_vars: Optional[List[int]] = None,
        verbose: bool = True
    ):
        """
        Inicjalizacja algorytmu Firefly.

        Args:
            objective_function: Funkcja celu do MINIMALIZACJI
                               np. lambda x: calculate_response_time(x)
            bounds: Lista zakresów dla każdej zmiennej decyzyjnej
                   np. [(1, 10), (1, 10)] dla 2 zmiennych w zakresie 1-10
            n_fireflies: Liczba świetlików (rozmiar populacji)
                        Więcej = lepsza eksploracja, ale wolniej
            max_iterations: Maksymalna liczba iteracji
                           Więcej = lepsze wyniki, ale dłużej
            alpha: Parametr losowości (0-1)
                  Wyższy = więcej eksploracji (przeszukiwanie)
                  Niższy = więcej eksploatacji (zbieżność)
            beta_0: Atrakcyjność bazowa (0-1)
                   Wyższy = silniejsze przyciąganie między świetlikami
            gamma: Współczynnik absorpcji światła (0-∞)
                  Wyższy = światło szybciej zanika z odległością
                  Niższy = świetliki "widzą się" z daleka
            integer_vars: Indeksy zmiennych, które muszą być całkowite
                         np. [0, 1, 2] jeśli liczba serwerów musi być int
            verbose: Czy wyświetlać postęp optymalizacji
        """
        self.objective_function = objective_function
        self.bounds = np.array(bounds)
        self.n_fireflies = n_fireflies
        self.max_iterations = max_iterations
        self.alpha = alpha
        self.beta_0 = beta_0
        self.gamma = gamma
        self.integer_vars = integer_vars if integer_vars else []
        self.verbose = verbose

        # Wymiary przestrzeni poszukiwań
        self.n_dimensions = len(bounds)
        self.lower_bounds = self.bounds[:, 0]
        self.upper_bounds = self.bounds[:, 1]

        # Historia optymalizacji (do wizualizacji)
        self.history = {
            'best_values': [],      # Najlepsza wartość w każdej iteracji
            'mean_values': [],      # Średnia wartość w populacji
            'worst_values': [],     # Najgorsza wartość w populacji
            'best_solutions': []    # Najlepsze rozwiązanie w każdej iteracji
        }

    def _initialize_fireflies(self) -> np.ndarray:
        """
        KROK 1: Inicjalizacja populacji świetlików (losowe rozwiązania).

        Generuje n_fireflies losowych pozycji w przestrzeni poszukiwań.

        PRZYKŁAD:
        ---------
        Jeśli optymalizujemy liczbę serwerów na 3 stacjach:
        bounds = [(1, 5), (1, 5), (1, 5)]
        Wygeneruje np:
        firefly_1 = [3, 2, 4]
        firefly_2 = [1, 5, 2]
        firefly_3 = [4, 3, 3]
        ...

        Returns:
            Macierz (n_fireflies × n_dimensions) z pozycjami świetlików
        """
        fireflies = np.random.uniform(
            self.lower_bounds,
            self.upper_bounds,
            size=(self.n_fireflies, self.n_dimensions)
        )

        # Zaokrąglij zmienne całkowite (np. liczba serwerów)
        for idx in self.integer_vars:
            fireflies[:, idx] = np.round(fireflies[:, idx])

        return fireflies

    def _evaluate_fireflies(self, fireflies: np.ndarray) -> np.ndarray:
        """
        KROK 2: Oceń jasność każdego świetlika (wartość funkcji celu).

        Args:
            fireflies: Macierz z pozycjami świetlików

        Returns:
            Wektor wartości funkcji celu dla każdego świetlika
        """
        intensities = np.zeros(self.n_fireflies)

        for i in range(self.n_fireflies):
            try:
                intensities[i] = self.objective_function(fireflies[i])
            except Exception as e:
                # Jeśli funkcja celu rzuca błąd, przypisz bardzo wysoką wartość
                intensities[i] = 1e10
                if self.verbose:
                    print(f"Błąd w ocenie świetlika {i}: {e}")

        return intensities

    def _distance(self, firefly_i: np.ndarray, firefly_j: np.ndarray) -> float:
        """
        Oblicz odległość euklidesową między dwoma świetlikami.

        WYJAŚNIENIE:
        ------------
        Odległość mówi, jak bardzo różnią się dwa rozwiązania.
        Im dalej, tym słabsze przyciąganie.

        Args:
            firefly_i: Pozycja pierwszego świetlika
            firefly_j: Pozycja drugiego świetlika

        Returns:
            Odległość euklidesowa
        """
        return np.linalg.norm(firefly_i - firefly_j)

    def _attractiveness(self, distance: float) -> float:
        """
        Oblicz atrakcyjność w funkcji odległości.

        FORMUŁA: β(r) = β₀ · e^(-γ · r²)

        WYJAŚNIENIE:
        ------------
        - Atrakcyjność maleje wykładniczo z odległością
        - β₀ = atrakcyjność bazowa (gdy r=0)
        - γ kontroluje jak szybko maleje
        - Im dalej świetliki, tym słabsze przyciąganie

        Args:
            distance: Odległość między świetlikami

        Returns:
            Wartość atrakcyjności (0-β₀)
        """
        return self.beta_0 * np.exp(-self.gamma * distance ** 2)

    def _move_firefly(
        self,
        firefly_i: np.ndarray,
        firefly_j: np.ndarray,
        beta: float
    ) -> np.ndarray:
        """
        KROK 3: Przesuń świetlika i w stronę jaśniejszego świetlika j.

        FORMUŁA: x_i^new = x_i + β(r)·(x_j - x_i) + α·(rand - 0.5)

        SKŁADNIKI:
        ----------
        1. β(r)·(x_j - x_i): Przyciąganie do jaśniejszego świetlika
        2. α·(rand - 0.5): Losowe perturbacje (eksploracja)

        PRZYKŁAD:
        ---------
        firefly_i = [3, 2, 4]  (gorszy)
        firefly_j = [4, 3, 5]  (lepszy)
        β = 0.8
        → firefly_i przesuwa się w stronę firefly_j

        Args:
            firefly_i: Pozycja świetlika do przesunięcia
            firefly_j: Pozycja jaśniejszego świetlika (cel)
            beta: Atrakcyjność

        Returns:
            Nowa pozycja świetlika i
        """
        # Składnik przyciągania
        attraction = beta * (firefly_j - firefly_i)

        # Składnik losowy (eksploracja)
        random_step = self.alpha * (np.random.rand(self.n_dimensions) - 0.5)

        # Nowa pozycja
        new_position = firefly_i + attraction + random_step

        # Upewnij się, że nie wychodzimy poza granice
        new_position = np.clip(new_position, self.lower_bounds, self.upper_bounds)

        # Zaokrąglij zmienne całkowite
        for idx in self.integer_vars:
            new_position[idx] = np.round(new_position[idx])

        return new_position

    def optimize(self) -> Tuple[np.ndarray, float, Dict[str, Any]]:
        """
        GŁÓWNA PĘTLA OPTYMALIZACJI.

        PRZEBIEG:
        ---------
        1. Wygeneruj populację początkową
        2. Oceń wszystkie rozwiązania
        3. Dla każdej iteracji:
           - Porównaj każdą parę świetlików
           - Przesuń ciemniejsze w stronę jaśniejszych
           - Dodaj losowość
           - Oceń nowe pozycje
        4. Zwróć najlepsze znalezione rozwiązanie

        Returns:
            best_solution: Najlepsze znalezione rozwiązanie (np. [4, 3, 5])
            best_value: Wartość funkcji celu dla najlepszego rozwiązania
            history: Historia optymalizacji (do wykresów)
        """
        if self.verbose:
            print("=" * 70)
            print("FIREFLY ALGORITHM - START OPTYMALIZACJI")
            print("=" * 70)
            print(f"Liczba świetlików: {self.n_fireflies}")
            print(f"Wymiary problemu: {self.n_dimensions}")
            print(f"Maksymalna liczba iteracji: {self.max_iterations}")
            print(f"Parametry: alpha={self.alpha}, beta_0={self.beta_0}, gamma={self.gamma}")
            print("=" * 70)

        # KROK 1: Inicjalizacja
        fireflies = self._initialize_fireflies()
        intensities = self._evaluate_fireflies(fireflies)

        # Znajdź najlepszego świetlika
        best_idx = np.argmin(intensities)
        best_solution = fireflies[best_idx].copy()
        best_value = intensities[best_idx]

        if self.verbose:
            print(f"\nRozwiązanie początkowe: {best_solution}")
            print(f"Wartość początkowa: {best_value:.4f}\n")

        # GŁÓWNA PĘTLA OPTYMALIZACJI
        for iteration in range(self.max_iterations):

            # Dla każdego świetlika i
            for i in range(self.n_fireflies):

                # Porównaj z każdym innym świetlikiem j
                for j in range(self.n_fireflies):

                    # Jeśli świetlik j jest jaśniejszy (lepsza wartość celu)
                    if intensities[j] < intensities[i]:

                        # Oblicz odległość i atrakcyjność
                        distance = self._distance(fireflies[i], fireflies[j])
                        beta = self._attractiveness(distance)

                        # Przesuń świetlika i w stronę j
                        fireflies[i] = self._move_firefly(
                            fireflies[i],
                            fireflies[j],
                            beta
                        )

            # Przesuń najlepszego świetlika losowo (eksploracja)
            best_idx = np.argmin(intensities)
            random_walk = self.alpha * (np.random.rand(self.n_dimensions) - 0.5)
            fireflies[best_idx] += random_walk
            fireflies[best_idx] = np.clip(
                fireflies[best_idx],
                self.lower_bounds,
                self.upper_bounds
            )
            for idx in self.integer_vars:
                fireflies[best_idx, idx] = np.round(fireflies[best_idx, idx])

            # Oceń nowe pozycje
            intensities = self._evaluate_fireflies(fireflies)

            # Aktualizuj najlepsze rozwiązanie
            current_best_idx = np.argmin(intensities)
            current_best_value = intensities[current_best_idx]

            if current_best_value < best_value:
                best_value = current_best_value
                best_solution = fireflies[current_best_idx].copy()

            # Zapisz historię (do wykresów)
            self.history['best_values'].append(best_value)
            self.history['mean_values'].append(np.mean(intensities))
            self.history['worst_values'].append(np.max(intensities))
            self.history['best_solutions'].append(best_solution.copy())

            # Wyświetl postęp
            if self.verbose and (iteration + 1) % 10 == 0:
                print(f"Iteracja {iteration + 1}/{self.max_iterations}: "
                      f"Najlepsza wartość = {best_value:.4f}, "
                      f"Średnia = {np.mean(intensities):.4f}")

        if self.verbose:
            print("\n" + "=" * 70)
            print("OPTYMALIZACJA ZAKOŃCZONA")
            print("=" * 70)
            print(f"Najlepsze rozwiązanie: {best_solution}")
            print(f"Najlepsza wartość: {best_value:.4f}")
            print("=" * 70)

        return best_solution, best_value, self.history
