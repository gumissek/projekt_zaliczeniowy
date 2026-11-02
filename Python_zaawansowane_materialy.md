# Zaawansowane techniki programowania w języku Python

**Kierunek:** Informatyka (inż.)  
**Forma zaliczenia:** Praca zaliczeniowa (projekt) z ćwiczeń laboratoryjnych  
**Opracował:** Bartosz Bryniarski

> Wymagania: Python 3.12+ (przykłady testowane na CPython). Każdy przykład można zapisać do pliku `.py` i uruchomić poleceniem `python3 plik.py`.

---

## Spis treści

1. Tworzenie i zastosowanie dekoratorów dla funkcji
2. Tworzenie i zastosowanie dekoratorów dla metod
3. Omówienie iteratorów
4. Omówienie generatorów, wyrażeń generujących
5. Wyrażenia regularne
6. Praca z wieloma wątkami
7. Praca z wieloma procesami
8. Omówienie Global Interpreter Lock (GIL)
9. Projekt zaliczeniowy – wymagania, kryteria oceny, propozycje tematów

---

## 1. Tworzenie i zastosowanie dekoratorów dla funkcji

### Teoria

W Pythonie **funkcje są obiektami pierwszej klasy** – można je przypisywać do zmiennych, przekazywać jako argumenty i zwracać z innych funkcji. Funkcja zdefiniowana wewnątrz innej funkcji „pamięta” zmienne z otaczającego zakresu – to **domknięcie (closure)**.

**Dekorator** to funkcja, która przyjmuje funkcję i zwraca nową funkcję (zwykle „opakowanie” – *wrapper*), rozszerzając jej działanie bez modyfikowania kodu źródłowego.

Zapis ze znakiem `@`:

```python
@decorator
def function(): ...
```

jest dokładnie równoważny:

```python
def function(): ...
function = decorator(function)
```

Kluczowe elementy poprawnego dekoratora:

| Element | Po co? |
|---|---|
| `*args, **kwargs` | wrapper przyjmie dowolne argumenty dekorowanej funkcji |
| `return func(*args, **kwargs)` | zachowanie wartości zwracanej |
| `@functools.wraps(func)` | zachowanie nazwy, docstringu i metadanych oryginału |

Typowe zastosowania: logowanie, pomiar czasu, cache (memoizacja), kontrola uprawnień, walidacja argumentów, ponawianie operacji (*retry*).

### Przykład 1 – prosty dekorator mierzący czas

```python
import functools
import time

def measure_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[{func.__name__}] wykonano w {elapsed:.4f} s")
        return result
    return wrapper

@measure_time
def sum_of_squares(n):
    """Zwraca sumę kwadratów 0..n-1."""
    return sum(i * i for i in range(n))

print(sum_of_squares(1_000_000))
print(sum_of_squares.__name__, "-", sum_of_squares.__doc__)  # dzięki wraps
```

### Przykład 2 – dekorator z parametrami (trzy poziomy zagnieżdżenia)

Jeśli dekorator ma przyjmować argumenty, potrzebujemy **fabryki dekoratorów**: funkcja zewnętrzna przyjmuje parametry i zwraca właściwy dekorator.

```python
import functools
import random

def retry(attempts=3, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"Próba {attempt}/{attempts} nieudana: {e}")
            raise RuntimeError(f"{func.__name__}: wyczerpano limit prób")
        return wrapper
    return decorator

@retry(attempts=5, exceptions=(ConnectionError,))
def fetch_data():
    if random.random() < 0.7:
        raise ConnectionError("brak połączenia")
    return {"status": "ok"}

print(fetch_data())
```

### Przykład 3 – nakładanie dekoratorów i dekoratory wbudowane

```python
from functools import lru_cache

@measure_time          # wykonywany jako drugi (zewnętrzny)
@lru_cache(maxsize=None)  # wykonywany jako pierwszy (wewnętrzny)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(80))
```

Dekoratory nakładane są **od dołu do góry**: `fib = measure_time(lru_cache(...)(fib))`.

**Do zapamiętania:** zawsze używaj `functools.wraps`; dekorator z parametrami = funkcja zwracająca dekorator.

---

## 2. Tworzenie i zastosowanie dekoratorów dla metod

### Teoria

Metoda to funkcja zdefiniowana w klasie, której pierwszym argumentem jest instancja (`self`) lub klasa (`cls`). Dekorator funkcyjny z `*args, **kwargs` działa także na metodach – `self` po prostu trafia do `args[0]`. Jeśli dekorator ma korzystać ze stanu obiektu, warto jawnie przyjąć `self`.

**Wbudowane dekoratory metod:**

| Dekorator | Znaczenie |
|---|---|
| `@staticmethod` | metoda bez `self`/`cls` – zwykła funkcja w przestrzeni nazw klasy |
| `@classmethod` | pierwszy argument to klasa (`cls`) – np. alternatywne konstruktory |
| `@property` | metoda dostępna jak atrybut; z `.setter` pozwala walidować przypisanie |
| `@functools.cached_property` | właściwość liczona raz i zapamiętywana w instancji |
| `@abc.abstractmethod` | metoda, którą musi zaimplementować klasa pochodna |

