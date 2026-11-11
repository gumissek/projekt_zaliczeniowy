from docfinder.results_iterator import ResultsIterator
from docfinder.models import SearchResult
from pathlib import Path

def print_result(result_data : dict[Path, SearchResult]) -> None:
    is_any_found = False
    for _fn, result in ResultsIterator(result_data):
        _count = result.get("count")
        _whole_word_count = result.get("whole_word_count")
        if _count > 0:
            is_any_found = True
            print(f"Plik {_fn}")
            print(f"Liczba wystapien {_count}")
            print(f"Liczba znalezionych pełnych słów {_whole_word_count}")
            for ln, ln_conent in result.get("lines").items():
                section = result.get("sections").get(ln)
                print(f"    Linia {ln}{f", sekcja {section}" if section is not None else ""}: {ln_conent}" )
    if not is_any_found:
        print("Nie znaleziono frazy")