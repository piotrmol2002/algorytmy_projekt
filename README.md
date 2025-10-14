# 🔥 Firefly Queueing Optimizer

**Aplikacja do optymalizacji zamkniętych systemów kolejkowych algorytmem świetlika (Firefly Algorithm)**

---

## 📋 Spis treści

- [Opis projektu](#opis-projektu)
- [Czym jest algorytm Firefly?](#czym-jest-algorytm-firefly)
- [Czym są zamknięte systemy kolejkowe?](#czym-są-zamknięte-systemy-kolejkowe)
- [Instalacja](#instalacja)
- [Uruchomienie](#uruchomienie)
- [Użycie przez interfejs webowy](#użycie-przez-interfejs-webowy)
- [Użycie przez kod Python](#użycie-przez-kod-python)
- [Struktura projektu](#struktura-projektu)
- [Funkcje celu](#funkcje-celu)
- [Parametry algorytmu](#parametry-algorytmu)

---

## 🎯 Opis projektu

Ten projekt pozwala **optymalizować systemy kolejkowe** (np. systemy komputerowe, sieci serwerów) używając **algorytmu świetlika (Firefly Algorithm)**.

**Co możesz zrobić:**
- ✅ Zdefiniować własną sieć kolejkową (liczba stacji, klientów, parametry)
- ✅ Wybrać funkcję celu (co chcesz optymalizować: czas, kolejki, etc.)
- ✅ Uruchomić optymalizację algorytmem Firefly
- ✅ Zobaczyć wyniki PRZED i PO optymalizacji
- ✅ Wykresy porównujące wydajność

### ✨ Co zostało zaimplementowane:

**Backend (Python Flask):**
- ✅ Pełna implementacja algorytmu Firefly z parametrami (α, β₀, γ)
- ✅ Solver MVA (Mean Value Analysis) dla dokładnej analizy systemów kolejkowych
- ✅ 5 funkcji celu do wyboru (czas odpowiedzi, kolejki, wykorzystanie, przepustowość)
- ✅ REST API z endpointami `/optimize` i `/api/objectives`
- ✅ Automatyczne generowanie wykresów porównawczych (matplotlib)
- ✅ Obliczanie metryk: czas odpowiedzi, długość kolejek, wykorzystanie serwerów, przepustowość

**Frontend (React + nginx):**
- ✅ Intuicyjny interfejs webowy do konfiguracji systemu
- ✅ Dynamiczna konfiguracja stacji (tempo obsługi, liczba serwerów)
- ✅ Wybór funkcji celu z listy rozwijanej
- ✅ Wyświetlanie charakterystyk początkowych systemu
- ✅ Porównanie "przed vs po" w 3 zakładkach (Podsumowanie, Metryki, Wykresy)
- ✅ Koszt optymalizacji (zmiana wartości funkcji celu)
- ✅ 4 wykresy porównawcze: zbieżność, metryki, kolejki, wykorzystanie

**Deployment:**
- ✅ Pełna konteneryzacja Docker (backend + frontend)
- ✅ Docker Compose do orkiestracji
- ✅ nginx jako reverse proxy i serwer statyczny
- ✅ Izolowana sieć Docker dla komunikacji między kontenerami

**Dokumentacja:**
- ✅ Szczegółowy README z instrukcjami instalacji i uruchomienia
- ✅ Wyjaśnienia algorytmu Firefly i systemów kolejkowych
- ✅ Przykłady użycia przez API i kod Python
- ✅ QUICKSTART.md z szybkim startem

---

## 🐛 Czym jest algorytm Firefly?

**Firefly Algorithm (FA)** to metaheurystyczny algorytm optymalizacyjny inspirowany zachowaniem świetlików:

### Jak działają świetliki w naturze?
1. Świetliki świecą, aby przyciągać partnerów
2. Im jaśniejszy świetlik, tym bardziej atrakcyjny
3. Świetlik porusza się w stronę jaśniejszego świetlika
4. Intensywność światła maleje z odległością

### Jak to działa w optymalizacji?
- **Świetlik** = jedno rozwiązanie (np. konfiguracja serwerów [3, 2, 4])
- **Jasność** = jakość rozwiązania (im lepsza wartość funkcji celu, tym jaśniejszy)
- **Ruch** = modyfikacja rozwiązania (zmiana parametrów)
- **Najlepszy świetlik** = optimum (najlepsza znaleziona konfiguracja)

**Formuła ruchu:**
```
x_i^new = x_i + β(r)·(x_j - x_i) + α·(rand - 0.5)
```
gdzie:
- `β(r) = β₀ · e^(-γ · r²)` - atrakcyjność malejąca z odległością
- `α` - parametr losowości (eksploracja)

---

## 🚦 Czym są zamknięte systemy kolejkowe?

**Closed Queueing Network** to model, gdzie:
- **Stała liczba klientów** krąży w systemie (N)
- Brak zewnętrznych przyjazdów/opuszczeń
- Klienci przechodzą między stacjami obsługi

### Przykład z życia:
System komputerowy z 3 procesorami:
- 20 zadań krąży między procesorami
- Po zakończeniu na CPU1, zadanie idzie do CPU2 lub CPU3
- System zawsze ma dokładnie 20 zadań

### Co optymalizujemy?
- 🔧 **Liczba serwerów** na każdej stacji (np. rdzeni procesora)
- ⚡ **Service rates** (szybkość obsługi)
- 🔀 **Routing** (jak rozdzielać zadania między stacje)

### Solver MVA (Mean Value Analysis):
Używamy **dokładnej metody analitycznej** do obliczania:
- Średniego czasu odpowiedzi
- Długości kolejek
- Wykorzystania serwerów
- Przepustowości

---

## 📦 Instalacja

### Opcja 1: Docker (ZALECANE)

#### Instalacja Dockera

**Windows:**
1. Pobierz Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Uruchom instalator i postępuj zgodnie z instrukcjami
3. Po instalacji uruchom Docker Desktop
4. Sprawdź: `docker --version` i `docker-compose --version`

**Linux (Ubuntu/Debian):**
```bash
# Aktualizacja pakietów
sudo apt-get update

# Instalacja Docker
sudo apt-get install ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Sprawdzenie
docker --version
docker compose version
```

**macOS:**
1. Pobierz Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Otwórz plik `.dmg` i przeciągnij Docker do Applications
3. Uruchom Docker Desktop
4. Sprawdź: `docker --version` i `docker-compose --version`

### Opcja 2: Instalacja lokalna

**Wymagania:**
- Python 3.11 lub nowszy
- pip

**Krok 1: Sklonuj projekt**
```bash
git clone https://github.com/piotrmol2002/algorytmy_projekt.git
cd algorytmy_projekt
```

**Krok 2: Zainstaluj zależności**
```bash
pip install -r requirements.txt
```

Instalowane biblioteki:
- `flask` - framework webowy
- `flask-cors` - Cross-Origin Resource Sharing
- `numpy` - obliczenia numeryczne
- `scipy` - narzędzia naukowe
- `matplotlib` - wykresy
- `plotly` - interaktywne wykresy
- `pandas` - analiza danych

---

## 🚀 Uruchomienie

### Opcja 1: Docker (ZALECANE)

```bash
# Uruchom kontenery
docker-compose up -d --build

# Otwórz w przeglądarce
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000

# Sprawdź logi (opcjonalnie)
docker logs firefly-backend
docker logs firefly-frontend

# Zatrzymaj kontenery
docker-compose down
```

### Opcja 2: Uruchomienie lokalne

**Backend:**
```bash
python app.py
```

**Frontend:** (w nowym terminalu)
```bash
cd frontend-simple
python -m http.server 3000
```

Następnie otwórz przeglądarkę:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Opcja 3: Prosty przykład w konsoli

```bash
python examples/simple_example.py
```

---

## 🌐 Użycie przez interfejs webowy

### Krok 1: Zdefiniuj sieć
- **Liczba stacji (K)**: Ile stacji obsługi (np. 3 procesory)
- **Liczba klientów (N)**: Ile zadań krąży w systemie (np. 20)

### Krok 2: Skonfiguruj stacje
Dla każdej stacji podaj:
- **Nazwa**: np. "Procesor 1", "Serwer Web"
- **Szybkość obsługi (μ)**: Ile zadań/s obsługuje 1 serwer (np. 5.0)
- **Liczba serwerów (początkowa)**: np. 2 (będzie optymalizowana)

### Krok 3: Wybierz funkcję celu
Co chcesz optymalizować?
- **Średni czas odpowiedzi** - minimalizuj czas oczekiwania
- **Średnia długość kolejki** - minimalizuj kolejki
- **Maksymalna długość kolejki** - unikaj wąskich gardeł
- **Równomierność obciążenia** - load balancing
- **Przepustowość** - maksymalizuj wydajność

### Krok 4: Parametry algorytmu
- **Liczba świetlików**: 20-30 (więcej = lepsza eksploracja)
- **Liczba iteracji**: 50-150 (więcej = lepsze wyniki)
- **Alpha (α)**: 0.5 (losowość)
- **Beta_0 (β₀)**: 1.0 (atrakcyjność)
- **Gamma (γ)**: 1.0 (absorpcja)

### Krok 5: Uruchom i zobacz wyniki!
- 📊 Porównanie PRZED vs PO
- 📈 Wykresy konwergencji
- 📉 Wizualizacje metryk

---

## 💻 Użycie przez kod Python

### Prosty przykład:

```python
from models.queueing_network import QueueingNetwork
from algorithms.optimizer import QueueingOptimizer

# 1. Utwórz sieć
network = QueueingNetwork(
    num_stations=3,              # 3 stacje
    num_customers=20,            # 20 klientów
    service_rates=[5, 3, 4],     # Szybkości obsługi
    num_servers=[2, 2, 2],       # Początkowa liczba serwerów
    station_names=['CPU1', 'CPU2', 'CPU3']
)

# 2. Utwórz optimizer
optimizer = QueueingOptimizer(
    network=network,
    objective='mean_response_time',  # Minimalizuj czas
    optimize_vars=['num_servers'],   # Optymalizuj liczbę serwerów
    server_bounds=(1, 6),            # 1-6 serwerów
    firefly_params={
        'n_fireflies': 20,
        'max_iterations': 50
    }
)

# 3. Uruchom optymalizację
results = optimizer.optimize()

# 4. Wyświetl wyniki
print(f"PRZED: {results['baseline']['metrics']['mean_response_time']:.4f} s")
print(f"PO: {results['optimized']['metrics']['mean_response_time']:.4f} s")
print(f"Poprawa: {results['improvement']['percent']:.2f}%")
```

---

## 📁 Struktura projektu

```
Firefly/
│
├── app.py                          # Główna aplikacja Flask
├── requirements.txt                # Zależności
├── README.md                       # Ten plik
│
├── models/                         # Modele matematyczne
│   ├── queueing_network.py        # Sieć kolejkowa
│   └── objective_functions.py     # Funkcje celu
│
├── algorithms/                     # Algorytmy optymalizacyjne
│   ├── firefly.py                 # Algorytm Firefly
│   └── optimizer.py               # Wrapper optymalizacji
│
├── simulation/                     # Solwery
│   └── mva_solver.py              # Mean Value Analysis
│
├── visualization/                  # Wizualizacje
│   └── plots.py                   # Generowanie wykresów
│
├── web/                           # Interfejs webowy
│   ├── templates/
│   │   └── index.html             # Główna strona
│   └── static/                    # CSS, JS
│
└── examples/                      # Przykłady użycia
    └── simple_example.py          # Prosty przykład
```

---

## 🎯 Funkcje celu

### 1. Średni czas odpowiedzi
```python
objective='mean_response_time'
```
Minimalizuj średni czas, jaki klient spędza w systemie.

### 2. Średnia długość kolejki
```python
objective='mean_queue_length'
```
Minimalizuj średnią liczbę klientów czekających.

### 3. Maksymalna długość kolejki
```python
objective='max_queue_length'
```
Minimalizuj największą kolejkę (unikaj wąskich gardeł).

### 4. Równomierność obciążenia
```python
objective='utilization_variance'
```
Minimalizuj różnice w wykorzystaniu serwerów (load balancing).

### 5. Przepustowość
```python
objective='throughput'
```
Maksymalizuj liczbę zadań przetwarzanych na jednostkę czasu.

---

## ⚙️ Parametry algorytmu

### Liczba świetlików (n_fireflies)
- **Zakres**: 10-100
- **Rekomendacja**: 20-30
- **Efekt**: Więcej = lepsza eksploracja przestrzeni, ale wolniej

### Liczba iteracji (max_iterations)
- **Zakres**: 10-500
- **Rekomendacja**: 50-150
- **Efekt**: Więcej = lepsze wyniki, ale dłużej

### Alpha (α) - Losowość
- **Zakres**: 0-1
- **Rekomendacja**: 0.5
- **Efekt**: Wyższy = więcej eksploracji, niższy = szybsza zbieżność

### Beta_0 (β₀) - Atrakcyjność
- **Zakres**: 0-2
- **Rekomendacja**: 1.0
- **Efekt**: Kontroluje siłę przyciągania między świetlikami

### Gamma (γ) - Absorpcja
- **Zakres**: 0-5
- **Rekomendacja**: 1.0
- **Efekt**: Kontroluje jak szybko maleje światło z odległością

---

## 📊 Interpretacja wyników

### Przed optymalizacją (Baseline)
- Początkowa konfiguracja sieci
- Metryki wydajności bez optymalizacji

### Po optymalizacji (Optimized)
- Znaleziona optymalna konfiguracja
- Poprawione metryki wydajności

### Poprawa (Improvement)
- Procentowa i bezwzględna poprawa funkcji celu
- Dodatni % = lepsze wyniki

### Wykresy:
1. **Konwergencja** - jak szybko algorytm znalazł optimum
2. **Porównanie metryk** - przed vs po dla wszystkich metryk
3. **Długości kolejek** - kolejki na każdej stacji
4. **Wykorzystanie serwerów** - utilization na każdej stacji

---

## 🎓 Zastosowania praktyczne

1. **Systemy komputerowe**: Optymalizacja liczby rdzeni procesora
2. **Sieci serwerów**: Alokacja zasobów w data center
3. **Call center**: Rozmieszczenie operatorów
4. **Systemy produkcyjne**: Optymalizacja stacji montażowych
5. **Sieci telekomunikacyjne**: Routing i przełączanie

---

## 📝 Autorzy

Projekt grupy Algorytmy - optymalizacja systemów kolejkowych.

---

## 🔗 Dokumentacja algorytmu Firefly

- Xin-She Yang (2008). "Nature-Inspired Metaheuristic Algorithms"
- Xin-She Yang (2010). "Firefly Algorithm, Stochastic Test Functions and Design Optimisation"

---

## ⚠️ Uwagi

- Solver MVA działa dokładnie dla sieci zamkniętych
- Dla bardzo dużych sieci (>10 stacji, >100 klientów) obliczenia mogą trwać dłużej
- Parametry algorytmu można dostosować w zależności od problemu

---

## ✅ TODO dla rozszerzeń

- [ ] Support dla optymalizacji macierzy routingu
- [ ] Eksport wyników do CSV/Excel
- [ ] Porównanie z innymi algorytmami (PSO, GA)
- [ ] Więcej funkcji celu wielokryterialnych
- [ ] Wsparcie dla sieci otwartych

---

**Powodzenia w optymalizacji!** 🔥