**Dekorator jako klasa.** Obiekt z metodą `__call__` może być dekoratorem. Uwaga: przy dekorowaniu **metod** taki obiekt musi implementować protokół deskryptora (`__get__`), aby poprawnie związać `self` – dlatego dla metod zwykle prościej użyć dekoratora funkcyjnego.

### Przykład 1 – dekorator korzystający ze stanu obiektu

```python
import functools

def login_required(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.logged_in:
            raise PermissionError(f"{method.__name__}: użytkownik niezalogowany")
        return method(self, *args, **kwargs)
    return wrapper

def log_call(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        print(f"{type(self).__name__}.{method.__name__}{args}")
        return method(self, *args, **kwargs)
    return wrapper

class Account:
    def __init__(self, owner):
        self.owner = owner
        self.logged_in = False
        self._balance = 0

    def login(self):
        self.logged_in = True

    @log_call
    @login_required
    def deposit(self, amount):
        self._balance += amount

k = Account("Anna")
try:
    k.deposit(100)
except PermissionError as e:
    print("Błąd:", e)
k.login()
k.deposit(100)
```

### Przykład 2 – `property`, `classmethod`, `staticmethod`, `cached_property`

```python
from functools import cached_property
import math

class Circle:
    def __init__(self, r):
        self.r = r                    # wywoła setter

    @property
    def r(self):
        return self._r

    @r.setter
    def r(self, value):
        if value <= 0:
            raise ValueError("Promień musi być dodatni")
        self._r = value

    @property
    def area(self):                   # atrybut tylko do odczytu
        return math.pi * self._r ** 2

    @classmethod
    def from_circumference(cls, circumference):         # alternatywny konstruktor
        return cls(circumference / (2 * math.pi))

    @staticmethod
    def unit():
        return "cm"

    @cached_property
    def description(self):
        print("(liczę opis...)")
        return f"Okrąg r={self._r:.2f} {self.unit()}"

o = Circle.from_circumference(31.4159)
print(o.area, o.description, o.description)         # opis liczony tylko raz
```

### Przykład 3 – dekorator-klasa z deskryptorem (dla dociekliwych)

```python
import functools

class CallCounter:
    """Zlicza wywołania metody (osobny licznik dla całej klasy)."""
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return functools.partial(self.__call__, instance)  # wiąże self

class Service:
    @CallCounter
    def ping(self):
        return "pong"

s = Service()
s.ping(); s.ping()
print(Service.ping.calls)          # 2
```

**Do zapamiętania:** w dekoratorze metody pierwszym argumentem wrappera jest `self`; dekorator-klasa dla metod wymaga `__get__`.

---

## 3. Omówienie iteratorów

### Teoria

- **Obiekt iterowalny (iterable)** – obiekt, po którym można przejść pętlą `for`; ma metodę `__iter__()` zwracającą iterator (np. `list`, `str`, `dict`, `set`, `range`, plik).
- **Iterator** – obiekt pamiętający pozycję; ma metody `__iter__()` (zwraca `self`) i `__next__()` (zwraca kolejny element lub zgłasza `StopIteration`).

Funkcje wbudowane: `iter(obj)` wywołuje `obj.__iter__()`, `next(it)` wywołuje `it.__next__()`.

Pętla `for` „pod spodem”:

```python
for x in collection:
    print(x)

# jest równoważna:
it = iter(collection)
while True:
    try:
        x = next(it)
    except StopIteration:
        break
    print(x)
```

Cechy iteratorów:
- są **leniwe** – element wyliczany dopiero na żądanie,
- są **jednorazowe** – po wyczerpaniu nie da się ich „przewinąć”,
- mogą być **nieskończone** (np. `itertools.count()`).

Dobra praktyka: klasa-kolekcja (iterable) w `__iter__` zwraca **nowy** iterator, dzięki czemu można po niej iterować wielokrotnie.

### Przykład 1 – własny iterator

```python
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

for x in Countdown(5):
    print(x, end=" ")       # 5 4 3 2 1
print()

it = Countdown(2)
print(next(it), next(it))   # 2 1
# next(it)  -> StopIteration
```

### Przykład 2 – kolekcja wielokrotnego użytku (iterable + osobny iterator)

```python
class Playlist:
    def __init__(self, *tracks):
        self._tracks = list(tracks)

    def __iter__(self):
        return PlaylistIterator(self._tracks)

    def __len__(self):
        return len(self._tracks)

class PlaylistIterator:
    def __init__(self, tracks):
        self._tracks = tracks
        self._i = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._i >= len(self._tracks):
            raise StopIteration
        track = self._tracks[self._i]
        self._i += 1
        return track

p = Playlist("Intro", "Track 2", "Outro")
print(list(p))
print([u.upper() for u in p])   # działa ponownie
```

### Przykład 3 – narzędzia: `iter(callable, sentinel)` i `itertools`

```python
import itertools

# Czytanie pliku blokami do napotkania pustego bajtu
# with open("plik.bin", "rb") as f:
#     for block in iter(lambda: f.read(4096), b""):
#         process(block)

counter = itertools.count(start=10, step=5)            # nieskończony
print(list(itertools.islice(counter, 4)))              # [10, 15, 20, 25]
print(list(itertools.chain("AB", [1, 2])))              # ['A','B',1,2]
print(list(itertools.zip_longest("abc", [1], fillvalue="-")))
for key, group in itertools.groupby("aaabbc"):
    print(key, len(list(group)))
```

