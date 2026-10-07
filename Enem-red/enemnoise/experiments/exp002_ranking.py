"""Experimento 002 — ranking latente × observado, escalas 10 / 100 / 1.000 redações."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..analysis.ranking import public_ranking_result, ranking_experiment
from ..models.competency import NoiseParams
from ..models.evaluator import Panel
from ..reporting import BANNER, figures_block, manifest_block, md_table, section
from ..simulation.engine import SimulationEngine
from ..simulation.population import PopulationPrior
from ..visualization import rankings as vr
from .common import make_manifest, prepare, write_json


def run(config: dict, outdir="results/exp002", quick: bool = False) -> dict:
    out = prepare(outdir)
    seed = config["seed"]
    R = 10 if quick else config["replicates"]
    sizes = [s for s in config["sizes"] if not (quick and s > 100)]
    prior = PopulationPrior(tuple(config["population"]["mu"]), config["population"]["tau"], config["population"]["rho"])
    rows, figs, details = [], [], {}
    for s in config["sigmas"]:
        eng = SimulationEngine("M1", config.get("rule", "inep_2025"),
                               NoiseParams.uniform(s, sigma_u=config.get("sigma_u", 0.15)), Panel.preset(config.get("panel", "neutro")))
        for m in sizes:
            theta = prior.sample(np.random.default_rng(seed + m), m)
            res = ranking_experiment(eng, theta, R, seed + 100 * m, config["top_fraction"])
            pub = public_ranking_result(res)
            details[f"sigma={s}|M={m}"] = pub
            rows.append({"sigma": s, "M": m, "spearman": res["spearman_mean"], "kendall": res["kendall_mean"],
                         "desloc_medio_rank": res["mean_abs_rank_displacement"],
                         "P(inversao)": res.get("p_inversion_all_pairs", float("nan")),
                         "P(empate)": res.get("p_tie_all_pairs", float("nan")),
                         "P(inv)_so_discretizacao": (res["discretization_only_baseline"] or {}).get("p_inversion", float("nan")),
                         "troca_no_topo": res["frac_of_top_replaced"]})
            if m == max(sizes) and s == config["sigmas"][len(config["sigmas"]) // 2]:
                lab = "SIMULADO (parâmetros HIPOTÉTICOS)"
                a = res["_arrays"]
                figs += [vr.plot_latent_vs_observed(a["latent"], a["obs_first"], out / "figures/latente_vs_observada.png", lab),
                         vr.plot_rank_vs_rank(a["latent"], a["obs_first"], out / "figures/ranking_verdadeiro_vs_observado.png", lab)]
                if "inversion_by_gap" in res:
                    figs.append(vr.plot_inversion_by_gap(res["inversion_by_gap"], out / "figures/inversao_por_gap.png", lab))
    df = pd.DataFrame(rows)
    df.to_csv(out / "ranking_summary.csv", index=False)
    write_json(out / "ranking_details.json", details)
    manifest = make_manifest("exp002_ranking", config, seed, R, quick=quick)
    write_json(out / "manifest.json", manifest)
    body = [BANNER,
            section("1. Pergunta", "Qual a probabilidade de a ordenação pelas notas diferir da ordenação latente apenas pela variabilidade de avaliação?"),
            section("2. Simulação", f"População HIPOTÉTICA (mu={config['population']['mu']}, tau={config['population']['tau']}, rho={config['population']['rho']}); "
                    f"{R} replicações; tamanhos {sizes}.\n\n{manifest_block(manifest)}"),
            section("3. Resultado", md_table(df, ".4f") + "\n\n" + figures_block(figs, str(out)) +
                    "\n\n`P(inv)_so_discretizacao`: inversões que ocorreriam mesmo com avaliadores perfeitos e sem ruído, apenas porque a nota só assume 6 níveis por competência (efeito da ESCALA, não do avaliador). `P(inversao)`: fração de pares (a,b) com T*_a > T*_b em que a nota observada de a é MENOR que a de b. `troca_no_topo`: fração do grupo "
                    f"'top {config['top_fraction']:.0%}' (pela ordem latente) substituída por outros candidatos."),
            section("4. Interpretação (condicional)", "Spearman alto convive com muitas inversões locais entre candidatos próximos. A curva de inversão por "
                    "diferença latente (figura) mostra onde a nota deixa de discriminar. Nada aqui informa o sigma real do ENEM.")]
    (out / "report.md").write_text("\n".join(body), encoding="utf-8")
    return {"summary": df, "details": details, "manifest": manifest}
