"""Executa o experimento a partir do config.yaml desta pasta.  Uso: python run.py [--quick] [--microdata caminho.csv]"""
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from enemnoise.experiments import exp001_single_essay as exp  # noqa: E402

if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    cfg = yaml.safe_load((here / "config.yaml").read_text(encoding="utf-8"))
    quick = "--quick" in sys.argv
    out = ROOT / "results" / "exp001"
    kw = {}
    if "--microdata" in sys.argv and "exp001" == "exp003":
        from enemnoise.providers.real import RealDataProvider
        kw["provider"] = RealDataProvider(sys.argv[sys.argv.index("--microdata") + 1], year_label="ENEM-2025")
    exp.run(cfg, out, quick=quick, **kw)
    print("OK ->", out / "report.md")
