from docfinder.files import _get_path
from pathlib import Path
from docfinder.search import find_in_text
from docfinder.files import read_file
from docfinder.display import print_result
from docfinder.config import SearchConfig

def get_input():
    _search_phase = None
    while not _search_phase:
        _search_phase = input("Podaj szukane słowo: ").strip()
        if not _search_phase:
            print("Podana fraza jest za krótka.")
    return _search_phase

def print_dict(data : dict) -> None:
    for k,v in data.items():
        print(f"{k}: {v}")

def read_files(dir_path : str | Path, search_phrase : str):

    while True:
        try:
            config = SearchConfig(path=dir_path)
            break
        except ValueError as error:
            print(error)
            dir_path = _get_path()

    _rfs_result = {}
    for _file in config.get_files():
        try:
            _fc, _ = read_file(_file)
            _rfs_result[_file] = find_in_text(search_phrase, _fc)
        except (OSError, UnicodeDecodeError) as error:
            print(f"Blad obslugi pliku {_file} - {error}")
    return _rfs_result

if __name__ == "__main__":
    print("Witaj w DocFinder!")
    phrase = get_input()
    print(f"Szukasz {phrase}")

    search_dir = input("Podaj nazwe folderu: ")
    result_read_files = read_files(search_dir, phrase)
    print_result(result_read_files)


