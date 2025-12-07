# Podział zadań - Projekt Firefly (część 2)
## Algorytm optymalizacji zamkniętych sieci kolejkowych

---

## PROGRAMIŚCI (implementacja)

### Programista 2: Kamil Piątek

1. **Implementacja 10. funkcji celu - wzór 4-208 (z `docs/wzor-4-208.png`):**
   ```
   f(m) = c₁·m + (c₂/(1+ρ))·[ρN + Σ(j=m+1 to N) C'ⱼ·(j!ρʲ)/(m!m!^(j-m)) / (Σ(j=0 to m) C'ⱼρʲ + Σ(j=m to N) C'ⱼ·(j!ρʲ)/(m!m!^(j-m)))]
   ```
   - Dodać nową funkcję w `models/objective_functions.py`
   - Nazwa funkcji: `erlang_cost_function` lub podobna
   - Dodać do `OBJECTIVE_CATALOG`
   - Dodać UI dla tej funkcji
   - Dodać wykresy porównawcze

2. **Dodanie obliczeń P₀ i P do WSZYSTKICH 9 funkcji celu:**
   - P₀ = prawdopodobieństwo, że system jest pusty
   - P = prawdopodobieństwo odrzucenia zgłoszenia
   - Implementacja w `mva_solver.py` - dodać do zwracanych metryk
   - Upewnić się, że są obliczane przy każdej optymalizacji/funkcji celu

3. **Dodanie średniej ilości zgłoszeń oczekujących w kolejce:**
   - Dla każdej funkcji celu obliczać Lq (queue length bez obsługiwanych)
   - Dodać do metryk w `mva_solver.py`

4. **Dodanie średniej ilości zajętych kanałów:**
   - Dla każdej funkcji celu obliczać liczbę aktywnie obsługujących serwerów
   - Dodać do metryk w `mva_solver.py`

5. **Nowe metryki również mają być wyświetlane w UI**

---

### Programista 3: Filip Wojtasiński

1. **Dodanie bezwzględnej zdolności obsługi systemu:**
   - Dla każdej funkcji celu obliczać A (absolute service capacity)
   - Dodać do metryk w `mva_solver.py`

2. **Dodanie średniej ilości zgłoszeń w systemie:**
   - Dla każdej funkcji celu obliczać L (total number in system)
   - Dodać do metryk w `mva_solver.py`

3. **Dodanie średniego czasu przebywania zgłoszeń w systemie:**
   - Dla każdej funkcji celu obliczać W (waiting time in system)
   - Dodać do metryk w `mva_solver.py`

4. **Dodanie średniego czasu przebywania zgłoszeń w kolejce:**
   - Dla każdej funkcji celu obliczać Wq (waiting time in queue only)
   - Dodać do metryk w `mva_solver.py`

5. **Nowe metryki również mają być wyświetlane w UI**
---

## DOKUMENTACJA

### Dok 1: Tamara Fyl

1. **Opracowanie przykładów dla funkcji celu: mean_response_time, throughput**
   - Na wzór istniejącego przykładu (sekcja 3.3 i 3.4)
   - Opis problemu dla każdej funkcji
   - Dane wejściowe
   - Tabela porównawcza przed/po
   - Podsumowanie wyników z interpretacją
   - Wnioski z przykładu

2. **Badanie optymalnych parametrów algorytmu Firefly dla funkcji: mean_response_time, throughput**
   - α (alfa) - losowość operacji
   - β₀ (beta0) - siła przyciągania
   - γ (gamma) - spadek atrakcyjności z odległością
   - Liczba świetlików
   - Liczba iteracji
   - Stwórz tabelę z wynikami testów dla różnych wartości parametrów
   - Badanie należy przeprowadzić z wykorzystaniem naszego programu

---

### Dok 2: Patryk Filipak

