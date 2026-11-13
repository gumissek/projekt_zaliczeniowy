"""Porównanie analizy tekstu i wnioski o GIL.

Przeanalizowano 500 powielonych tekstów, wykonując po pięć przebiegów
dla każdej liczby workerow. Pomiar obejmował również utworzenie puli
wątków lub procesów oraz przekazanie im danych.
Średnie czasy w sekundach (sekwencyjnie / wątki / procesy) wyniosły:
  4 workerow: 0,730 / 0,745 / 0,312 (procesy około 2,34 razy szybciej),
  8 workerow: 0,702 / 0,723 / 0,242 (procesy około 2,90 razy szybciej),
  16 workerow: 0,706 / 0,715 / 0,218 (procesy około 3,24 razy szybciej).
Wyniki analiz były równe we wszystkich 15 przebiegach. Dla tych danych
16 procesów dało najlepszy czas, ale poprawa względem 8 była mniejsza niż
przy przejściu z 4 na 8. Większa liczba procesów nie zawsze jest korzystna.
W standardowym interpreterze CPython z włączonym GIL tylko jeden wątek naraz
wykonuje kod Pythona w danym interpreterze. Dlatego wątki zwykle nie
przyspieszają zadań obciążających procesor, a ich obsługa wprowadza narzut.
Wątki są natomiast przydatne przy operacjach I/O, gdy program czeka na dane.
Osobne procesy mają osobne interpretery i mogą wykorzystywać wiele rdzeni,
ale ich uruchomienie i przekazywanie danych również kosztuje czas.
W tej serii przyspieszenie procesów wyniosło od 2,34 do 3,24 razy, zależnie
od liczby pracowników. Wynik zależy od komputera, danych i rozmiaru zadania. Dane były sztuczne
, więc wyniku nie należy uogólniac.
"""

from docfinder.index import extract_words
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from docfinder.decorators import measure_time

EXAMPLE_TEXTS = [
    "Python jest językiem programowania. Python służy do analizy danych.",
    "Wyszukiwarka dokumentów znajduje słowa w plikach tekstowych.",
    "Wątki i procesy pozwalają wykonywać zadania współbieżnie.",
    "Indeks dokumentów przyspiesza wyszukiwanie słów w wielu plikach.",
    "Kot śpi na kanapie, a pies biega w ogrodzie.",
]

benchmark_texts = [(text + " ") * 1000 for text in EXAMPLE_TEXTS] * 100

@measure_time
def analyze_sequential(texts: list[str]) -> list[set[str]]:
    """Zwraca zbiory słów z tekstów analizowanych sekwencyjnie."""
    if not texts:
        return []

    if not all(isinstance(i,str) for i in texts):
        raise ValueError

    result = [ extract_words(text) for text in texts]

    return result

@measure_time
def analyze_threaded(texts: list[str], workers: int = 4) -> list[set[str]]:
    """Zwraca zbiory słów z tekstów analizowanych w puli wątków."""
    if not texts:
        return []

    if not all(isinstance(i,str) for i in texts):
        raise ValueError
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = executor.map(extract_words,texts)
        return list(results)

@measure_time
def analyze_processes(texts: list[str], workers: int = 4) -> list[set[str]]:
    """Zwraca zbiory słów z tekstów analizowanych w puli procesów."""
    if not texts:
        return []

    if not all(isinstance(i,str) for i in texts):
        raise ValueError

    with ProcessPoolExecutor(max_workers=workers) as p_executor:
        results = p_executor.map(extract_words,texts)
        return list(results)


def run_benchmark(texts : list[str] ,runs : int = 3, workers: int = 4 ) -> None:
    """Uruchamia wskazaną liczbę porównań i wyświetla zgodność wyników."""
    print(f"Benchmark - wydajnosciowy - workers: {workers}")
    overall_results = {}
    for run in range(1, runs + 1):
        print(f"    {run}# Analiza - sekwencyjna")
        result_sequential = analyze_sequential(texts)
        print(f"    {run}# Analiza - w watkach")
        result_threaded = analyze_threaded(texts, workers)
        print(f"    {run}# Analiza - w procesach")
        result_processes = analyze_processes(texts, workers)
        run_equal = result_sequential == result_threaded == result_processes
        print(f"Run {run}# Czy wyniki takie same? {run_equal}")
        overall_results[run] = run_equal
    print(f"Całościowe wyniki dla {runs} przebiegów:")
    for k, v in overall_results.items():
        print(F"    Przebieg {k} - wynik {v}")

if __name__ == "__main__":
    workers = [4,8,16]
    for w in workers:
        run_benchmark(texts=benchmark_texts, runs=5, workers=w)
  
