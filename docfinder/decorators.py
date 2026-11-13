import functools
import time
import errno
import logging

KODY_BLEDOW_WZNOWIEN = {errno.EINTR, errno.EAGAIN, errno.ETIMEDOUT}
# EINTR - Operacja została przerwana.
# EAGAIN - Zasób jest chwilowo niedostępny albo operacji nie można teraz ukończyć.
# ETIMEDOUT - Operacja przekroczyła limit czasu.

logger = logging.getLogger(__name__)

def measure_time(func) -> None:
    """Dekoruje funkcję, logując czas jej poprawnego wykonania."""
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        """Wywołuje funkcję, mierzy jej czas i zwraca jej wynik."""
        start = time.perf_counter()
        result = func(*args,**kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"Wykonano funkcje {func.__name__} w {elapsed:.4f} s")
        return result
    return wrapper

def folder_required(method):
    """Sprawdza istnienie folderu obiektu przed wywołaniem dekorowanej metody."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """Sprawdza folder i wywołuje metodę lub zgłasza ValueError."""
        if not self.folder.is_dir():
            raise ValueError(f"Folder nie istnieje: {self.folder}")
        return method(self, *args, **kwargs)
    return wrapper


def retry(attempts:int = 3 ):
    """Ponawia wywołanie funkcji po wybranych tymczasowych błędach I/O. Liczbę prób określa parametr attempts."""
    if attempts < 1:
        raise ValueError(f"Za mala liczba prob {attempts}")
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            """Wywołuje funkcję ponownie po obsługiwanym błędzie, do wyczerpania prób."""
            for att in range(1, attempts+1):
                try:
                    return func(*args, **kwargs)
                except OSError as oserr:
                    if oserr.errno not in KODY_BLEDOW_WZNOWIEN:
                        raise
                    logger.warning("Błąd %s, próba %s z %s", oserr, att, attempts)
                    if att == attempts:
                        raise
        return wrapper
    return decorator   