1. **Aktualizacja legendy symboli - dodać:**
   - P₀ - prawdopodobieństwo, że system jest pusty
   - P - prawdopodobieństwo odrzucenia zgłoszenia
   - Lq - średnia ilość zgłoszeń oczekujących w kolejce
   - A - bezwzględna zdolność obsługi systemu
   - W - średni czas przebywania zgłoszeń w systemie
   - Wq - średni czas przebywania zgłoszeń w kolejce
   - α - losowość operacji (parametr Firefly)
   - β₀ - siła przyciągania (parametr Firefly)
   - γ - spadek atrakcyjności z odległością (parametr Firefly)

2. **Opracowanie przykładów dla funkcji celu: mean_queue_length, max_queue_length**
   - Analogicznie jak Dok 1 (wyżej)
   - Opis problemu, dane, tabela, interpretacja, wnioski

3. **Badanie optymalnych parametrów algorytmu Firefly dla funkcji: mean_queue_length, max_queue_length**
   - Analogicznie jak Dok 1 (wyżej)

---

### Dok 3: Maksym Kobzar

1. **Opracowanie teoretyczne: 10. funkcja celu (wzór 4-208) (dodać do tabeli w 2.4)**
   - Nazwa, cel, opis

2. **Aktualizacja opracowania teoretycznego wszystkich funkcji celu (dodać punkt 2.6)**
   - Opisz matematyczne wzory wszystkich 10 funkcji celu

3. **Opracowanie przykładów dla funkcji celu: response_time_percentile, utilization_variance**
   - Analogicznie jak Dok 1 (wyżej)
   - Opis problemu, dane, tabela, interpretacja, wnioski

4. **Badanie optymalnych parametrów algorytmu Firefly dla funkcji: response_time_percentile, utilization_variance**
   - Analogicznie jak Dok 1 (wyżej)

5. **Weryfikacja wzoru 4-208 na przykładzie z książki (str. 95-98 PDF z Discorda)**
   - Wziąć wzór 4-208 jako funkcję celu
   - Sprawdzić czy wyjdzie tak samo jak w przykładzie z książki
   - Opracować w punkcie z opracowaniem przykładów
   - Wykorzystać do tego nasz program

---

### Dok 4: Daniel Kiermasz

1. **Opracowanie przykładów dla funkcji celu: profit, weighted_objective**
   - Analogicznie jak Dok 1 (wyżej)
   - Opis problemu, dane, tabela, interpretacja, wnioski

2. **Badanie optymalnych parametrów algorytmu Firefly dla funkcji: profit, weighted_objective**
   - Analogicznie jak Dok 1 (wyżej)

3. **Zaktualizowanie zestawienia wszystkich wzorów użytych w projekcie**
   - Zaktualizować zestawienie:
     - Wzory MVA (sredni czas przebvywania zgloszen w styustemie oraz sredni czas przebywania zgloszen w kolejce)
     - Dziesiątą funkcję celu (2.4)
     - Wzory algorytmu Firefly (dodać nowy podpunkt w punkcie 2)
     - Wzory metryk (P₀, P, Lq, A, W, Wq, etc.) (pod legendą symboli (2.5) lub dodac w tabeli 4-tą kolumnę)

---

### Dok 5: Illona Hrabovenko

1. **Opracowanie przykładów dla funkcji celu: weighted_multi_objective, erlang_cost_function (wzór 4-208)**
   - Analogicznie jak Dok 1
   - Opis problemu, dane, tabela, interpretacja, wnioski
   - Dla erlang_cost_function może być inny problem niż dla pozostałych

2. **Badanie optymalnych parametrów algorytmu Firefly dla funkcji: weighted_multi_objective, erlang_cost_function**
   - Analogicznie jak Dok 1

3. **Dodanie wniosków końcowych (punkt 6)**
   - Uwzględnić wszystkie 10 funkcji celu
   - Uwzględnić dotychczasowe i nowe metryki (P₀, P, Lq, A, W, Wq itp.)
   - Podsumować wyniki badań parametrów Firefly (wnioski)

---

**Link do dokumentacji:** https://docs.google.com/document/d/12qaPAiPSV-BlppgIuTLx2yaaS67Jcr4JcxJ9BlUAhNY/edit?tab=t.0

**Link do github:** https://github.com/piotrmol2002/algorytmy_projekt
