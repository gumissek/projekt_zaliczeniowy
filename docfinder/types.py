from typing import NotRequired, TypedDict

class SearchResult(TypedDict):
    count: int
    lines: NotRequired[dict[int,str]]