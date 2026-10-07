from __future__ import annotations

from .common import plt, save, stamp


def plot_sensitivity(rows, path, provenance: str, cutoff_key: str = None):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    x = [r["delta_latent_points"] for r in rows]
    axes[0].plot(x, [r["delta_mean_final"] for r in rows], "o-")
    axes[0].plot(x, x, "k--", lw=1, label="proporcional (Δnota = Δlatente)")
    axes[0].set(xlabel="Δ latente (pts)", ylabel="Δ média da nota final (pts)", title="Δ avaliação → Δ nota")
    axes[0].legend(fontsize=8)
    if rows and rows[0]["delta_p_cutoff"]:
        for c in rows[0]["delta_p_cutoff"]:
            axes[1].plot(x, [r["delta_p_cutoff"][c] for r in rows], "o-", label=f"corte {float(c):g}")
        axes[1].legend(fontsize=8)
    axes[1].set(xlabel="Δ latente (pts)", ylabel="Δ P(nota ≥ corte)", title="Δ nota → Δ decisão")
    return save(stamp(fig, provenance), path)
