import functools
import time

def measure_time(func):
    """
    Dekorator do mierzenia czasu wykonania funkcji
    """
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        start = time.perf_counter()
        result = func(*args,**kwargs)
        elapsed = time.perf_counter() - start
        print(f"Wykonano funkcje {func} w {elapsed:.4f} s")
        return result
    return wrapper

def folder_required(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.folder.is_dir():
            raise ValueError(f"Folder nie istnieje: {self.folder}")
        return method(self, *args, **kwargs)
    return wrapper
