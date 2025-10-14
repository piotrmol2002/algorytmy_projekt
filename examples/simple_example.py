"""
====================================================================
PROSTY PRZYKŁAD UŻYCIA
====================================================================

Ten plik pokazuje jak użyć całego systemu krok po kroku.
Idealny punkt startowy dla nowicjusza!

====================================================================
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from models.queueing_network import QueueingNetwork
from algorithms.optimizer import QueueingOptimizer


def main():
    """
    PRZYKŁAD: Optymalizacja systemu 3 procesorów.

    SCENARIUSZ:
    -----------
    Mamy system komputerowy z 3 procesorami (stacjami).
    20 zadań krąży między nimi.

    POCZĄTKOWA KONFIGURACJA (nieoptymalna):
    - Procesor 1: 2 rdzenie, obsługa 5 zadań/s
    - Procesor 2: 2 rdzenie, obsługa 3 zadania/s
    - Procesor 3: 2 rdzenie, obsługa 4 zadania/s

    CEL: Znaleźć optymalną liczbę rdzeni dla każdego procesora
         (aby zminimalizować średni czas odpowiedzi)

    OGRANICZENIE: Każdy procesor może mieć 1-6 rdzeni
    """

    print("\n" + "="*70)
    print("PRZYKŁAD: Optymalizacja systemu 3 procesorów")
    print("="*70)

    # KROK 1: Definiujemy początkową sieć kolejkową
    print("\n📋 KROK 1: Definiowanie sieci bazowej...")

    network = QueueingNetwork(
        num_stations=3,              # 3 procesory
        num_customers=20,            # 20 zadań w systemie
        service_rates=[5, 3, 4],     # Szybkość obsługi [zadania/s]
        num_servers=[2, 2, 2],       # Początkowa liczba rdzeni
        station_names=['Procesor 1', 'Procesor 2', 'Procesor 3']
    )

    print(f"   ✓ Utworzono sieć z {network.K} stacjami")
    print(f"   ✓ Liczba zadań w systemie: {network.N}")
    print(f"   ✓ Początkowa konfiguracja rdzeni: {network.m.tolist()}")

    # KROK 2: Tworzymy optimizer
    print("\n🔧 KROK 2: Konfiguracja optymizera...")

    optimizer = QueueingOptimizer(
        network=network,
        objective='mean_response_time',  # Minimalizuj czas odpowiedzi
        optimize_vars=['num_servers'],   # Optymalizuj liczbę rdzeni
        server_bounds=(1, 6),            # Każdy procesor: 1-6 rdzeni
        firefly_params={
            'n_fireflies': 20,           # 20 świetlików (rozwiązań)
            'max_iterations': 50,        # 50 iteracji
            'alpha': 0.5,                # Parametr losowości
            'beta_0': 1.0,               # Atrakcyjność bazowa
            'gamma': 1.0                 # Absorpcja światła
        }
    )

    print("   ✓ Optimizer skonfigurowany")
    print(f"   ✓ Funkcja celu: Minimalizacja średniego czasu odpowiedzi")
    print(f"   ✓ Zakres liczby rdzeni: 1-6 na procesor")

    # KROK 3: Uruchamiamy optymalizację!
    print("\n🚀 KROK 3: Uruchamianie optymalizacji...\n")

    results = optimizer.optimize(verbose=True)

    # KROK 4: Wyświetlamy wyniki
    print("\n" + "="*70)
    print("📊 WYNIKI OPTYMALIZACJI")
    print("="*70)

    print("\n🔴 PRZED OPTYMALIZACJĄ:")
    baseline = results['baseline']
    print(f"   Konfiguracja rdzeni: {baseline['network']['num_servers']}")
    print(f"   Średni czas odpowiedzi: {baseline['metrics']['mean_response_time']:.4f} s")
    print(f"   Średnia długość kolejki: {baseline['metrics']['mean_queue_length']:.2f} zadań")
    print(f"   Przepustowość: {baseline['metrics']['throughput']:.4f} zadań/s")

    print("\n🟢 PO OPTYMALIZACJI:")
    optimized = results['optimized']
    print(f"   Konfiguracja rdzeni: {optimized['network']['num_servers']}")
    print(f"   Średni czas odpowiedzi: {optimized['metrics']['mean_response_time']:.4f} s")
    print(f"   Średnia długość kolejki: {optimized['metrics']['mean_queue_length']:.2f} zadań")
    print(f"   Przepustowość: {optimized['metrics']['throughput']:.4f} zadań/s")

    print("\n✨ POPRAWA:")
    improvement = results['improvement']
    print(f"   Procentowa poprawa: {improvement['percent']:.2f}%")
    print(f"   Bezwzględna poprawa: {improvement['absolute']:.4f} s")

    print("\n" + "="*70)
    print("✅ Optymalizacja zakończona pomyślnie!")
    print("="*70)


if __name__ == '__main__':
    main()
