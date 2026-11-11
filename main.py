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

if __name__ == "__main__":
    print_welcome()
    is_on = True
    search_dir = input("Podaj nazwe folderu: ")
    f_contents, index = prepare_documents(search_dir)
    while is_on:
        phrase = get_input()
        if phrase.lower() == "quit":
            break
        print(f"Szukasz: {phrase}")
        result_read_files = read_files(f_contents,index, phrase)
        print_result(result_read_files)

    print("Dziękuje za skorzystanie z DocFinder!")