**Do zapamiętania:** iterable ma `__iter__`, iterator ma `__iter__` + `__next__`; koniec sygnalizuje `StopIteration`.

---

## 4. Omówienie generatorów, wyrażeń generujących

### Teoria

**Generator** to najprostszy sposób tworzenia iteratora. Jest to funkcja zawierająca słowo kluczowe `yield`. Wywołanie takiej funkcji **nie wykonuje** jej ciała – zwraca obiekt generatora. Każde `next()` uruchamia kod do najbliższego `yield`, zwraca wartość i **zawiesza** wykonanie, zachowując stan zmiennych lokalnych.

Porównanie z iteratorem z tematu 3 – ten sam efekt w 4 linijkach:

```python
def countdown(start):
    while start > 0:
        yield start
        start -= 1
```

**Wyrażenie generujące (generator expression)** – składnia jak list comprehension, ale w nawiasach okrągłych. Tworzy elementy leniwie, nie buduje listy w pamięci:

```python
squares_list = [x * x for x in range(10**6)]   # cała lista w RAM
squares_gen   = (x * x for x in range(10**6))   # obiekt ~200 B
total = sum(x * x for x in range(10**6))          # nawiasy można pominąć
```

Dodatkowe mechanizmy:
- `yield from iterowalny` – deleguje generowanie do innego generatora/kolekcji,
- `gen.send(value)` – przekazanie wartości **do** generatora (wynik wyrażenia `yield`),
- `return` w generatorze kończy iterację (`StopIteration`).

Zastosowania: przetwarzanie dużych plików linia po linii, strumienie danych, potoki (*pipelines*), sekwencje nieskończone.

### Przykład 1 – generator nieskończony i `islice`

