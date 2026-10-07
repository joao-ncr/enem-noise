"""Gera docs/model_cards/*.md a partir dos ModelCard no código (fonte única de verdade)."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from enemnoise.simulation.distributions import MODELS  # noqa: E402

out = ROOT / "docs" / "model_cards"
out.mkdir(parents=True, exist_ok=True)
for k, m in MODELS.items():
    (out / f"{k}.md").write_text(m.card.to_markdown(), encoding="utf-8")
    print("escrito", out / f"{k}.md")
