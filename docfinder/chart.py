from pathlib import Path
import matplotlib.pyplot as plt

def save_chart(times: dict[str, float],workers: int,run: int, output_path: Path) -> None:
    """Zapisuje wykres czasów jednego przebiegu benchmarku."""
    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.bar(times.keys(), times.values())
    ax.bar_label(bars, fmt="%.4f s", padding=3)

    ax.set_title(f"Przebieg {run}, liczba workerow: {workers}")
    ax.set_ylabel("Czas [s]")
    ax.set_ylim(0, max(times.values()) * 1.15)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)