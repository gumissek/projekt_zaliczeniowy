from typing import Self
from collections.abc import Iterator
from pathlib import Path
from docfinder.decorators import folder_required
from docfinder.files import iter_files



class SearchConfig:
    def __init__(self, path: Path) -> None:
        self.folder = Path(path)

    @property
    def folder(self) -> Path:
        return self._folder

    @folder.setter
    def folder(self, folder_path : str | Path) -> None:
        __folder = Path(folder_path)
        if not __folder.is_dir():
            raise ValueError(f"To nie jest folder: {__folder}")
        self._folder = __folder

    @folder_required
    def get_files(self) -> Iterator[Path]:
        return iter_files(self.folder)

    @classmethod
    def from_current_directory(cls) -> Self:
        return cls(Path.cwd())
