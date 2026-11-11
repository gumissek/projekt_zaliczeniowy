from pathlib import Path

from docfinder.search import find_in_text, find_word_in_text
from docfinder.decorators import measure_time
from docfinder.concurrent_reader import read_concurrent_files
from docfinder.models import SearchResult
from docfinder.config import SearchConfig
from docfinder.files import _get_path
from docfinder.index import build_index, get_from_index


@measure_time
def read_files(search_phrase : str, search_mode : str , file_contents : list[tuple[str,Path]], index : dict[str, set[Path]]) -> dict[Path, SearchResult]:
    if search_mode == "1":
        return {
            file_path: find_in_text(search_phrase, content)
            for content, file_path in file_contents
        }
    if search_mode == "2":
        find_word_in_text(search_phrase, "")
        matching_paths = get_from_index(index, search_phrase)
        return {
            file_path: find_word_in_text(search_phrase, content)
            for content, file_path in file_contents
            if file_path in matching_paths
        }
    raise ValueError("Niepoprawny tryb wyszukiwania.")


def prepare_documents(dir_path : str | Path)-> tuple[list[tuple[str,Path]], dict[str, set[Path]]]:
    while True:
        try:
            config = SearchConfig(path=dir_path)
            break
        except ValueError as error:
            print(error)
            dir_path = _get_path()

    file_paths = config.get_files()

    file_contents = read_concurrent_files(file_paths)
    index = build_index(file_contents)
    print("Zbudowano index i zawartosc plików!")
    return file_contents, index
