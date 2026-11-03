from pathlib import Path
from typing import Self
from docfinder.types import SearchResult

class ResultsIterator:
    def __init__(
        self, result_dict: dict[Path, SearchResult]) -> None:
        self.items_iterator = iter(result_dict.items())

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> tuple[Path, SearchResult]:
        return next(self.items_iterator)