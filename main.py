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

def _get_path()-> Path:
        return Path(input("Podaj poprawna sciezke: ").strip())

def read_file(file_path : Path) -> tuple[str,Path]:
    """
    Odczytuje plik od podanej sciezce
    :param file_path
    """
    _file_path = Path(file_path)
    
    while not os.path.isfile(_file_path) or not Path(_file_path).suffix.lower() in ALLOWED_EXTENSIONS:
        if not os.path.isfile(_file_path):
            print("To nie jest plik.")
        if not Path(_file_path).suffix.lower() in ALLOWED_EXTENSIONS:
            print(f"Plik musi posiadac rozszerzenie {ALLOWED_EXTENSIONS}.")
        _file_path = _get_path()

    with open(_file_path,'r',encoding='utf-8') as f:
        fc = f.read()
        return fc , _file_path


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

def print_dict(data : dict) -> None:
    for k,v in data.items():
        print(f"{k}: {v}")

def get_files_from_folder(f_path : str | Path)-> list[Path]:
    _f_path = Path(f_path)
    while not os.path.isdir(_f_path):
        _f_path = _get_path()
 
    _dir_content = Path(_f_path).iterdir()
    result = []
    try:
        for item in _dir_content:
            if os.path.isdir(item):
                for i in get_files_from_folder(item):
                    result.append(i)
            elif os.path.isfile(item) and item.suffix.lower() in ALLOWED_EXTENSIONS:
                result.append(item)
    except OSError as _error:
        print(f"Blad dostepu do sciezki {_f_path} - {_error}")
    return result

def read_files(dir_path : str | Path, search_phrase : str):
    dir_path = Path(dir_path)
    _files_dir = get_files_from_folder(dir_path)
    _rfs_result = {}
    for _file in _files_dir:
        try:
            _fc, _ = read_file(_file)
            _rfs_result[_file] = find_in_text(search_phrase, _fc)
        except (OSError, UnicodeDecodeError) as error:
            print(f"Blad obslugi pliku {_file} - {error}")
    return _rfs_result

def print_result(result_data : dict) -> None:
    is_any_found = False
    for _fn, result in result_data.items():
        _count = result.get("count")
        if _count > 0:
            is_any_found = True
            print(f"Plik {_fn}")
            print(f"Liczba wystapien {_count}")
            for ln, ln_conent in result.get("lines").items():
                print(f"    Linia {ln}: {ln_conent}")
    if not is_any_found:
        print("Nie znaleziono frazy")


if __name__ == "__main__":
    print("Witaj w DocFinder!")
    phrase = get_input()
    print(f"Szukasz {phrase}")

    search_dir = input("Podaj nazwe folderu: ")
    result_read_files = read_files(search_dir, phrase)
    print_result(result_read_files)


