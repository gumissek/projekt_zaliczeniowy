from pathlib import Path
from docfinder.models import SearchResult, RegexHeadingResult
import re

NAGLOWEK_PATTERN = r"^(?P<level>#{1,6})\s+(?P<title>.+)$"

def find_whole_word(word: str, text: str):
    pattern = r"\b" + re.escape(word) + r"\b"
    matches = re.finditer(pattern, text, re.IGNORECASE)
    return sum(1 for match in matches)

def parse_heading(line:str) -> RegexHeadingResult | None:
    match = re.match(NAGLOWEK_PATTERN, line)
    if not match:
        return None
    return {
        "heading" : len(match.group("level")),
        "title" : match.group("title")
    }


def get_heading_and_title(text: str) -> dict[int, str | None]:
    current_heading = None
    sections = {}
    for index,ln in enumerate(text.splitlines(),start=1 ):
        heading = parse_heading(ln)

        if heading is not None:
            current_heading = heading["title"]

        sections[index] = current_heading
    
    return sections
        

def find_in_text(searching_phrase: str, text: str)-> SearchResult:
    """
    Szuka frazy w tekscie i zwraca ilsoc wystapien
    """
    result : SearchResult = {
        "count" : text.lower().count(searching_phrase.lower()),
        "whole_word_count" : find_whole_word(searching_phrase, text)
    }
    if searching_phrase.lower() in text.lower():
        # wyrazenie generujace 
        pary = ( (i, line) for i, line in enumerate(text.splitlines(), start = 1) if searching_phrase.lower() in line.lower())
        result["lines"] = dict(pary)
        result["sections"] = get_heading_and_title(text)
    return result