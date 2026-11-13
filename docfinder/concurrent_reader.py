from threading import Lock
from collections.abc import Iterable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from docfinder.files import read_file
import logging

logger = logging.getLogger(__name__)
class ReadCounter:
    """Przechowuje liczbę i ścieżki odczytanych plików, chroniąc je lockiem."""
    def __init__(self) -> None:
        # lock
        """Inicjuje lock, licznik i listę ścieżek."""
        self._lock = Lock()
        self.counter : int = 0
        self.correct_paths : list [Path] =[]

    @property
    def correct_paths(self) -> list[Path]:
        """Zwraca kopię listy ścieżek pod ochroną locka."""
        with self._lock:
            return self._correct_paths.copy()

    @correct_paths.setter
    def correct_paths(self, paths : list[Path]) -> None:
        """Zastępuje listę ścieżek kopią podanej listy. Odrzuca niepoprawne dane."""
        if not isinstance(paths, list) or not all( isinstance(path, Path) for path in paths):
            raise ValueError
        with self._lock:
            self._correct_paths = paths.copy()

    def add_correct_path(self, path:Path) -> None:
        """Dodaje ścieżkę poprawnie odczytanego pliku pod ochroną locka."""
        with self._lock:
            self._correct_paths.append(path)

    def drop_correct_paths(self) -> None:
        """Czyści listę ścieżek pod ochroną locka."""
        with self._lock:
            self._correct_paths.clear()

    @property
    def counter(self) -> int:
        """Zwraca wartość licznika pod ochroną locka."""
        with self._lock:
            return self._counter
    
    @counter.setter
    def counter(self, value:int) -> None:
        """Ustawia całkowitą wartość licznika pod ochroną locka."""
        if not isinstance(value, int):
            raise ValueError("")
        with self._lock:
            self._counter = value

    def increment(self) -> None:
        """Zwiększa licznik pod ochroną locka."""
        with self._lock:
            self._counter += 1 



def read_concurrent_files(path_list : Iterable[Path]) -> list[tuple[str,Path]]:
    """Odczytuje pliki w wątkach i zwraca ich treść wraz ze ścieżkami. Błędy odczytu zapisuje w logu."""
    counter = ReadCounter()
    results: list[tuple[str, Path]] = []

    def read_and_count(path: Path) -> tuple[str,Path]:
        """Odczytuje plik i zapisuje jego ścieżkę oraz zwiększa licznik po sukcesie."""
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
                logger.warning(f"Blad obslugi pliku {path} - {_err}")

    logger.info(f"Odczytano poprawnie {counter.counter} plików.")
    logger.info(f"Sciezki odczytanych plikow: {counter.correct_paths}")
    return results
