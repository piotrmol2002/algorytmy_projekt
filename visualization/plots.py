"""
====================================================================
MODUŁ WIZUALIZACJI
====================================================================

Generuje wykresy porównujące wyniki przed i po optymalizacji.

RODZAJE WYKRESÓW:
-----------------
1. Wykres konwergencji algorytmu Firefly
2. Porównanie metryk (przed vs po)
3. Porównanie długości kolejek na stacjach
4. Porównanie wykorzystania serwerów

====================================================================
"""

import matplotlib
matplotlib.use('Agg')  # Backend dla serwerów bez GUI
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any, List
import io
import base64


def plot_convergence(history: Dict[str, List]) -> str:
    """
    Wykres konwergencji algorytmu Firefly.

    Pokazuje jak wartość funkcji celu zmienia się w czasie optymalizacji.

    Args:
        history: Historia optymalizacji z FireflyAlgorithm

    Returns:
        Base64 encoded string z obrazem
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    iterations = range(1, len(history['best_values']) + 1)

    # Najlepsza wartość (zielona linia)
    ax.plot(iterations, history['best_values'],
            'g-', linewidth=2, label='Najlepsza wartość')

    # Średnia wartość (niebieska linia)
    ax.plot(iterations, history['mean_values'],
            'b--', linewidth=1.5, label='Średnia w populacji')

    # Najgorsza wartość (czerwona linia)
    ax.plot(iterations, history['worst_values'],
            'r:', linewidth=1, alpha=0.7, label='Najgorsza wartość')

    ax.set_xlabel('Iteracja', fontsize=12)
    ax.set_ylabel('Wartość funkcji celu', fontsize=12)
    ax.set_title('Konwergencja Algorytmu Firefly', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # Konwersja do base64
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return img_base64


def plot_metrics_comparison(baseline: Dict[str, Any], optimized: Dict[str, Any]) -> str:
    """
    Wykres porównania głównych metryk (przed vs po).

    Args:
        baseline: Metryki przed optymalizacją
        optimized: Metryki po optymalizacji

    Returns:
        Base64 encoded string z obrazem
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Metryki do porównania
    metrics = [
        ('mean_response_time', 'Średni czas odpowiedzi [s]'),
        ('mean_queue_length', 'Średnia długość kolejki'),
        ('throughput', 'Przepustowość [zadania/s]'),
        ('total_servers', 'Łączna liczba serwerów')
    ]

    for idx, (metric_key, metric_label) in enumerate(metrics):
        ax = axes[idx // 2, idx % 2]

        baseline_val = baseline['metrics'][metric_key]
        optimized_val = optimized['metrics'][metric_key]

        bars = ax.bar(['Przed', 'Po'], [baseline_val, optimized_val],
                      color=['#ff6b6b', '#51cf66'], alpha=0.8, edgecolor='black')

        ax.set_ylabel(metric_label, fontsize=11)
        ax.set_title(metric_label, fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        # Dodaj wartości na słupkach
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Oblicz procentową zmianę
        if baseline_val != 0:
            change_percent = ((optimized_val - baseline_val) / baseline_val) * 100
            color = 'green' if (change_percent < 0 and metric_key != 'throughput') or \
                              (change_percent > 0 and metric_key == 'throughput') else 'red'
            ax.text(0.5, 0.95, f'Zmiana: {change_percent:+.1f}%',
                   transform=ax.transAxes, ha='center', va='top',
                   fontsize=9, color=color, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()

    # Konwersja do base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return img_base64


def plot_queue_lengths_comparison(baseline: Dict[str, Any], optimized: Dict[str, Any]) -> str:
    """
    Wykres porównania długości kolejek na każdej stacji.

    Args:
        baseline: Metryki przed optymalizacją
        optimized: Metryki po optymalizacji

    Returns:
        Base64 encoded string z obrazem
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    station_names = baseline['metrics']['station_names']
    baseline_queues = baseline['metrics']['queue_lengths']
    optimized_queues = optimized['metrics']['queue_lengths']

    x = np.arange(len(station_names))
    width = 0.35

    bars1 = ax.bar(x - width/2, baseline_queues, width,
                   label='Przed optymalizacją', color='#ff6b6b', alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, optimized_queues, width,
                   label='Po optymalizacji', color='#51cf66', alpha=0.8, edgecolor='black')

    ax.set_xlabel('Stacja', fontsize=12)
    ax.set_ylabel('Długość kolejki [liczba klientów]', fontsize=12)
    ax.set_title('Porównanie długości kolejek na stacjach', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(station_names, rotation=15, ha='right')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    # Dodaj wartości na słupkach
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=9)

    plt.tight_layout()

    # Konwersja do base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return img_base64


def plot_utilization_comparison(baseline: Dict[str, Any], optimized: Dict[str, Any]) -> str:
    """
    Wykres porównania wykorzystania serwerów (utilization).

    Args:
        baseline: Metryki przed optymalizacją
        optimized: Metryki po optymalizacji

    Returns:
        Base64 encoded string z obrazem
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    station_names = baseline['metrics']['station_names']
    baseline_util = [u * 100 for u in baseline['metrics']['utilizations']]  # Konwersja na %
    optimized_util = [u * 100 for u in optimized['metrics']['utilizations']]

    x = np.arange(len(station_names))
    width = 0.35

    bars1 = ax.bar(x - width/2, baseline_util, width,
                   label='Przed optymalizacją', color='#ff6b6b', alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, optimized_util, width,
                   label='Po optymalizacji', color='#51cf66', alpha=0.8, edgecolor='black')

    ax.set_xlabel('Stacja', fontsize=12)
    ax.set_ylabel('Wykorzystanie serwerów [%]', fontsize=12)
    ax.set_title('Porównanie wykorzystania serwerów', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(station_names, rotation=15, ha='right')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 110)  # 0-110% dla lepszej widoczności

    # Linia 100% (maksymalne wykorzystanie)
    ax.axhline(y=100, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Maksymalne wykorzystanie')

    # Dodaj wartości na słupkach
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=9)

    plt.tight_layout()

    # Konwersja do base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return img_base64

def plot_response_time_percentiles(baseline: Dict[str, Any], optimized: Dict[str, Any]) -> str:
    """
    Wykres percentyli czasów odpowiedzi (np. 50%, 90%, 95%, 99%) przed i po optymalizacji.

    Wykorzystuje:
    - metrics['response_time_samples'] jeśli istnieje (dokładne próbki),
    - w przeciwnym razie metrics['response_times'] (średnie czasy per stacja – przybliżenie).

    Args:
        baseline: Metryki przed optymalizacją
        optimized: Metryki po optymalizacji

    Returns:
        Base64 encoded string z obrazem (lub pusty string, jeśli brak danych)
    """
    baseline_metrics = baseline['metrics']
    optimized_metrics = optimized['metrics']

    # Pobierz próbki / czasy odpowiedzi
    if 'response_time_samples' in baseline_metrics:
        R_before = np.array(baseline_metrics['response_time_samples'], dtype=float)
    else:
        R_before = np.array(baseline_metrics.get('response_times', []), dtype=float)

    if 'response_time_samples' in optimized_metrics:
        R_after = np.array(optimized_metrics['response_time_samples'], dtype=float)
    else:
        R_after = np.array(optimized_metrics.get('response_times', []), dtype=float)

    # Jeśli nie mamy danych → nie rysujemy
    if R_before.size == 0 or R_after.size == 0:
        return ""

    percentiles = [50, 90, 95, 99]
    labels = [f"{p}%" for p in percentiles]

    values_before = [np.percentile(R_before, p) for p in percentiles]
    values_after = [np.percentile(R_after, p) for p in percentiles]

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(percentiles))
    width = 0.35

    bars1 = ax.bar(x - width/2, values_before, width,
                   label='Przed optymalizacją', color='#ff6b6b', alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, values_after, width,
                   label='Po optymalizacji', color='#51cf66', alpha=0.8, edgecolor='black')

    ax.set_xlabel('Percentyl', fontsize=12)
    ax.set_ylabel('Czas odpowiedzi [s]', fontsize=12)
    ax.set_title('Percentyle czasów odpowiedzi', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    # Dodaj wartości na słupkach
    for bars in (bars1, bars2):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}',
                    ha='center', va='bottom', fontsize=9)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return img_base64
def generate_all_plots(results: Dict[str, Any]) -> Dict[str, str]:
    """
    Generuje wszystkie wykresy naraz.

    Args:
        results: Pełne wyniki z QueueingOptimizer.optimize()

    Returns:
        Słownik z base64 encoded obrazami
    """
    plots = {}

    # Wykres konwergencji
    if 'history' in results:
        plots['convergence'] = plot_convergence(results['history'])

    # Porównanie metryk
    plots['metrics'] = plot_metrics_comparison(
        results['baseline'],
        results['optimized']
    )

    # Porównanie kolejek
    plots['queues'] = plot_queue_lengths_comparison(
        results['baseline'],
        results['optimized']
    )

    # Porównanie wykorzystania
    plots['utilization'] = plot_utilization_comparison(
        results['baseline'],
        results['optimized']
    )
     # Wykres percentyli czasów odpowiedzi
    resp_percentiles_img = plot_response_time_percentiles(
        results['baseline'],
        results['optimized']
    )
    if resp_percentiles_img:
        plots['response_time_percentiles'] = resp_percentiles_img

    return plots
