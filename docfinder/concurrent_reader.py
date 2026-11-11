from threading import Lock
from collections.abc import Iterable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from docfinder.files import read_file

class ReadCounter:
    def __init__(self):
        # lock
        self._lock = Lock()
        self.counter : int = 0
        self.correct_paths : list [Path] =[]

    @property
    def correct_paths(self) -> list[Path]:
        with self._lock:
            return self._correct_paths.copy()

    @correct_paths.setter
    def correct_paths(self, paths : list[Path]) -> None:
        if not isinstance(paths, list) or not all( isinstance(path, Path) for path in paths):
            raise ValueError
        with self._lock:
            self._correct_paths = paths.copy()

    def add_correct_path(self, path:Path) -> None:
        with self._lock:
            self._correct_paths.append(path)

    def drop_correct_paths(self) -> None:
        with self._lock:
            self._correct_paths.clear()

    @property
    def counter(self) -> int:
        with self._lock:
            return self._counter
    
    @counter.setter
    def counter(self, value:int) -> None:
        if not isinstance(value, int):
            raise ValueError("")
        with self._lock:
            self._counter = value

    def increment(self):
        with self._lock:
            self._counter += 1 



def read_concurrent_files(path_list : Iterable[Path]) -> list[tuple[str,Path]]:
    counter = ReadCounter()
    results: list[tuple[str, Path]] = []

    def read_and_count(path: Path) -> tuple[str,Path]:
        result = read_file(path) # rzuci blad i nie policzy pliku ktrego nie dalo sie odczytac
        counter.increment()
        counter.add_correct_path(path)
        return result

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(read_and_count, path): path
            for path in path_list
        }
        for future, path in futures.items():
            try:
                _result = future.result()
                results.append(_result)
            except (OSError, UnicodeDecodeError) as _err:
                print(f"Blad obslugi pliku {path} - {_err}")

    print(f"Odczytano poprawnie {counter.counter} plików.")
    print(f"    Sciezki odczytanych plikow: {counter.correct_paths}")
    return results


    