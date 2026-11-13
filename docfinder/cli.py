from pathlib import Path
from docfinder.display import print_result
from docfinder.service import read_files, prepare_documents
import argparse


def parse_arguments() -> argparse.Namespace:
    """Pobiera argumenty przekazane przy uruchomieniu programu."""
    parser = argparse.ArgumentParser(
        description="Wyszukuje frazy i słowa w dokumentach."
    )
    parser.add_argument("folder", nargs="?", help="Folder z dokumentami")
    parser.add_argument("fraza", nargs="?", help="Szukana fraza lub słowo")
    parser.add_argument(
        "--tryb",
        choices=["1", "2"],
        default="1",
        help="1: fraza, 2: całe słowo przez indeks",
    )
    args = parser.parse_args()
    if (args.folder is None) != (args.fraza is None):
        parser.error("Podaj zarówno folder, jak i szukaną frazę.")
    if args.folder is not None:
        if not args.folder.strip() or not Path(args.folder).is_dir():
            parser.error("Podaj ścieżkę do istniejącego folderu.")
        if not args.fraza.strip():
            parser.error("Szukana fraza nie może być pusta.")
    return args

def invalid_input()-> None:
    """Wyświetla komunikat o pustej frazie."""
    print("Podana fraza jest za krótka.")
    
def get_input()-> str:
    """Pobiera i zwraca niepustą frazę od użytkownika."""
    _search_phase = None
    while not _search_phase:
        _search_phase = input("Podaj szukane słowo lub napisz 'quit' jesli chcesz przerwac: ").strip()
        if not _search_phase:
            invalid_input()
    return _search_phase

def print_welcome() -> None:
    """Wyświetla powitanie i dane autora."""
    print("Witaj w DocFinder!")
    print("Autor: Piotr Biliński nr albumu 112798")

def get_search_mode()-> str:
    """Pobiera od użytkownika poprawny tryb wyszukiwania: 1 albo 2."""
    print("Wybór trybu wyszukiwania:")
    print("    Wybierz 1: fragment lub fraza")
    print("    Wybierz 2: całe słowo przez indeks")
    while True:
        mode = input("Wybierz tryb: ")
        if mode not in ["1", "2"]:
            print("Niepoprawny tryb.")
        else:
            break
    return mode 

def main() -> None:
    """Uruchamia interfejs konsolowy i obsługuje zapytania aż do wpisania quit.
    Wywolanie np.: python main.py dane_testowe kot --tryb 2
    """
    args = parse_arguments()
    if args.folder is not None:
        f_contents, index = prepare_documents(args.folder)
        try:
            result = read_files(args.fraza, args.tryb, f_contents, index)
        except ValueError as error:
            print(error)
            raise SystemExit(2) from error
        print_result(result)
        return

    print_welcome()
    is_on = True
    search_mode = get_search_mode()
    search_dir = input("Podaj nazwe folderu: ")
    f_contents, index = prepare_documents(search_dir)
    while is_on:
        phrase = get_input()
        if phrase.lower() == "quit":
            break
        print(f"Szukasz: {phrase}")
        try:
            result_read_files = read_files(phrase, search_mode, f_contents, index)
        except ValueError as error:
            print(error)
            continue
        print_result(result_read_files)

    print("Dziękuje za skorzystanie z DocFinder!")

