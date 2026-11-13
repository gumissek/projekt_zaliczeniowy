from typing import Self
from collections.abc import Iterator
from pathlib import Path
from docfinder.decorators import folder_required
from docfinder.files import iter_files



class SearchConfig:
    """Przechowuje i sprawdza folder używany do wyszukiwania."""
    def __init__(self, path: Path) -> None:
        """Tworzy konfigurację dla wskazanego folderu."""
        self.folder = Path(path)

    @property
    def folder(self) -> Path:
        """Zwraca skonfigurowany folder."""
        return self._folder

    @folder.setter
    def folder(self, folder_path : str | Path) -> None:
        """Ustawia istniejący folder lub zgłasza ValueError."""
        __folder = Path(folder_path)
        if not __folder.is_dir():
            raise ValueError(f"To nie jest folder: {__folder}")
        self._folder = __folder

    @folder_required
    def get_files(self) -> Iterator[Path]:
        """Zwraca iterator ścieżek dokumentów w skonfigurowanym folderze."""
        return iter_files(self.folder)

    @classmethod
    def from_current_directory(cls) -> Self:
        """Tworzy konfigurację dla bieżącego katalogu roboczego."""
        return cls(Path.cwd())
