from typing import NotRequired, TypedDict

class SearchResult(TypedDict):
    count: int
    whole_word_count : int
    lines: NotRequired[dict[int,str]]
    sections: NotRequired[dict[int, str | None]]

class RegexHeadingResult(TypedDict):
    heading: int
    title: str