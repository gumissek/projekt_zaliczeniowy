from pathlib import Path
import os

ALLOWED_EXTENSIONS = {".md", ".txt"}

def get_input():
    _search_phase = None
    while not _search_phase:
        _search_phase = input("Podaj szukane słowo: ").strip()
        if not _search_phase:
            print("Podana fraza jest za krótka.")
    return _search_phase


def read_file(file_path : str) -> tuple[str,str]:
    """
    Odczytuje plik od podanej sciezce
    :param file_path
    """
    _file_path = file_path.strip()
    def _get_filepath()-> str:
        return input("Podaj poprawna sciezke do pliku: ").strip()

    while not os.path.isfile(_file_path) or not Path(_file_path).suffix.lower() in ALLOWED_EXTENSIONS:
        if not os.path.isfile(_file_path):
            print("To nie jest plik.")
        if not Path(_file_path).suffix.lower() in ALLOWED_EXTENSIONS:
            print(f"Plik musi posiadac rozszerzenie {ALLOWED_EXTENSIONS}.")
        _file_path = _get_filepath()

    with open(_file_path,'r',encoding='utf-8') as f:
        fc = f.read()
        return fc , _file_path


def find_in_text(searching_phrase: str, text: str)-> dict[str,int | dict[int,str]]:
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

def print_dict(data : dict) -> None:
    for k,v in data.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    print("Witaj w DocFinder!")
    phrase = get_input()
    print(f"Szukasz {phrase}")
    file_name = input("Podaj nazwe pliku: ")
    f_content, file_name = read_file(file_name)
    result = find_in_text(phrase, f_content)
    occ_in_file = result.get("count")
    if occ_in_file > 0:
        found_lines = result.get("lines")
        print(f"Szukana fraza wystepuje w pliku {occ_in_file} w liniach")
        print_dict(found_lines)
    else:
        print("Brak szukanej frazy w pliku")