from collections.abc import Iterable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from docfinder.files import read_file


def read_concurrent_files(path_list : Iterable[Path]) -> list[tuple[str,Path]]:

    results: list[tuple[str, Path]] = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(read_file, path): path
            for path in path_list
        }
        for future, path in futures.items():
            try:
                _result = future.result()
                results.append(_result)
            except (OSError, UnicodeDecodeError) as _err:
                print(f"Blad obslugi pliku {path} - {_err}")

    return results