```python
from itertools import islice

def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

print(list(islice(fibonacci(), 10)))   # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### Przykład 2 – potok przetwarzania logów (pipeline)

Każdy etap jest generatorem – dane przepływają element po elemencie, więc plik o rozmiarze kilku GB nie zostanie wczytany do pamięci.

```python
def read_lines(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")

def filter_lines(lines, phrase):
    return (l for l in lines if phrase in l)          # wyrażenie generujące

def parse(lines):
    for l in lines:
        date, level, *rest = l.split(" ", 2)
        yield {"date": date, "level": level, "msg": rest[0] if rest else ""}

# przygotowanie danych testowych
with open("app.log", "w", encoding="utf-8") as f:
    f.write("2026-10-01 INFO start\n2026-10-01 ERROR brak pliku\n"
            "2026-10-02 INFO ok\n2026-10-02 ERROR timeout\n")

pipeline = parse(filter_lines(read_lines("app.log"), "ERROR"))
for entry in pipeline:
    print(entry)
```

### Przykład 3 – `yield from`, porównanie pamięci, `send`

```python
import sys

def flatten(nested):
    for el in nested:
        if isinstance(el, list):
            yield from flatten(el)      # rekurencyjna delegacja
        else:
            yield el

print(list(flatten([1, [2, [3, 4]], 5])))  # [1, 2, 3, 4, 5]

print(sys.getsizeof([x for x in range(10**6)]))  # ok. 8 MB
print(sys.getsizeof((x for x in range(10**6))))  # ok. 200 B

def running_average():
    total = n = 0
    average = None
    while True:
        x = yield average
        total += x; n += 1
        average = total / n

g = running_average()
next(g)                 # "rozruch" generatora
print(g.send(10), g.send(20), g.send(30))   # 10.0 15.0 20.0
```

**Do zapamiętania:** `yield` zamienia funkcję w generator; `( ... for ... )` to leniwy odpowiednik list comprehension.

---

## 5. Wyrażenia regularne

### Teoria

Wyrażenie regularne (*regex*) to wzorzec opisujący zbiór napisów. W Pythonie obsługuje je moduł `re`. Wzorce zapisujemy jako **surowe napisy** `r"..."`, aby `\` nie był interpretowany przez Pythona.

**Najważniejsze elementy składni:**

| Symbol | Znaczenie | Symbol | Znaczenie |
|---|---|---|---|
| `.` | dowolny znak (poza `\n`) | `\d` / `\D` | cyfra / nie-cyfra |
| `^` / `$` | początek / koniec napisu | `\w` / `\W` | znak „słowny” / inny |
| `*` | 0 lub więcej | `\s` / `\S` | biały znak / inny |
| `+` | 1 lub więcej | `\b` | granica słowa |
| `?` | 0 lub 1 (lub tryb leniwy) | `[abc]`, `[a-z]` | klasa znaków |
| `{n}`, `{n,m}` | dokładnie n / od n do m | `[^abc]` | negacja klasy |
| `(...)` | grupa przechwytująca | `a\|b` | alternatywa |
| `(?P<name>...)` | grupa nazwana | `(?:...)` | grupa nieprzechwytująca |

**Funkcje modułu `re`:**

| Funkcja | Działanie |
|---|---|
| `re.match(p, s)` | dopasowanie od **początku** napisu |
| `re.fullmatch(p, s)` | dopasowanie **całego** napisu (walidacja) |
| `re.search(p, s)` | pierwsze wystąpienie w dowolnym miejscu |
| `re.findall(p, s)` | lista wszystkich dopasowań |
| `re.finditer(p, s)` | iterator obiektów `Match` |
| `re.sub(p, zamiana, s)` | zamiana dopasowań |
| `re.split(p, s)` | podział napisu wg wzorca |
| `re.compile(p, flagi)` | prekompilacja wzorca używanego wielokrotnie |

Flagi: `re.IGNORECASE` (`re.I`), `re.MULTILINE` (`re.M`), `re.DOTALL` (`re.S`), `re.VERBOSE` (`re.X` – komentarze we wzorcu).

**Zachłanność:** `.*` dopasowuje jak najwięcej, `.*?` – jak najmniej.

### Przykład 1 – walidacja i wyszukiwanie

```python
import re

def is_valid_email(s):
    return re.fullmatch(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", s) is not None

for e in ["jan.kowalski@uczelnia.edu.pl", "zly@", "a@b"]:
    print(e, is_valid_email(e))

text = "Tel: 501-234-567, biuro 71 345 67 89, kod 50-370 Wrocław"
print(re.findall(r"\b\d{3}-\d{3}-\d{3}\b", text))   # ['501-234-567']
print(re.findall(r"\b\d{2}-\d{3}\b", text))         # ['50-370']

postal_code = re.search(r"(\d{2})-(\d{3})", text)
print(postal_code.group(0), postal_code.group(1), postal_code.group(2), postal_code.span())
```

### Przykład 2 – parsowanie logów serwera WWW (grupy nazwane, `VERBOSE`)

```python
import re
from collections import Counter

LOG_PATTERN = re.compile(r"""
    (?P<ip>\d{1,3}(?:\.\d{1,3}){3})   # adres IP
    \s-\s-\s
    \[(?P<date>[^\]]+)\]              # data w nawiasach
    \s"(?P<method>GET|POST|PUT|DELETE)
    \s(?P<url>\S+)\s[^"]*"
    \s(?P<status>\d{3})
""", re.VERBOSE)

logs = """\
192.168.1.10 - - [03/Oct/2026:10:00:01 +0200] "GET /index.html HTTP/1.1" 200 512
10.0.0.5 - - [03/Oct/2026:10:00:02 +0200] "POST /login HTTP/1.1" 401 128
192.168.1.10 - - [03/Oct/2026:10:00:05 +0200] "GET /admin HTTP/1.1" 403 64
"""

status_codes = Counter()
for m in LOG_PATTERN.finditer(logs):
    d = m.groupdict()
    status_codes[d["status"]] += 1
    print(f'{d["ip"]:<15} {d["method"]:<5} {d["url"]:<12} {d["status"]}')
print(status_codes)
```

### Przykład 3 – `sub`, `split`, zachłanność

```python
import re

# Anonimizacja numerów PESEL (11 cyfr)
print(re.sub(r"\b(\d{2})\d{7}(\d{2})\b", r"\1*******\2", "PESEL: 90010112345"))

# Zamiana formatu daty z funkcją
print(re.sub(r"(\d{4})-(\d{2})-(\d{2})",
             lambda m: f"{m[3]}.{m[2]}.{m[1]}", "Termin: 2027-01-31"))

print(re.split(r"[;,\s]+", "a, b;c   d"))        # ['a', 'b', 'c', 'd']

html = "<b>pogrubiony</b> i <i>kursywa</i>"
print(re.findall(r"<.*>", html))    # zachłanne – jeden długi wynik
print(re.findall(r"<.*?>", html))   # leniwe – każdy znacznik osobno
```

**Do zapamiętania:** zawsze `r"..."`; `fullmatch` do walidacji, `search`/`finditer` do wyszukiwania; wzorce używane wielokrotnie – `re.compile`.

---

## 6. Praca z wieloma wątkami

### Teoria

**Wątek** to niezależna ścieżka wykonania w obrębie jednego procesu. Wątki **współdzielą pamięć** (zmienne globalne, obiekty), co ułatwia wymianę danych, ale rodzi ryzyko **wyścigu (race condition)**.

W CPython (ze standardowym GIL – temat 8) wątki **nie przyspieszają obliczeń CPU**, ale świetnie sprawdzają się w zadaniach **I/O-bound**: sieć, dysk, oczekiwanie na odpowiedź, bazy danych – w czasie czekania jednego wątku inne mogą pracować.

**Moduł `threading`:**

| Element | Opis |
|---|---|
| `Thread(target=f, args=(...))` | utworzenie wątku |
| `t.start()` / `t.join()` | uruchomienie / oczekiwanie na zakończenie |
| `daemon=True` | wątek kończony razem z programem |
| `Lock` / `RLock` | wzajemne wykluczanie (sekcja krytyczna) |
| `Event`, `Condition`, `Semaphore` | synchronizacja i sygnalizacja |
| `queue.Queue` | bezpieczna wątkowo kolejka (producent–konsument) |

**Wysokopoziomowo:** `concurrent.futures.ThreadPoolExecutor` – pula wątków, `submit()` zwraca `Future`, `map()` działa jak równoległe `map`.

### Przykład 1 – przyspieszenie zadań I/O

```python
import threading
import time
from concurrent.futures import ThreadPoolExecutor

def fetch(url):
    time.sleep(1)                 # symulacja oczekiwania na sieć
    return f"{url}: OK"

urls = [f"https://serwer{i}.example" for i in range(8)]

start = time.perf_counter()
results = [fetch(u) for u in urls]
print(f"Sekwencyjnie: {time.perf_counter() - start:.2f} s")   # ~8 s

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(fetch, urls))
print(f"Pula wątków:  {time.perf_counter() - start:.2f} s")   # ~1 s
print(results[:2])
```

### Przykład 2 – wyścig i `Lock`

```python
import threading

counter = 0
lock = threading.Lock()

def increment_unsafe(n):
    global counter
    for _ in range(n):
        tmp = counter       # odczyt
        tmp += 1            # modyfikacja
        counter = tmp       # zapis – w międzyczasie inny wątek mógł zmienić licznik

def increment_safe(n):
    global counter
    for _ in range(n):
        with lock:       # sekcja krytyczna
            counter += 1

for function in (increment_unsafe, increment_safe):
    counter = 0
    threads = [threading.Thread(target=function, args=(200_000,)) for _ in range(4)]
    for t in threads: t.start()
    for t in threads: t.join()
    print(f"{function.__name__}: {counter} (oczekiwano 800000)")
```

Wersja bez blokady często daje wynik mniejszy niż oczekiwany – utracone aktualizacje.

### Przykład 3 – producent–konsument z `queue.Queue`

```python
import queue
import threading
import time
import random

task_queue = queue.Queue(maxsize=5)
SENTINEL = None

def producer(n):
    for i in range(n):
        time.sleep(random.uniform(0.05, 0.2))
        task_queue.put(f"zadanie-{i}")
        print(f"[P] dodano zadanie-{i}")
    task_queue.put(SENTINEL)

def consumer():
    while (task := task_queue.get()) is not SENTINEL:
        print(f"    [K] przetwarzam {task}")
        time.sleep(0.15)
        task_queue.task_done()

tp = threading.Thread(target=producer, args=(6,))
tc = threading.Thread(target=consumer)
tp.start(); tc.start()
tp.join(); tc.join()
print("Gotowe")
```

**Do zapamiętania:** wątki = I/O; współdzielone dane chroń `Lock`-iem lub komunikuj się przez `Queue`.

---

## 7. Praca z wieloma procesami

### Teoria

**Proces** to niezależnie działający program z **własną przestrzenią pamięci** i **własnym interpreterem Pythona** (a więc własnym GIL). Dzięki temu procesy mogą faktycznie równolegle wykorzystywać wiele rdzeni CPU – to właściwe narzędzie dla zadań **CPU-bound** (obliczenia, kompresja, przetwarzanie obrazów, symulacje).

Koszty: tworzenie procesu jest wolniejsze niż wątku, a dane przekazywane między procesami muszą być **serializowane (pickle)** – przesyłanie dużych obiektów bywa kosztowne.

**Moduł `multiprocessing`:**

| Element | Opis |
|---|---|
| `Process(target=f, args=(...))` | utworzenie procesu |
| `Pool(n)` – `map`, `imap`, `starmap`, `apply_async` | pula procesów roboczych |
| `Queue`, `Pipe` | komunikacja między procesami |
| `Value`, `Array` | pamięć współdzielona (proste typy) |
| `Manager()` | współdzielone `dict`, `list` (przez proces-pośrednika) |
| `cpu_count()` | liczba rdzeni |

Wysokopoziomowo: `concurrent.futures.ProcessPoolExecutor` – ten sam interfejs co `ThreadPoolExecutor`, więc łatwo porównywać oba podejścia.

> **Ważne:** kod uruchamiający procesy musi być w bloku `if __name__ == "__main__":`. Na Windows i macOS (metoda startu *spawn*) moduł jest importowany ponownie w każdym procesie potomnym – bez tego zabezpieczenia program tworzyłby procesy w nieskończoność.

### Przykład 1 – zadanie CPU-bound: sekwencyjnie vs pula procesów

```python
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

def is_prime(n):
    if n < 2:
        return False
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            return False
    return True

def count_primes(interval):
    a, b = interval
    return sum(1 for n in range(a, b) if is_prime(n))

if __name__ == "__main__":
    N = 3_000_000
    k = cpu_count()
    step = N // k
    chunks = [(i * step, (i + 1) * step) for i in range(k)]

    start = time.perf_counter()
    result = count_primes((0, N))
    print(f"Sekwencyjnie: {result} liczb, {time.perf_counter() - start:.2f} s")

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=k) as pool:
        result = sum(pool.map(count_primes, chunks))
    print(f"{k} procesów:  {result} liczb, {time.perf_counter() - start:.2f} s")
