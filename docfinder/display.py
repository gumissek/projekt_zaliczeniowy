def print_result(result_data : dict) -> None:
    is_any_found = False
    for _fn, result in result_data.items():
        _count = result.get("count")
        if _count > 0:
            is_any_found = True
            print(f"Plik {_fn}")
            print(f"Liczba wystapien {_count}")
            for ln, ln_conent in result.get("lines").items():
                print(f"    Linia {ln}: {ln_conent}")
    if not is_any_found:
        print("Nie znaleziono frazy")