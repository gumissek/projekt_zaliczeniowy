def find_in_text(searching_phrase: str, text: str)-> dict[str,int | dict[int,str]]:
    """
    Szuka frazy w tekscie i zwraca ilsoc wystapien
    """
    result = {
        "count" : text.lower().count(searching_phrase.lower())
    }
    if searching_phrase.lower() in text.lower():
        # wyrazenie generujace 
        pary = ( (i, line) for i, line in enumerate(text.splitlines(), start = 1) if searching_phrase.lower() in line.lower())
        result["lines"] = dict(pary)
    return result