"""Relatórios em Markdown com a cadeia: observação → hipótese → simulação → resultado → interpretação."""
from __future__ import annotations

from typing import Dict, List, Sequence

import pandas as pd

BANNER = ("> **Atenção:** todos os números abaixo são **SIMULADOS** e dependem de parâmetros **HIPOTÉTICOS**. "
          "Não constituem evidência empírica sobre o ENEM real. Valem como mapa condicional às premissas listadas.\n")


def md_table(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.astype(object).iterrows():
        cells = []
        for c in cols:
            v = r[c]
            cells.append(format(v, floatfmt) if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def section(title: str, body: str, level: int = 2) -> str:
    return f"{'#' * level} {title}\n\n{body.strip()}\n"


def manifest_block(manifest: Dict) -> str:
    keys = ["experiment", "seed", "iterations", "model_version", "data_version", "timestamp_utc", "config_hash",
            "numpy", "python"]
    return "```\n" + "\n".join(f"{k}: {manifest.get(k)}" for k in keys if k in manifest) + "\n```"


def figures_block(paths: Sequence[str], rel_to: str = "") -> str:
    import os
    return "\n".join(f"![{os.path.basename(p)}]({os.path.relpath(p, rel_to) if rel_to else p})" for p in paths)
