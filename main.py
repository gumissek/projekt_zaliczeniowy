
def get_input():
    _search_phase = None
    while not _search_phase:
        _search_phase = input("Podaj szukane słowo: ").strip()
        if not _search_phase:
            print("Podana fraza jest za krótka.")
    return _search_phase


if __name__ == "__main__":
    print("Witaj w DocFinder!")
    phrase = get_input()
    print(f"Szukasz {phrase}")
