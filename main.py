from pathlib import Path
from docfinder.search import find_in_text
from docfinder.files import read_file, iter_files
from docfinder.display import print_result

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
    dir_path = Path(dir_path)
    _rfs_result = {}
    for _file in iter_files(dir_path):
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


