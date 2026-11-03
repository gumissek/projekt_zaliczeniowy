from pathlib import Path
from docfinder.types import SearchResult

def find_in_text(searching_phrase: str, text: str)-> SearchResult:
    """
    Szuka frazy w tekscie i zwraca ilsoc wystapien
    """
    result : SearchResult = {
        "count" : text.lower().count(searching_phrase.lower())
    }
    if searching_phrase.lower() in text.lower():
        # wyrazenie generujace 
        pary = ( (i, line) for i, line in enumerate(text.splitlines(), start = 1) if searching_phrase.lower() in line.lower())
        result["lines"] = dict(pary)
    return result