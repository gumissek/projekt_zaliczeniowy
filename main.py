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


if __name__ == "__main__":
    print("Witaj w DocFinder!")
    phrase = get_input()
    print(f"Szukasz {phrase}")
    file_name = input("Podaj nazwe pliku: ")
    f_content, file_name = read_file(file_name)

    if phrase.lower() in f_content.lower():
        print(f"Szukana fraza {phrase} znajduje sie w pliku {file_name}")
    else:
        print(f"Brak szukanej frazy w pliku {file_name}")
