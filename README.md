# DocFinder

DocFinder to konsolowa wyszukiwarka lokalnych dokumentów tekstowych i Markdown. Przeszukuje folder wraz z podfolderami, wyświetla liczbę dopasowań, pasujące linie i sekcje Markdown. Dostępne są wyszukiwanie frazy oraz wyszukiwanie całego słowa z użyciem indeksu.

## Uruchomienie

Wymagany jest Python 3.12 lub nowszy. Projekt sprawdzono na Pythonie 3.14.4. W katalogu głównym zainstaluj zależność używaną do tworzenia wykresów benchmarku:

```powershell
python -m pip install -r requirements.txt
```

Uruchom program interaktywnie:

```powershell
python main.py
```

Wybierz tryb `1` dla fragmentu lub frazy albo `2` dla całego słowa, a następnie podaj folder i wyszukiwane wyrażenie. Wpisz `quit`, aby zakończyć.
Przykładowe dokumenty znajdują się w katalogu `dane_testowe`.

Można też wykonać jednorazowe wyszukiwanie z argumentami:

```powershell
python main.py dane_testowe kot --tryb 2
python main.py dane_testowe "Lorem Ipsum" --tryb 1
python main.py --help
```

Benchmark uruchamia się poleceniem `python -m docfinder.benchmark`. Porównuje on analizę sekwencyjną, wątki, procesy i `asyncio`, sprawdza zgodność wyników oraz zapisuje wykresy poszczególnych przebiegów w `benchmark_results`.

## Mapowanie zagadnień na kod

| #   | Zagadnienie         | Gdzie w kodzie i jak zostało wykorzystane                                                                                                                                                                 |
| --- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Dekoratory funkcji  | `docfinder/decorators.py` -> `measure_time` mierzy czas wykonania, a `retry(attempts)` ponawia operację po wybranych błędach I/O. Oba używają `functools.wraps`.                                          |
| 2   | Dekoratory metod    | `docfinder/decorators.py` -> `folder_required` sprawdza folder przez `self`. `docfinder/config.py` -> `SearchConfig.folder` używa `@property` i settera, a `from_current_directory` używa `@classmethod`. |
| 3   | Iteratory           | `docfinder/results_iterator.py` -> klasa `ResultsIterator` implementuje `__iter__` i `__next__`.                                                                                                          |
| 4   | Generatory          | `docfinder/files.py` -> `iter_files` używa `yield` i `yield from` do rekurencyjnego wyszukiwania plików. `docfinder/search.py` -> `find_in_text` używa wyrażenia generującego pasujące linie.             |
| 5   | Wyrażenia regularne | `docfinder/search.py` -> `find_whole_word` rozpoznaje granice słów, a `NAGLOWEK_PATTERN` i `parse_heading` rozpoznają nagłówki Markdown przy użyciu nazwanych grup `level` i `title`.                     |
| 6   | Wątki               | `docfinder/concurrent_reader.py` -> `read_concurrent_files` odczytuje pliki przez `ThreadPoolExecutor`, a `ReadCounter` chroni licznik i listę ścieżek za pomocą `Lock`.                                  |
| 7   | Procesy             | `docfinder/index.py` -> `build_index` używa `ProcessPoolExecutor` do równoległego wyodrębniania słów przez `extract_words`.                                                                               |
| 8   | GIL                 | `docfinder/benchmark.py` -> `analyze_sequential`, `analyze_threaded` i `analyze_processes` porównują tę samą analizę tekstu. Wyniki i wnioski znajdują się w opisie modułu i w folderze benchmark_results |

## Wyniki pomiarów wydajności

Wyniki pochodzą z uruchomienia benchmarku 13 listopada 2026 r. dla 500 sztucznie powielonych tekstów. Każda wartość jest średnią z pięciu przebiegów, obliczoną z czasów wyświetlonych w logach z dokładnością do czterech miejsc po przecinku. Pomiar obejmował utworzenie puli wątków lub procesów i przekazanie danych. Liczba workerów dotyczy wątków i procesów, a pomiary sekwencyjne i `asyncio` wykonano osobno w każdej serii. Wyniki wszystkich czterech metod były zgodne we wszystkich 15 przebiegach.

| Liczba workerów | Sekwencyjnie [s] | Wątki [s] | Procesy [s] | asyncio [s] |
| --------------- | ---------------- | --------- | ----------- | ----------- |
| 4               | 0,6874           | 0,7035    | 0,7814      | 0,7006      |
| 8               | 0,6919           | 0,7017    | 0,7594      | 0,7076      |
| 16              | 0,6967           | 0,7189    | 0,8683      | 0,7089      |

Wykresy poszczególnych przebiegów zapisano w folderze `benchmark_results`. Wyniki zależą od sprzętu, danych i obciążenia systemu.

## Wnioski dotyczące GIL

W standardowym CPythonie z włączonym GIL tylko jeden wątek naraz wykonuje kod Pythona w danym interpreterze. W tej serii analiza w wątkach trwała nieco dłużej niż analiza sekwencyjna. Wątki nie przyspieszyły więc badanego zadania obciążającego procesor. Przy operacjach I/O mogą jednak pracować współbieżnie, gdy jeden z wątków czeka na dane. Osobne procesy mają oddzielne interpretery i mogą korzystać z wielu rdzeni. W tej serii procesy były wolniejsze od wykonania sekwencyjnego, a pomiar obejmował koszt utworzenia puli i przekazania danych. Wariant `asyncio` również nie przyspieszył obliczeń, ponieważ analiza nie oddaje sterowania podczas pracy nad tekstem.

## Napotkane problemy

- Pliki z niepoprawnym kodowaniem UTF-8 powodowały błędy odczytu. Program zapisuje ostrzeżenie i kontynuuje pracę z pozostałymi plikami.
- Błędy dostępu do folderów wymagały obsługi wyjątków, aby przeglądanie pozostałych katalogów mogło być kontynuowane.
- Pusta ścieżka była interpretowana jako bieżący katalog. Dodano sprawdzanie pustego wejścia i ponowne pytanie o ścieżkę.
- Współdzielony licznik i lista ścieżek wymagały synchronizacji wątków. Zastosowano `Lock`.
