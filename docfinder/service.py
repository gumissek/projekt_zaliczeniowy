from pathlib import Path

from docfinder.search import find_in_text
from docfinder.decorators import measure_time
from docfinder.concurrent_reader import read_concurrent_files
from docfinder.models import SearchResult
from docfinder.config import SearchConfig
from docfinder.files import _get_path

@measure_time
def read_files(dir_path : str | Path, search_phrase : str) -> dict[Path, SearchResult]:
    while True:
        try:
            config = SearchConfig(path=dir_path)
            break
        except ValueError as error:
            print(error)
            dir_path = _get_path()

    file_paths = config.get_files()

    file_contents = read_concurrent_files(file_paths)

    _rfs_result ={
        file_path: find_in_text(search_phrase, content)
        for content, file_path in file_contents
    }

    return _rfs_result