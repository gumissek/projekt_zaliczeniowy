from pathlib import Path
from collections.abc import Iterator
import os

ALLOWED_EXTENSIONS = {".md", ".txt"}

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


def get_files_from_folder(f_path : str | Path)-> list[Path]:
    _f_path = Path(f_path)
    while not os.path.isdir(_f_path):
        _f_path = _get_path()

    result = []
    try:
        _dir_content = Path(_f_path).iterdir()
        for item in _dir_content:
            if os.path.isdir(item):
                for i in get_files_from_folder(item):
                    result.append(i)
            elif os.path.isfile(item) and item.suffix.lower() in ALLOWED_EXTENSIONS:
                result.append(item)
    except OSError as _error:
        print(f"Blad dostepu do sciezki {_f_path} - {_error}")
    return result



def iter_files(folder_path : Path) -> Iterator[Path]:
    _folder_path = Path(folder_path)
    while not os.path.isdir(_folder_path):
        _folder_path = _get_path()

    try:
        for item in Path(_folder_path).iterdir():
            if os.path.isfile(item) and item.suffix.lower() in ALLOWED_EXTENSIONS:
                yield item
            elif os.path.isdir(item):
                # generator
                yield from iter_files(item)
    except OSError as _err:
        print(f"Blad dostepu do {_folder_path} - {_err}")
