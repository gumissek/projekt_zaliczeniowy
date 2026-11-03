def find_in_text(searching_phrase: str, text: str)-> dict[str,int | dict[int,str]]:
    """
    Szuka frazy w tekscie i zwraca ilsoc wystapien
    """
    result = {
        "count" : text.lower().count(searching_phrase.lower())
    }
    if searching_phrase.lower() in text.lower():
        occured_lines = {}
        for i, line in enumerate(text.splitlines()):
            if searching_phrase.lower() in line.lower():
                occured_lines[i+1] = line
        result["lines"] = occured_lines
    return result