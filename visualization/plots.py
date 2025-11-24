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


def plot_profit_breakdown(results: Dict[str, Any]) -> str:
    """
    Wykres breakdown zysku ekonomicznego (dla funkcji profit).
    Pokazuje: przychod, koszty, zysk netto - przed i po optymalizacji.

    Args:
        results: Pelne wyniki optymalizacji z kosztem typu 'profit_breakdown'

    Returns:
        Base64 encoded string z obrazem (lub pusty jesli nie ma danych)
    """
    cost = results.get('cost')
    if not cost or cost.get('type') != 'profit_breakdown':
        return ""

    fig, ax = plt.subplots(figsize=(12, 7))

    categories = ['Przychod\n(r*X)', 'Koszt\nserwerow\n(Cs*sum_mu)', 'Koszt\nklientow\n(Cn*N)', 'Zysk\nnetto']

    before_values = [
        cost['baseline']['revenue'],
        -cost['baseline']['cost_servers'],
        -cost['baseline']['cost_customers'],
        cost['baseline']['profit']
    ]

    after_values = [
        cost['optimized']['revenue'],
        -cost['optimized']['cost_servers'],
        -cost['optimized']['cost_customers'],
        cost['optimized']['profit']
    ]

    x = np.arange(len(categories))
    width = 0.35

    bars1 = ax.bar(x - width/2, before_values, width,
                   label='Przed optymalizacja', color='#ff6b6b', alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, after_values, width,
                   label='Po optymalizacji', color='#51cf66', alpha=0.8, edgecolor='black')

    ax.set_ylabel('Wartosc', fontsize=12)
    ax.set_title('Analiza ekonomiczna (Profit Breakdown)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10)
    ax.legend(fontsize=10)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax.grid(axis='y', alpha=0.3)

    # Dodaj wartosci na slupkach
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            label_y = height + (0.5 if height >= 0 else -0.5)
            ax.text(bar.get_x() + bar.get_width()/2., label_y,
                   f'{height:.2f}',
                   ha='center', va='bottom' if height >= 0 else 'top',
                   fontsize=9, fontweight='bold')

    # Dodaj ROI w narozniku
    roi = cost['delta']['roi_percent']
    investment = cost['delta']['investment']
    gain = cost['delta']['profit_gain']

    info_text = f"Inwestycja: {investment:.2f}\nZysk: {gain:.2f}\nROI: {roi:.1f}%"
    ax.text(0.98, 0.97, info_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return img_base64


def plot_weighted_radar(baseline: Dict[str, Any], optimized: Dict[str, Any]) -> str:
    """
    Wykres radarowy (pajak) dla funkcji weighted_objective.
    Porownuje znormalizowane metryki przed i po optymalizacji.

    Args:
        baseline: Metryki przed optymalizacja
        optimized: Metryki po optymalizacji

    Returns:
        Base64 encoded string z obrazem
    """
    baseline_metrics = baseline['metrics']
    optimized_metrics = optimized['metrics']

    # Kategorie do porownania
    categories = ['Czas\nodpowiedzi', 'Przepustowosc', 'Dlugosc\nkolejki', 'Wykorzystanie']

    # Normalizuj metryki (im wyzszy tym lepiej, 0-1)
    # Czas odpowiedzi - mniejszy = lepszy
    R_before = baseline_metrics['mean_response_time']
    R_after = optimized_metrics['mean_response_time']
    R_max = max(R_before, R_after)
    R_normalized_before = 1 - (R_before / R_max) if R_max > 0 else 0.5
    R_normalized_after = 1 - (R_after / R_max) if R_max > 0 else 0.5

    # Przepustowosc - wieksza = lepsza
    X_before = baseline_metrics['throughput']
    X_after = optimized_metrics['throughput']
    X_max = max(X_before, X_after)
    X_normalized_before = X_before / X_max if X_max > 0 else 0.5
    X_normalized_after = X_after / X_max if X_max > 0 else 0.5

    # Dlugosc kolejki - mniejsza = lepsza
    L_before = baseline_metrics['mean_queue_length']
    L_after = optimized_metrics['mean_queue_length']
    L_max = max(L_before, L_after)
    L_normalized_before = 1 - (L_before / L_max) if L_max > 0 else 0.5
    L_normalized_after = 1 - (L_after / L_max) if L_max > 0 else 0.5

    # Wykorzystanie - srednie
    U_before = np.mean(baseline_metrics['utilizations'])
    U_after = np.mean(optimized_metrics['utilizations'])

    values_before = [R_normalized_before, X_normalized_before, L_normalized_before, U_before]
    values_after = [R_normalized_after, X_normalized_after, L_normalized_after, U_after]

    # Zamknij wykres (dodaj pierwszy element na koncu)
    values_before += values_before[:1]
    values_after += values_after[:1]

    # Katy dla kazdej kategorii
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    # Stworz wykres
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

    ax.plot(angles, values_before, 'o-', linewidth=2, label='Przed', color='#ff6b6b')
    ax.fill(angles, values_before, alpha=0.25, color='#ff6b6b')

    ax.plot(angles, values_after, 'o-', linewidth=2, label='Po', color='#51cf66')
    ax.fill(angles, values_after, alpha=0.25, color='#51cf66')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_title('Porownanie metryk (Wykres radarowy)\nFunkcja: weighted_objective',
                 y=1.08, fontsize=13, fontweight='bold')
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
    ax.grid(True)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
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

    # Wykres percentyli czasow odpowiedzi
    resp_percentiles_img = plot_response_time_percentiles(
        results['baseline'],
        results['optimized']
    )
    if resp_percentiles_img:
        plots['response_time_percentiles'] = resp_percentiles_img

    # Wykres breakdown zysku (dla profit)
    profit_img = plot_profit_breakdown(results)
    if profit_img:
        plots['profit_breakdown'] = profit_img

    # Wykres radarowy (dla weighted_objective)
    objective_name = results.get('optimization_info', {}).get('objective_name', '')
    if objective_name == 'weighted_objective':
        radar_img = plot_weighted_radar(results['baseline'], results['optimized'])
        if radar_img:
            plots['weighted_radar'] = radar_img

    return plots
