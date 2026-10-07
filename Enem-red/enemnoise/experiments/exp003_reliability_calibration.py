"""Experimento 003 — confiabilidade (ICC/SEM) por sigma + filtro de consistência com alvos observáveis."""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from ..analysis.reliability import reliability_report
from ..calibration import consistency_scan
from ..models.competency import NoiseParams
from ..models.evaluator import Panel
from ..providers.base import DataProvider
from ..providers.simulated import SimulatedDataProvider
from ..reporting import BANNER, manifest_block, md_table, section
from ..simulation.engine import SimulationEngine
from ..simulation.population import PopulationPrior
from .common import make_manifest, prepare, write_json


def run(config: dict, outdir="results/exp003", quick: bool = False, provider: Optional[DataProvider] = None) -> dict:
    out = prepare(outdir)
    seed = config["seed"]
    m = 5_000 if quick else config["n_essays"]
    prior = PopulationPrior(tuple(config["population"]["mu"]), config["population"]["tau"], config["population"]["rho"])
    rel_rows = []
    for s in config["sigmas"]:
        eng = SimulationEngine("M1", config.get("rule", "inep_2025"), NoiseParams.uniform(s, sigma_u=config.get("sigma_u", 0.15)),
                               Panel.preset("neutro"))
        th = prior.sample(np.random.default_rng(seed), m)
        b = eng.grade_chunked(th, seed + 1)
        rep = reliability_report(b.s1, b.s2)
        t = rep["total"]
        rel_rows.append({"sigma": s, "ICC(1,1)_total": t["icc_1_1"], "ICC(1,2)_total": t["icc_1_k"], "SEM_total_pts": t["sem"],
                         "DP_obs_total": float(np.sqrt(t["var_observed_single"])), "p_terceiro": float(b.third.mean()),
                         "kappa_C3": rep["C3"].get("kappa_quadratico", float("nan")),
                         "ICC_C1": rep["C1"]["icc_1_1"], "ICC_C3": rep["C3"]["icc_1_1"], "ICC_C5": rep["C5"]["icc_1_1"]})
    rel = pd.DataFrame(rel_rows)
    rel.to_csv(out / "reliability_by_sigma.csv", index=False)

    used_synth = provider is None
    provider = provider or SimulatedDataProvider(true_sigma=config["synthetic_true_sigma"], n=10_000 if quick else 50_000, seed=seed)
    tgt = provider.calibration_target()
    cal = consistency_scan(tgt, config["calibration_sigmas"], config.get("sigma_u", 0.15),
                           n=4_000 if quick else 20_000, seed=seed + 2,
                           taus=(0.7, 1.1) if quick else (0.5, 0.7, 0.9, 1.1, 1.3), rhos=(0.7,) if quick else (0.5, 0.7, 0.9))
    # Teste de má especificação: alvo gerado por M1H + painel misto, ajustado com M1 + painel neutro
    mis_prov = SimulatedDataProvider(true_sigma=config["synthetic_true_sigma"], n=10_000 if quick else 50_000, seed=seed,
                                     model="M1H", panel="misto")
    mis = consistency_scan(mis_prov.calibration_target(), config["calibration_sigmas"], config.get("sigma_u", 0.15),
                           n=4_000 if quick else 20_000, seed=seed + 3,
                           taus=(0.7, 1.1) if quick else (0.5, 0.7, 0.9, 1.1, 1.3), rhos=(0.7,) if quick else (0.5, 0.7, 0.9))
    mis_df = pd.DataFrame(mis["fits"])[["sigma", "distance", "tau", "rho", "p_third", "consistent"]]
    mis_df.to_csv(out / "calibration_misspecified.csv", index=False)
    cal_df = pd.DataFrame(cal["fits"])[["sigma", "distance", "tau", "rho", "p_third", "p_banca", "consistent"]]
    cal_df.to_csv(out / "calibration_scan.csv", index=False)
    manifest = make_manifest("exp003_reliability_calibration", config, seed, m, data_version=getattr(provider, "data_version", ""), quick=quick)
    write_json(out / "manifest.json", manifest)
    write_json(out / "calibration.json", {k: v for k, v in cal.items()})
    tprov = "SIMULADO (alvo SINTÉTICO — apenas demonstração do método)" if used_synth else "OBSERVADO (alvo real)"
    body = [BANNER,
            section("1. Confiabilidade por sigma (população HIPOTÉTICA)", md_table(rel, ".4f") +
                    "\n\nICC(1,1): fração da variância observada (por avaliador) que é variância real entre redações. SEM = erro padrão de medida de UM avaliador."),
            section("2. Filtro de consistência com alvo observável",
                    f"Alvo: **{tprov}** — {tgt.source}. Distância: média das distâncias de Wasserstein por competência + diferença de DP do total.\n\n" +
                    md_table(cal_df, ".4f") +
                    f"\n\nSigmas consistentes (tolerância 25%): {cal['consistent_sigmas']}.  \n**Conjunto estreito?** {cal['narrow_consistent_set']}.  \n{cal['warning']}"),
            section("2b. Teste de má especificação (alvo sintético gerado por M1H + painel misto; ajustado com M1 + painel neutro)",
                    f"Sigma verdadeiro do gerador = {config['synthetic_true_sigma']}. Sigma escolhido pelo ajuste = {mis['best_sigma']}; "
                    f"consistentes: {mis['consistent_sigmas']}.\n\n" + md_table(mis_df, ".4f") +
                    "\n\nSe o sigma escolhido difere do verdadeiro, a calibração por marginal é **sensível à especificação** — com dados reais, trate o resultado como faixa, não como valor."),
            section("3. Como tornar isto uma estimativa", "Ver `docs/DADOS_NECESSARIOS.md`: notas por avaliador, taxa real de terceiro corretor e distribuição real por competência permitem fixar sigma e migrar de HIPOTÉTICO para ESTIMADO."),
            section("Manifesto", manifest_block(manifest))]
    (out / "report.md").write_text("\n".join(body), encoding="utf-8")
    return {"reliability": rel, "calibration": cal, "misspecified": mis, "manifest": manifest}