```

### Przykład 2 – `Process` i komunikacja przez `Queue`

```python
from multiprocessing import Process, Queue, current_process
import os

def worker(tasks, results):
    while (n := tasks.get()) is not None:
        results.put((current_process().name, os.getpid(), n, n ** 2))

if __name__ == "__main__":
    tasks, results = Queue(), Queue()
    processes = [Process(target=worker, args=(tasks, results), name=f"P{i}")
               for i in range(3)]
    for p in processes: p.start()

    numbers = range(1, 10)
    for n in numbers: tasks.put(n)
    for _ in processes: tasks.put(None)      # sygnał końca dla każdego procesu

    for _ in numbers:
        print(results.get())
    for p in processes: p.join()
```

### Przykład 3 – pamięć współdzielona i `Pool.starmap`

```python
from multiprocessing import Pool, Value, Lock

def init(counter_, lock_):
    global counter, lock
    counter, lock = counter_, lock_

def power(base, exponent):
    with lock:
        counter.value += 1
    return base ** exponent

if __name__ == "__main__":
    counter = Value("i", 0)       # liczba całkowita w pamięci współdzielonej
    lock = Lock()
    with Pool(4, initializer=init, initargs=(counter, lock)) as pool:
        print(pool.starmap(power, [(2, 10), (3, 4), (5, 3), (10, 2)]))
    print("Liczba wywołań:", counter.value)
