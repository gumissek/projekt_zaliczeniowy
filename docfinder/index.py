import re
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor


def extract_words(text : str) -> set[str]:
    if not isinstance(text,str):
        raise ValueError
    _text = text.lower()
    matches = set(re.findall(r"\b\w+\b", _text))
    return matches



def build_index(result_read_concurrent_files : list[tuple[str, Path]]) -> dict[str, set[Path]]:
    index = {}
    texts = (text for text, path in result_read_concurrent_files)
    with ProcessPoolExecutor(max_workers=8) as p_executor:
        word_sets = p_executor.map(extract_words,texts)
        for (_, path), words in zip(result_read_concurrent_files, word_sets):
            for word in words:
                if word not in index:
                    index[word] = set()
                index[word].add(path)
    return index


def get_from_index(index :dict[str, set[Path]] , word : str) -> set[Path]:
    _word = word.lower()
    return index.get(_word, set())



# if __name__ == "__main__":
#     print(extract_words("Python i kot. Kot śpi."))