from pathlib import Path
from docfinder.display import print_result
from docfinder.service import read_files, prepare_documents

def invalid_input()-> None:
    print("Podana fraza jest za krótka.")
    
def get_input()-> str:
    _search_phase = None
    while not _search_phase:
        _search_phase = input("Podaj szukane słowo lub napisz 'quit' jesli chcesz przerwac: ").strip()
        if not _search_phase:
            invalid_input()
    return _search_phase

def print_welcome() -> None:
    print("Witaj w DocFinder!")
    print("Autor: Piotr Biliński nr albumu 112798")

def get_search_mode()-> str:
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

