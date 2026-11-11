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

    
    