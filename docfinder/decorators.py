import functools
import time
import errno

KODY_BLEDOW_WZNOWIEN = {errno.EINTR, errno.EAGAIN, errno.ETIMEDOUT}
# EINTR - Operacja została przerwana.
# EAGAIN - Zasób jest chwilowo niedostępny albo operacji nie można teraz ukończyć.
# ETIMEDOUT - Operacja przekroczyła limit czasu.


def measure_time(func):
    """
    Dekorator do mierzenia czasu wykonania funkcji
    """
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        start = time.perf_counter()
        result = func(*args,**kwargs)
        elapsed = time.perf_counter() - start
        print(f"Wykonano funkcje {func.__name__} w {elapsed:.4f} s")
        return result
    return wrapper

def folder_required(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.folder.is_dir():
            raise ValueError(f"Folder nie istnieje: {self.folder}")
        return method(self, *args, **kwargs)
    return wrapper


def retry(attempts:int = 3 ):
    if attempts < 1:
        raise ValueError(f"Za mala liczba prob {attempts}")
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            for att in range(1, attempts+1):
                try:
                    return func(*args, **kwargs)
                except OSError as oserr:
                    if oserr.errno not in KODY_BLEDOW_WZNOWIEN:
                        raise
                    print(f"Blad {oserr} / {att}")
                    if att == attempts:
                        raise
        return wrapper
    return decorator   