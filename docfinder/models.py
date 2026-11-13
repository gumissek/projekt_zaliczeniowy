from typing import NotRequired, TypedDict

class SearchResult(TypedDict):
    """Opisuje wynik wyszukiwania, w tym liczbę dopasowań oraz opcjonalnie linie i sekcje."""
    count: int
    whole_word_count : int
    lines: NotRequired[dict[int,str]]
    sections: NotRequired[dict[int, str | None]]

class RegexHeadingResult(TypedDict):
    """Opisuje poziom i tytuł rozpoznanego nagłówka Markdown."""
    heading: int
    title: str