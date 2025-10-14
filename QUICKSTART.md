# 🚀 QUICKSTART - Szybki start

**Uruchom aplikację Firefly Optimizer w 3 prostych krokach!**

---

## ⚡ Opcja 1: Docker (REKOMENDOWANE)

### Wymagania:
- Docker Desktop zainstalowany ([pobierz tutaj](https://www.docker.com/products/docker-desktop))

### Uruchomienie:

```bash
# 1. Przejdź do katalogu projektu
cd C:\Users\HP\Desktop\AT\Algorytmy\Firefly

# 2. Uruchom Docker Compose
docker-compose up --build
```

### Gotowe! 🎉
Otwórz przeglądarkę: **http://localhost:5000**

### Zatrzymanie:
```bash
docker-compose down
```

---

## 💻 Opcja 2: Uruchomienie lokalne (bez Dockera)

### Wymagania:
- Python 3.8+ zainstalowany
- pip

### Krok 1: Zainstaluj zależności
```bash
cd C:\Users\HP\Desktop\AT\Algorytmy\Firefly
pip install -r requirements.txt
```

### Krok 2: Uruchom aplikację
```bash
python app.py
```

### Gotowe! 🎉
Otwórz przeglądarkę: **http://localhost:5000**

### Zatrzymanie:
Naciśnij `Ctrl+C` w terminalu

---

## 📝 Szybki test - Prosty przykład

Zamiast interfejsu webowego możesz uruchomić prosty przykład:

```bash
python examples/simple_example.py
```

To uruchomi optymalizację przykładowego systemu 3 procesorów i wyświetli wyniki w konsoli.

---

## 🎯 Pierwsze kroki w aplikacji webowej

1. **Zdefiniuj sieć**
   - Liczba stacji: np. 3
   - Liczba klientów: np. 20
   - Kliknij "Generuj konfigurację stacji"

2. **Skonfiguruj stacje**
   - Dla każdej stacji podaj szybkość obsługi (np. 5.0 zadań/s)
   - Ustaw początkową liczbę serwerów (np. 2)

3. **Wybierz funkcję celu**
   - Np. "Średni czas odpowiedzi"

4. **Ustaw parametry algorytmu**
   - Liczba świetlików: 25
   - Liczba iteracji: 100
   - Pozostaw domyślne wartości α, β₀, γ

5. **Kliknij "Uruchom optymalizację"**
   - Poczekaj ~30-60 sekund
   - Zobacz wyniki i wykresy!

---

## 🐛 Rozwiązywanie problemów

### Port 5000 zajęty
Zmień port w `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Zmień na 8080
```

### Błąd instalacji numpy/scipy (Windows)
Zainstaluj Visual C++ Build Tools:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

Lub użyj Docker (łatwiej!)

### Docker nie działa
Upewnij się, że Docker Desktop jest uruchomiony i działa.

---

## 📚 Dalsze kroki

Po uruchomieniu aplikacji przeczytaj pełną dokumentację w **README.md**:
- Szczegóły algorytmu Firefly
- Opis funkcji celu
- Zaawansowane parametry
- Użycie przez kod Python

---

## 🆘 Pomoc

Jeśli coś nie działa:
1. Sprawdź czy wszystkie zależności są zainstalowane
2. Sprawdź logi w terminalu
3. Spróbuj użyć Dockera zamiast lokalnej instalacji

---

**Powodzenia!** 🔥
