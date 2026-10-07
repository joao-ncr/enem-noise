"""Utilidades comuns: toda figura carrega o rótulo de proveniência (exigência do projeto)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def stamp(fig, provenance: str, extra: str = ""):
    fig.text(0.01, 0.005, f"[{provenance}] {extra}".strip(), fontsize=7, color="#a33", ha="left", va="bottom")
    return fig


def save(fig, path):
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return str(path)
