from pathlib import Path
from docfinder.display import print_result
from docfinder.service import read_files

def get_input():
    _search_phase = None
    while not _search_phase:
        _search_phase = input("Podaj szukane słowo: ").strip()
        if not _search_phase:
            print("Podana fraza jest za krótka.")
    return _search_phase

if __name__ == "__main__":
    print("Witaj w DocFinder!")
    print("Autor: Piotr Biliński nr albumu 112798")
    phrase = get_input()
    print(f"Szukasz {phrase}")

    search_dir = input("Podaj nazwe folderu: ")
    result_read_files = read_files(search_dir, phrase)
    print_result(result_read_files)


