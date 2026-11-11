import re
from pathlib import Path



def extract_words(text : str) -> set[str]:
    if not isinstance(text,str):
        raise ValueError
    _text = text.lower()
    matches = set(re.findall(r"\b\w+\b", _text))
    return matches



def build_index(result_read_concurrent_files : list[tuple[str, Path]]) -> dict[str, set[Path]]:
    index = {}
    for text, path in result_read_concurrent_files:
        for word in extract_words(text):
            if word not in index:
                index[word] = set()
            index[word].add(path)
    return index


def get_from_index(index :dict[str, set[Path]] , word : str) -> set[Path]:
    _word = word.lower()
    return index.get(_word, set())



# if __name__ == "__main__":
#     print(extract_words("Python i kot. Kot śpi."))