```

**Do zapamiętania:** procesy = CPU; zawsze `if __name__ == "__main__":`; komunikacja przez `Queue`/`Pipe`, a nie zmienne globalne.

---

## 8. Omówienie Global Interpreter Lock (GIL)

### Teoria

**GIL (Global Interpreter Lock)** to blokada w interpreterze **CPython**, która sprawia, że w danej chwili **tylko jeden wątek wykonuje kod bajtowy Pythona**, nawet na maszynie wielordzeniowej.

**Dlaczego istnieje?** CPython zarządza pamięcią przez **zliczanie referencji** – każdy obiekt ma licznik odwołań. Bez globalnej blokady każda zmiana licznika musiałaby być osobno synchronizowana. GIL upraszcza implementację interpretera i rozszerzeń w C oraz przyspiesza programy jednowątkowe.

**Kiedy GIL jest zwalniany?**
- przy operacjach wejścia/wyjścia (odczyt pliku, gniazda sieciowe, `time.sleep`),
- okresowo, co pewien interwał (`sys.getswitchinterval()`, domyślnie 5 ms) – interpreter przełącza wątki,
- w rozszerzeniach C, które go jawnie zwalniają (np. NumPy, `hashlib`, `zlib` przy dużych danych).

**Konsekwencje praktyczne:**

| Rodzaj zadania | Wątki (`threading`) | Procesy (`multiprocessing`) | `asyncio` |
|---|---|---|---|
| I/O-bound (sieć, dysk) | ✅ dobre przyspieszenie | ✅ działa, ale drożej | ✅ bardzo dobre |
| CPU-bound (obliczenia) | ❌ brak przyspieszenia, czasem wolniej | ✅ skaluje się na rdzenie | ❌ |
| Współdzielenie danych | łatwe (wspólna pamięć) | trudniejsze (pickle, Queue) | łatwe |

**GIL nie zwalnia z synchronizacji!** Operacja `counter += 1` składa się z kilku instrukcji kodu bajtowego, między którymi może nastąpić przełączenie wątku (por. przykład 2 z tematu 6).

**Python bez GIL (free-threading).** Od Pythona 3.13 dostępna jest eksperymentalna kompilacja CPythona bez GIL (PEP 703, plik wykonywalny zwykle `python3.13t`), a w Pythonie 3.14 tryb ten stał się oficjalnie wspieranym (choć nadal opcjonalnym) wariantem. W takiej kompilacji wątki mogą równolegle wykonywać kod Pythona na wielu rdzeniach, kosztem nieco wolniejszego działania jednowątkowego i konieczności dostosowania niektórych bibliotek. Domyślna dystrybucja CPythona nadal posiada GIL. Inne implementacje: Jython i IronPython nie mają GIL, PyPy – ma.

### Przykład 1 – pomiar wpływu GIL (wątki vs procesy dla CPU)

```python
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def compute(n):
    s = 0
    for i in range(n):
        s += i * i
    return s

def measure(name, executor_cls, tasks):
    start = time.perf_counter()
    with executor_cls(max_workers=4) as ex:
        list(ex.map(compute, tasks))
    print(f"{name:<12} {time.perf_counter() - start:.2f} s")

if __name__ == "__main__":
    tasks = [5_000_000] * 4

    start = time.perf_counter()
    for t in tasks:
        compute(t)
    print(f"{'Sekwencyjnie':<12} {time.perf_counter() - start:.2f} s")

    measure("4 wątki", ThreadPoolExecutor, tasks)    # ≈ sekwencyjnie (GIL!)
    measure("4 procesy", ProcessPoolExecutor, tasks)  # wyraźnie szybciej
```

Typowy wynik na 4-rdzeniowym CPU ze standardowym CPython: sekwencyjnie ~1,6 s, wątki ~1,6 s, procesy ~0,5 s.

### Przykład 2 – sprawdzenie środowiska i interwał przełączania

```python
import sys
import sysconfig

print("Wersja:", sys.version)
print("Interwał przełączania wątków:", sys.getswitchinterval(), "s")

# Czy interpreter został skompilowany z obsługą free-threading?
print("Kompilacja free-threading:", bool(sysconfig.get_config_var("Py_GIL_DISABLED")))

