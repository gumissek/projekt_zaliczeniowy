from docfinder.results_iterator import ResultsIterator
from docfinder.types import SearchResult
from pathlib import Path

def print_result(result_data : dict[Path, SearchResult]) -> None:
    is_any_found = False
    for _fn, result in ResultsIterator(result_data):
        _count = result.get("count")
        if _count > 0:
            is_any_found = True
            print(f"Plik {_fn}")
            print(f"Liczba wystapien {_count}")
            for ln, ln_conent in result.get("lines").items():
                print(f"    Linia {ln}: {ln_conent}")
    if not is_any_found:
        print("Nie znaleziono frazy")