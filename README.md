# Firefly Optimizer - Optymalizacja systemow kolejkowych

Aplikacja do optymalizacji zamknietych systemow kolejkowych algorytmem Firefly.

## Wymagania

- Docker + Docker Compose
- Python 3.11+ (dla uruchomienia lokalnego)
- Node.js 18+ (dla frontendu)

## Szybki start (Docker)

```bash
# 1. Sklonuj repozytorium
git clone https://github.com/piotrmol2002/algorytmy_projekt.git
cd Firefly

# 2. Zbuduj i uruchom kontenery
docker-compose up --build -d

# 3. Otworz przegladarke
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
```

## Uruchomienie lokalne (bez Dockera)

### Backend
```bash
# 1. Zainstaluj zaleznosci
pip install -r requirements.txt

# 2. Uruchom backend
python app.py

# Backend dostepny: http://localhost:5000
```

### Frontend
```bash
# 1. Przejdz do folderu frontend
cd frontend

# 2. Zainstaluj zaleznosci
npm install

# 3. Uruchom frontend
npm start

# Frontend dostepny: http://localhost:3000
```

## Przydatne komendy Docker

```bash
# Budowanie i uruchamianie
docker-compose up --build -d      # Zbuduj i uruchom w tle
docker-compose up                 # Uruchom z logami
docker-compose down               # Zatrzymaj kontenery

# Logi
docker logs firefly-backend       # Logi backendu
docker logs firefly-frontend      # Logi frontendu
docker logs -f firefly-backend    # Logi na zywo

# Status
docker ps                         # Lista uruchomionych kontenerow
docker-compose ps                 # Status uslug

# Restart
docker-compose restart            # Restart wszystkich
docker-compose restart backend    # Restart tylko backendu

# Czyszczenie
docker-compose down -v            # Zatrzymaj + usun volumeny
docker system prune -f            # Usun nieuzywane obrazy/kontenery
```

## Przyklady uzycia (CLI)

```bash
# Generowanie raportow do sprawozdania
python examples/report_generator.py

# Przyklad systemu terminalowego
python examples/terminal_system.py

# Prosty przyklad
python examples/simple_example.py
```

## Struktura projektu

```
Firefly/
  app.py                    # Backend Flask
  models/                   # Modele danych
    queueing_network.py     # Model sieci kolejkowej
    objective_functions.py  # Funkcje celu
  algorithms/               # Algorytmy
    firefly.py              # Algorytm Firefly
    optimizer.py            # Optimizer laczacy wszystko
  simulation/               # Symulacja
    mva_solver.py           # Mean Value Analysis
  visualization/            # Wizualizacje
    plots.py                # Generowanie wykresow
  examples/                 # Przyklady
  frontend/                 # Frontend React
  reports/                  # Wygenerowane raporty
  docker-compose.yml        # Konfiguracja Docker
  requirements.txt          # Zaleznosci Python
```

## Funkcje celu

Aplikacja oferuje 9 różnych funkcji celu, które można wybrać do optymalizacji. Każda z nich koncentruje się na innym aspekcie wydajności systemu.

| Nazwa funkcji celu | Cel | Opis |
| :--- | :--- | :--- |
| **Średni czas odpowiedzi** | MINIMALIZACJA | Minimalizuje średni czas, jaki zadanie spędza w całym systemie (oczekiwanie + obsługa). |
| **Średnia długość kolejki** | MINIMALIZACJA | Minimalizuje średnią liczbę zadań oczekujących w kolejkach we wszystkich stacjach. |
| **Maksymalna długość kolejki**| MINIMALIZACJA | Skupia się na redukcji najdłuższej kolejki w systemie, co pomaga eliminować "wąskie gardła". |
| **Równomierność obciążenia** | MINIMALIZACJA | Dąży do równego rozłożenia pracy na wszystkie serwery poprzez minimalizację wariancji ich wykorzystania. |
| **95-percentyl czasu odpowiedzi**| MINIMALIZACJA | Minimalizuje czas, którego 95% zadań nie przekracza. Chroni to przed skrajnie długimi czasami oczekiwania. |
| **Przepustowość systemu** | MAKSYMALIZACJA | Maksymalizuje liczbę zadań, które system jest w stanie przetworzyć w jednostce czasu. |
| **Zysk ekonomiczny** | MAKSYMALIZACJA | Maksymalizuje zysk obliczony na podstawie przychodów, kosztów obsługi i kosztów utrzymania zadań w systemie. |
| **Kompromisowa wielokryterialna**| MAKSYMALIZACJA | Umożliwia jednoczesną optymalizację czasu odpowiedzi, przepustowości i długości kolejki (`w1*(-R) + w2*X + w3*(-L)`). |
| **Generyczna funkcja ważona** | MINIMALIZACJA | Pozwala na zdefiniowanie własnej, ważonej kombinacji wielu kryteriów (np. czasu odpowiedzi, wariancji obciążenia). |


## Troubleshooting

```bash
# Port zajety
docker-compose down
lsof -i :5000  # lub :3000

# Jesli blad budowania (sprobuj bez cache zbudowac)
docker-compose build --no-cache

# Reset calkowity
docker-compose down -v
docker system prune -af
docker-compose up --build -d
```
