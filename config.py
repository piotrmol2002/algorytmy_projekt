"""
====================================================================
PLIK KONFIGURACYJNY
====================================================================

Centralne miejsce na konfigurację aplikacji.

====================================================================
"""

# =============================================================================
# KONFIGURACJA APLIKACJI WEBOWEJ
# =============================================================================

# Flask
FLASK_HOST = '0.0.0.0'  # 0.0.0.0 = dostęp z innych urządzeń w sieci
FLASK_PORT = 5000
FLASK_DEBUG = True

# Tajny klucz Flask (zmień w produkcji!)
SECRET_KEY = 'firefly-optimizer-secret-key-change-in-production'


# =============================================================================
# DOMYŚLNE PARAMETRY SIECI KOLEJKOWEJ
# =============================================================================

DEFAULT_NETWORK = {
    'num_stations': 3,
    'num_customers': 20,
    'service_rates': [5.0, 3.0, 4.0],
    'num_servers': [2, 2, 2],
    'station_names': ['Stacja 1', 'Stacja 2', 'Stacja 3']
}


# =============================================================================
# DOMYŚLNE PARAMETRY ALGORYTMU FIREFLY
# =============================================================================

DEFAULT_FIREFLY_PARAMS = {
    'n_fireflies': 25,           # Liczba świetlików (populacja)
    'max_iterations': 100,       # Liczba iteracji
    'alpha': 0.5,                # Parametr losowości (0-1)
    'beta_0': 1.0,               # Atrakcyjność bazowa
    'gamma': 1.0                 # Współczynnik absorpcji
}


# =============================================================================
# OGRANICZENIA I WALIDACJA
# =============================================================================

# Minimalne i maksymalne wartości
MIN_STATIONS = 2
MAX_STATIONS = 20
MIN_CUSTOMERS = 1
MAX_CUSTOMERS = 200
MIN_SERVICE_RATE = 0.1
MAX_SERVICE_RATE = 100.0
MIN_SERVERS = 1
MAX_SERVERS = 50

# Ograniczenia dla algorytmu Firefly
MIN_FIREFLIES = 10
MAX_FIREFLIES = 100
MIN_ITERATIONS = 10
MAX_ITERATIONS = 1000


# =============================================================================
# USTAWIENIA WIZUALIZACJI
# =============================================================================

# Matplotlib
PLOT_DPI = 100
PLOT_STYLE = 'default'
FIGURE_SIZE_DEFAULT = (10, 6)
FIGURE_SIZE_LARGE = (12, 8)

# Kolory
COLOR_BASELINE = '#ff6b6b'      # Czerwony dla baseline
COLOR_OPTIMIZED = '#51cf66'     # Zielony dla optimized
COLOR_FIREFLY = '#667eea'       # Fioletowy dla Firefly


# =============================================================================
# USTAWIENIA SOLVERA MVA
# =============================================================================

# Tolerancja dla obliczeń numerycznych
MVA_TOLERANCE = 1e-6

# Maksymalna liczba iteracji MVA
MVA_MAX_ITERATIONS = 10000


# =============================================================================
# LOGI I DEBUGOWANIE
# =============================================================================

# Czy wyświetlać szczegółowe logi
VERBOSE = True

# Poziom logowania
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR


# =============================================================================
# FUNKCJE POMOCNICZE
# =============================================================================

def validate_network_params(num_stations, num_customers, service_rates, num_servers):
    """
    Waliduje parametry sieci kolejkowej.

    Args:
        num_stations: Liczba stacji
        num_customers: Liczba klientów
        service_rates: Lista szybkości obsługi
        num_servers: Lista liczb serwerów

    Raises:
        ValueError: Jeśli parametry są nieprawidłowe
    """
    if not (MIN_STATIONS <= num_stations <= MAX_STATIONS):
        raise ValueError(f"Liczba stacji musi być między {MIN_STATIONS} a {MAX_STATIONS}")

    if not (MIN_CUSTOMERS <= num_customers <= MAX_CUSTOMERS):
        raise ValueError(f"Liczba klientów musi być między {MIN_CUSTOMERS} a {MAX_CUSTOMERS}")

    if len(service_rates) != num_stations:
        raise ValueError(f"Długość service_rates ({len(service_rates)}) musi równać się liczbie stacji ({num_stations})")

    if len(num_servers) != num_stations:
        raise ValueError(f"Długość num_servers ({len(num_servers)}) musi równać się liczbie stacji ({num_stations})")

    for i, rate in enumerate(service_rates):
        if not (MIN_SERVICE_RATE <= rate <= MAX_SERVICE_RATE):
            raise ValueError(f"Service rate dla stacji {i} musi być między {MIN_SERVICE_RATE} a {MAX_SERVICE_RATE}")

    for i, servers in enumerate(num_servers):
        if not (MIN_SERVERS <= servers <= MAX_SERVERS):
            raise ValueError(f"Liczba serwerów dla stacji {i} musi być między {MIN_SERVERS} a {MAX_SERVERS}")


def validate_firefly_params(n_fireflies, max_iterations, alpha, beta_0, gamma):
    """
    Waliduje parametry algorytmu Firefly.

    Args:
        n_fireflies: Liczba świetlików
        max_iterations: Liczba iteracji
        alpha: Parametr losowości
        beta_0: Atrakcyjność bazowa
        gamma: Współczynnik absorpcji

    Raises:
        ValueError: Jeśli parametry są nieprawidłowe
    """
    if not (MIN_FIREFLIES <= n_fireflies <= MAX_FIREFLIES):
        raise ValueError(f"Liczba świetlików musi być między {MIN_FIREFLIES} a {MAX_FIREFLIES}")

    if not (MIN_ITERATIONS <= max_iterations <= MAX_ITERATIONS):
        raise ValueError(f"Liczba iteracji musi być między {MIN_ITERATIONS} a {MAX_ITERATIONS}")

    if not (0 <= alpha <= 1):
        raise ValueError("Alpha musi być między 0 a 1")

    if not (0 <= beta_0 <= 2):
        raise ValueError("Beta_0 musi być między 0 a 2")

    if not (0 <= gamma <= 10):
        raise ValueError("Gamma musi być między 0 a 10")