# Python 3.13+: czy GIL jest aktualnie włączony?
if hasattr(sys, "_is_gil_enabled"):
    print("GIL włączony:", sys._is_gil_enabled())
```

### Przykład 3 – kiedy wątki jednak pomagają mimo GIL

```python
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor

data = [bytes(50_000_000)] * 4        # 4 bloki po 50 MB

def digest(block):
    return hashlib.sha256(block).hexdigest()   # hashlib zwalnia GIL dla dużych danych

start = time.perf_counter()
[digest(b) for b in data]
print(f"Sekwencyjnie: {time.perf_counter() - start:.2f} s")

start = time.perf_counter()
with ThreadPoolExecutor(4) as ex:
    list(ex.map(digest, data))
print(f"4 wątki:      {time.perf_counter() - start:.2f} s")   # szybciej!
```

**Reguła wyboru:**
- czekasz (sieć, dysk) → **wątki** lub `asyncio`,
- liczysz w czystym Pythonie → **procesy**,
- liczysz w bibliotece C zwalniającej GIL (NumPy, hashlib) → wątki mogą wystarczyć,
- free-threaded Python 3.13t/3.14t → wątki mogą przyspieszać również obliczenia.

---

## 9. Projekt zaliczeniowy

### 9.1. Cel

Samodzielne (lub w parach – po uzgodnieniu z prowadzącym) zaprojektowanie i implementacja aplikacji w języku Python **na dowolny temat**, która w uzasadniony, praktyczny sposób wykorzystuje **wszystkie** zagadnienia omawiane na zajęciach.

### 9.2. Wymagania obowiązkowe

Projekt musi zawierać co najmniej:

| # | Zagadnienie | Minimalne wymaganie |
|---|---|---|
| 1 | Dekoratory funkcji | 2 własne dekoratory, w tym **co najmniej 1 z parametrami**; użycie `functools.wraps` |
| 2 | Dekoratory metod | 1 własny dekorator metody korzystający z `self` + użycie `@property` (z setterem), `@classmethod` lub `@staticmethod` |
| 3 | Iteratory | 1 własna klasa implementująca protokół iteratora (`__iter__`, `__next__`) |
| 4 | Generatory | 1 funkcja-generator (`yield`) + wyrażenia generujące; mile widziany potok generatorów lub `yield from` |
| 5 | Wyrażenia regularne | co najmniej 2 różne wzorce (walidacja i/lub ekstrakcja danych), w tym grupy nazwane |
| 6 | Wątki | przetwarzanie współbieżne zadań I/O (`threading` lub `ThreadPoolExecutor`) z poprawną synchronizacją (`Lock`/`Queue`) |
| 7 | Procesy | przetwarzanie równoległe zadania CPU-bound (`multiprocessing` lub `ProcessPoolExecutor`) |
| 8 | GIL | **pomiar porównawczy** (sekwencyjnie / wątki / procesy) wraz z wnioskami w dokumentacji |

Wymagania techniczne:
- Python 3.12+, kod podzielony na moduły (nie jeden plik na 1000 linii),
- czytelne nazwy, docstringi, adnotacje typów (*type hints*) w kluczowych funkcjach,
- obsługa błędów (wyjątki, nieprawidłowe dane wejściowe),
- dane testowe dołączone do projektu lub generowane przez skrypt,
- plik `requirements.txt`, jeśli używane są biblioteki zewnętrzne,
- repozytorium Git (np. GitHub/GitLab) z historią commitów pokazującą postęp prac.

### 9.3. Elementy dodatkowe

- testy jednostkowe (`unittest` lub `pytest`),
- interfejs wiersza poleceń (`argparse`) lub prosty GUI/web,
- logowanie przy użyciu modułu `logging`,
- porównanie z `asyncio` lub uruchomienie benchmarku na free-threaded Python 3.13t/3.14t,
- wykresy wyników pomiarów (np. `matplotlib`).

### 9.4. Co należy oddać

1. Dokument (`.pdf`, `.md` lub `.txt`) umieszczony na platformie Moodle, zawierający link do repozytorium z kodem źródłowym oraz krótką instrukcję, gdzie w repozytorium znajduje się projekt (np. nazwa gałęzi i katalogu).
2. Plik `README.md` umieszczony w głównym katalogu repozytorium, zawierający:
   - opis projektu i instrukcję uruchomienia,
   - **tabelę mapowania**: zagadnienie → plik / klasa / funkcja, w której zostało użyte,
   - wyniki pomiarów wydajności (tabela) i wnioski dotyczące GIL (5–10 zdań),
   - krótki opis problemów napotkanych w trakcie realizacji.
3. Krótka prezentacja / obrona projektu na ostatnich zajęciach (ok. 10 min): demonstracja działania + odpowiedzi na pytania dotyczące kodu.

Przykład tabeli mapowania w README:

| Zagadnienie | Gdzie w kodzie |
|---|---|
| Dekorator z parametrami | `utils/decorators.py` → `retry(attempts, delay)` |
| Dekorator metody | `core/scanner.py` → `Scanner.requires_config` |
| Iterator | `core/reader.py` → klasa `ChunkReader` |
| Generator | `core/pipeline.py` → `parse_lines()` |
| Regex | `core/patterns.py` → `IP_RE`, `DATE_RE` |
| Wątki | `io/downloader.py` → `ThreadPoolExecutor` |
| Procesy | `core/analyzer.py` → `ProcessPoolExecutor` |
| Pomiar GIL | `benchmarks/gil_benchmark.py` |

### 9.5. Kryteria oceny (100 pkt)

| Kryterium | Punkty |
|---|---|
| Realizacja zagadnień | 50 |
| Jakość kodu: struktura, czytelność, docstringi, type hints, obsługa błędów | 20 |
| Dokumentacja (README, tabela mapowania, wyniki i wnioski z pomiarów) | 10 |
| Obrona projektu – zrozumienie własnego kodu | 10 |
| Elementy dodatkowe (testy, CLI, logging, wykresy, asyncio…) | 10 |

Skala ocen: 0–50 pkt – ndst (2,0); 51–60 – dst (3,0); 61–70 – dst+ (3,5); 71–80 – db (4,0); 81–90 – db+ (4,5); 91–100 – bdb (5,0).

### 9.6. Propozycje tematów

Student może zaproponować własny temat (do akceptacji prowadzącego). Przykłady:

1. **Analizator logów serwera WWW** – wczytuje duże pliki logów (generator, własny iterator czytający blokami), wyciąga IP, daty, kody HTTP i adresy URL (regex), równolegle liczy statystyki dla wielu plików (procesy), pobiera informacje o adresach IP z lokalnej bazy / API (wątki). Dekoratory: pomiar czasu, cache, walidacja konfiguracji.

2. **Wyszukiwarka zduplikowanych plików** – rekurencyjnie przegląda katalogi (generator `os.scandir` + `yield from`), filtruje nazwy plików wzorcami (regex), liczy skróty SHA-256 (porównanie wątki vs procesy – świetny przykład na GIL i `hashlib`), raportuje duplikaty.

3. **Crawler stron WWW (lokalnych lub z dozwolonej domeny testowej)** – pobiera strony współbieżnie (wątki + `Queue`), wyodrębnia linki, adresy e-mail i nagłówki (regex), analizuje treść (procesy – np. statystyki słów), z ograniczeniem liczby żądań na sekundę realizowanym dekoratorem `@rate_limit(n)`.

4. **Wsadowy procesor obrazów** – zmiana rozmiaru, filtry, znaki wodne dla setek zdjęć (Pillow + procesy), wczytywanie/zapisywanie plików (wątki), filtrowanie plików wg wzorca nazw i dat w nazwach (regex), iterator po partiach plików, dekoratory logujące operacje.

5. **System analizy danych CSV / sprzedażowych** – czytanie dużych plików CSV generatorem, walidacja pól (e-mail, kod pocztowy, NIP – regex), agregacje obliczane równolegle (procesy), eksport raportów do wielu formatów współbieżnie (wątki), klasy modeli z `@property` i walidacją.

6. **Monitor dostępności usług** – okresowo sprawdza listę własnych/testowych serwerów (wątki – zapytania HTTP lub `socket` na `localhost`), parsuje odpowiedzi i pliki konfiguracyjne (regex), analizuje historię czasów odpowiedzi (generatory, procesy do statystyk), dekorator `@retry` i `@timeout`.

7. **Analizator korpusu tekstów** – statystyki częstości słów, n-gramy, najdłuższe zdania dla zbioru książek z domeny publicznej (np. Projekt Gutenberg), tokenizacja wyrażeniami regularnymi, przetwarzanie plików równolegle (procesy), pobieranie plików (wątki), iterator po zdaniach.

8. **Narzędzie do kopii zapasowych** – wyszukuje zmienione pliki (generatory, sumy kontrolne), wyklucza ścieżki wg reguł (regex jak w `.gitignore`), kompresuje pliki równolegle (procesy, `zlib`/`zipfile`), kopiuje na dysk docelowy (wątki), dekoratory raportujące postęp i czas.

9. **Symulator kolejki zgłoszeń / systemu bankowego** – klasy kont z dekoratorami metod (autoryzacja, walidacja, logowanie operacji), wielu „klientów” jako wątki z poprawną synchronizacją, iterator po historii transakcji, wykrywanie podejrzanych transakcji regułami regex, równoległe generowanie raportów (procesy).

10. **Generator i walidator danych testowych** – generuje duże zbiory fikcyjnych danych osobowych (generatory, nieskończone strumienie), waliduje je wzorcami (regex: PESEL, e-mail, telefon, kod pocztowy), sprawdza sumy kontrolne PESEL równolegle (procesy), zapisuje do wielu plików (wątki).

11. **Mini-silnik wyszukiwania w dokumentach** – indeksuje katalog plików tekstowych/Markdown (procesy budują indeks odwrócony), obsługuje zapytania z wzorcami regex, zwraca wyniki leniwie (generator), cache wyników dekoratorem z parametrem `@cache(ttl=...)`.

12. **Benchmark algorytmów** – implementacja kilku algorytmów (sortowanie, liczby pierwsze, mnożenie macierzy w czystym Pythonie), dekorator `@benchmark(repeats=n)`, iterator po zestawach danych wejściowych, parsowanie pliku konfiguracji testów regexem, porównanie sekwencyjnie / wątki / procesy (i opcjonalnie free-threaded Python) z wykresami.

