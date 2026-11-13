from pathlib import Path
from typing import Self
from docfinder.models import SearchResult

class ResultsIterator:
    """Iteruje po parach ścieżki i wyniku wyszukiwania."""
    def __init__(self, result_dict: dict[Path, SearchResult]) -> None:
        """Tworzy iterator elementów słownika wyników."""
        self.items_iterator = iter(result_dict.items())

    def __iter__(self) -> Self:
        """Zwraca ten iterator."""
        return self

    def __next__(self) -> tuple[Path, SearchResult]:
        """Zwraca kolejną parę ścieżki i wyniku albo zgłasza StopIteration."""
        return next(self.items_iterator)
