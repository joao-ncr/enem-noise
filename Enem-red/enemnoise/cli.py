"""CLI: python -m enemnoise <comando>"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _cfg(name: str) -> dict:
    return yaml.safe_load((ROOT / "experiments" / name / "config.yaml").read_text(encoding="utf-8"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="enemnoise", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for e in ("exp001", "exp002", "exp003"):
        p = sub.add_parser(e, help=f"executa o experimento {e}")
        p.add_argument("--quick", action="store_true", help="versão rápida (menos iterações)")
        p.add_argument("--out", default=None)
        if e == "exp003":
            p.add_argument("--microdata", default=None, help="CSV dos microdados do ENEM (baixar manualmente)")
            p.add_argument("--year", default="ENEM-2025")
    sub.add_parser("all", help="executa exp001, exp002, exp003").add_argument("--quick", action="store_true")
    s = sub.add_parser("serve", help="sobe a API (uvicorn)")
    s.add_argument("--host", default="127.0.0.1"); s.add_argument("--port", type=int, default=8000)
    r = sub.add_parser("real-target", help="calcula alvos de calibração dos microdados reais")
    r.add_argument("--microdata", required=True); r.add_argument("--year", default="ENEM-2025")
    r.add_argument("--out", default="data/processed/calibration_target.json")
    c = sub.add_parser("simulate", help="simula a partir de um JSON (mesmo formato de POST /simulate)")
    c.add_argument("--config", required=True)
    a = ap.parse_args(argv)

    if a.cmd in ("exp001", "exp002", "exp003", "all"):
        from .experiments import exp001_single_essay, exp002_ranking, exp003_reliability_calibration
        mods = {"exp001": exp001_single_essay, "exp002": exp002_ranking, "exp003": exp003_reliability_calibration}
        todo = ["exp001", "exp002", "exp003"] if a.cmd == "all" else [a.cmd]
        for name in todo:
            out = getattr(a, "out", None) or f"results/{name}"
            kw = {}
            if name == "exp003" and getattr(a, "microdata", None):
                from .providers.real import RealDataProvider
                kw["provider"] = RealDataProvider(a.microdata, year_label=a.year)
            mods[name].run(_cfg({"exp001": "exp001_single_essay", "exp002": "exp002_ranking",
                                 "exp003": "exp003_reliability_calibration"}[name]), out, quick=a.quick, **kw)
            print(f"[{name}] relatório: {out}/report.md")
    elif a.cmd == "serve":
        import uvicorn
        uvicorn.run("enemnoise.api.app:app", host=a.host, port=a.port)
    elif a.cmd == "real-target":
        from .providers.real import RealDataProvider
        from .simulation.summary import to_jsonable
        t = RealDataProvider(a.microdata, year_label=a.year).calibration_target()
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(to_jsonable({"source": t.source, "provenance": t.provenance.name,
            "comp_mean": t.comp_mean, "comp_probs": t.comp_probs, "total_mean": t.total_mean, "total_std": t.total_std,
            "n_valid": t.n_valid, "n_1000": t.n_1000, "p_zero": t.p_zero, "extra": t.extra}), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OBSERVADO] alvo salvo em {a.out}: n={t.n_valid}, notas 1000={t.n_1000}, média total={t.total_mean:.1f}")
    elif a.cmd == "simulate":
        from .api.controllers import runs
        from .api.schemas.models import SimulateRequest
        req = SimulateRequest(**json.loads(Path(a.config).read_text(encoding="utf-8"))).model_dump()
        persist = req.pop("persist", True)
        print(json.dumps(runs.execute("simulate", req, persist), ensure_ascii=False, indent=2)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
