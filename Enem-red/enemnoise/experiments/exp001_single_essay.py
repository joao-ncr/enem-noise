"""Experimento 001 — uma redação, muitas avaliações (pré-registrado em experiments/exp001_single_essay/prereg.md).

Critérios fixados a priori (HIPOTÉTICOS), ver config.yaml:
  H1 (variabilidade relevante) para uma célula se  DP(nota) >= sd_threshold  OU  P(|nota - E[nota]| >= err_threshold) >= p_threshold.
  H0 caso contrário. O desvio é medido em torno da média simulada (ruído puro), separando viés de variância.
O resultado é um MAPA em função de sigma — não uma conclusão sobre o ENEM real.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

from ..analysis.compare import compare_pair
from ..analysis.paradox import ParadoxDetector
from ..analysis.sensitivity import competency_variability_heatmap
from ..models.competency import NoiseParams
from ..models.essay import Essay
from ..models.evaluator import Panel
from ..reporting import BANNER, figures_block, manifest_block, md_table, section
from ..simulation.engine import SimulationEngine
from ..simulation.monte_carlo import run_grid
from ..visualization import distributions as vd
from .common import make_manifest, prepare, write_json


def run(config: dict, outdir="results/exp001", quick: bool = False) -> Dict:
    out = prepare(outdir)
    n = 10_000 if quick else config["iterations"]
    seed = config["seed"]
    crit = config["criteria"]
    cutoffs = config.get("cutoffs", [])
    essays = [Essay.uniform(f"nivel_{lv:g}", lv) for lv in config["essay_levels"]]

    # ---- Fase 1: grade de variabilidade -----------------------------------------------------
    rows = run_grid(essays, config["models"], config["panels"], config["sigmas"], config["sigma_us"], n, seed, cutoffs,
                    config.get("rule", "inep_2025"), config.get("sigma_beta", 0.1))
    recs = []
    for r in rows:
        st = r["stats"]
        sd, pn = st["std"], st["noise_only"]["p_abs_dev_ge_threshold"]
        pl = st["vs_latent"]["p_abs_err_ge_threshold"]
        h1 = (sd >= crit["sd_threshold"]) or (pn >= crit["p_threshold"])
        rec = {"model": r["model"], "panel": r["panel"], "sigma": r["sigma"], "sigma_u": r["sigma_u"], "essay": r["essay"],
               "T_latente": r["latent_total"], "media": st["mean"], "dp": sd, "q2.5": st["quantiles"]["2.5"],
               "q97.5": st["quantiles"]["97.5"], "p_terceiro": st["p_third_rater"], "p_banca": st["p_banca"],
               "p_dev40_ruido": pn, "p_err40_vs_latente": pl, "vies": st["vs_latent"]["bias"],
               "gap_medio_pares": st["rater_gap"]["mean_abs_total_diff"], "H1": h1}
        for c in cutoffs:
            rec[f"P(>= {c:g})"] = st["classification_impact"][str(c)]["p_ge"]
        recs.append(rec)
    grid = pd.DataFrame(recs)
    grid.to_csv(out / "grid.csv", index=False)

    # sigma crítico: menor sigma (da grade) em que H1 é satisfeito, por configuração
    crit_rows = []
    for key, g in grid.groupby(["model", "panel", "sigma_u", "essay"]):
        g = g.sort_values("sigma")
        hit = g[g["H1"]]
        crit_rows.append({"model": key[0], "panel": key[1], "sigma_u": key[2], "essay": key[3],
                          "sigma_critico": float(hit["sigma"].iloc[0]) if len(hit) else None})
    crit_df = pd.DataFrame(crit_rows)
    crit_df.to_csv(out / "sigma_critico.csv", index=False)

    # ---- Fase 2: A vs B (1 nível em 1 competência) -------------------------------------------
    A = Essay("A", tuple(config["pair"]["A"])); B = Essay("B", tuple(config["pair"]["B"]))
    det = ParadoxDetector()
    cmp_recs = []
    for k, (m, pn, s, su) in enumerate([(m, pn, s, su) for m in config["models"] for pn in config["panels"]
                                         for s in config["sigmas"] for su in config["sigma_us"]]):
        eng = SimulationEngine(m, config.get("rule", "inep_2025"), NoiseParams.uniform(s, sigma_u=su,
                               sigma_beta=config.get("sigma_beta", 0.1)), Panel.preset(pn))
        sd = int(np.random.SeedSequence([seed, 1000 + k]).generate_state(1)[0])
        c = compare_pair(eng, A, B, n, sd)
        cmp_recs.append({"model": m, "panel": pn, "sigma": s, "sigma_u": su, "dif_latente": c["latent_diff"],
                         "P(A>B)": c["p_a_gt_b"], "P(empate)": c["p_tie"], "P(inversao)": c["p_ranking_inversion"],
                         "sobreposicao": c["overlap_coefficient"],
                         "P1_inversao": det.inversion(c).triggered, "P3_sobreposicao": det.overlap(c).triggered})
    cmp_df = pd.DataFrame(cmp_recs)
    cmp_df.to_csv(out / "compare_AB.csv", index=False)

    # ---- Fase 3: P(1000 | desempenho latente) (hipótese do deck: depende de alocação de corretores) --------
    p1000 = []
    for pn in config["panels"]:
        for s in config["sigmas"]:
            eng = SimulationEngine("M1", config.get("rule", "inep_2025"),
                                   NoiseParams.uniform(s, sigma_u=config["sigma_us"][-1], sigma_beta=config.get("sigma_beta", 0.1)),
                                   Panel.preset(pn))
            for lv in config["p1000_levels"]:
                r = eng.run_essay(Essay.uniform("p1000", lv), n, seed + 5)
                p = float((r.final >= 1000).mean())
                p1000.append({"panel": pn, "sigma": s, "theta_nivel": lv, "P(nota=1000)": p,
                              "ep_mc": float(np.sqrt(p * (1 - p) / n))})
    p1000_df = pd.DataFrame(p1000)
    p1000_df.to_csv(out / "p1000_curve.csv", index=False)

    # ---- Figuras -------------------------------------------------------------------------------
    figs = []
    mid_s = config["sigmas"][len(config["sigmas"]) // 2]
    eng = SimulationEngine("M1", config.get("rule", "inep_2025"),
                           NoiseParams.uniform(mid_s, sigma_u=config["sigma_us"][-1]), Panel.preset("neutro"))
    ess_mid = essays[len(essays) // 2]
    rr = eng.run_essay(ess_mid, n, seed + 9, cutoffs)
    figs.append(vd.plot_distribution(rr.final, out / "figures/distribuicao.png",
                                     f"Distribuição simulada ({ess_mid.id}, sigma={mid_s:g}, M1)", rr.provenance,
                                     rr.latent_total, cutoffs))
    groups = {}
    for pn in config["panels"]:
        e = SimulationEngine("M1", config.get("rule", "inep_2025"),
                             NoiseParams.uniform(mid_s, sigma_u=config["sigma_us"][-1]), Panel.preset(pn))
        groups[pn] = e.run_essay(ess_mid, min(n, 20000), seed + 11).final
    figs.append(vd.plot_boxplot(groups, out / "figures/boxplot_paineis.png", "Nota final por painel de avaliadores", rr.provenance))
    ra = eng.run_essay(A, n, seed + 13); rb = eng.run_essay(B, n, seed + 14)
    figs.append(vd.plot_density_overlap(ra.final, rb.final, "A", "B", out / "figures/sobreposicao_AB.png", rr.provenance,
                                        compare_pair(eng, A, B, n, seed + 15)["overlap_coefficient"]))
    hm = competency_variability_heatmap(eng, ess_mid, config["sigmas"], min(n, 20000), seed + 17)
    figs.append(vd.plot_heatmap(hm["std_final"], [f"C{i + 1}" for i in range(5)], hm["sigmas"],
                                out / "figures/heatmap_competencia_sigma.png",
                                "Competência × variabilidade (só aquela competência varia)", rr.provenance))

    # ---- Relatório ------------------------------------------------------------------------------
    n_cells, n_h1 = len(grid), int(grid["H1"].sum())
    manifest = make_manifest("exp001_single_essay", config, seed, n, quick=quick)
    write_json(out / "manifest.json", manifest)
    resumo = grid.groupby(["model", "sigma"]).agg(dp_medio=("dp", "mean"), p_terceiro_medio=("p_terceiro", "mean"),
                                                  frac_H1=("H1", "mean")).reset_index()
    h0 = grid[~grid["H1"]]
    body = [BANNER,
            section("1. Observação (contexto; nenhum dado real usado)",
                    "Cada competência é avaliada em 6 níveis (0–200, passo 40); duas avaliações independentes são consolidadas pela "
                    "regra 2025 (fontes secundárias; confirmar na Cartilha). Não há notas por avaliador públicas para calibrar sigma."),
            section("2. Hipóteses e critérios (fixados antes da execução)",
                    f"H0: DP < {crit['sd_threshold']} pts **e** P(|nota − E[nota]| ≥ {crit['err_threshold']}) < {crit['p_threshold']:.0%}.  \n"
                    f"H1: caso contrário. Limiares HIPOTÉTICOS (`config.yaml`)."),
            section("3. Simulação", f"{n_cells} células na fase 1 × {n:,} iterações; modelos {config['models']}; painéis {config['panels']}; "
                    f"sigma ∈ {config['sigmas']}; sigma_u ∈ {config['sigma_us']}.  \n"
                    f"Manifesto:\n\n{manifest_block(manifest)}"),
            section("4. Resultado",
                    f"**H1 satisfeito em {n_h1} de {n_cells} células ({n_h1 / n_cells:.0%}); H0 em {n_cells - n_h1}.**\n\n"
                    "Resumo por modelo e sigma:\n\n" + md_table(resumo) +
                    "\n\nSigma crítico (menor sigma da grade com H1):\n\n" + md_table(crit_df.fillna("n/a")) +
                    "\n\nFase 2 — A=[4,4,4,4,4] vs B=[4,4,3,4,4] (diferença latente de 40 pts):\n\n" +
                    md_table(cmp_df.groupby(["model", "sigma"]).agg(P_A_gt_B=("P(A>B)", "mean"), P_empate=("P(empate)", "mean"),
                             P_inversao=("P(inversao)", "mean"), sobreposicao=("sobreposicao", "mean")).reset_index()) +
                    "\n\nFase 3 — P(nota = 1000 | desempenho latente), M1:\n\n" +
                    md_table(p1000_df[p1000_df["theta_nivel"] >= 4.5].pivot_table(index=["panel", "sigma"], columns="theta_nivel",
                             values="P(nota=1000)").reset_index(), ".4f") +
                    "\n\n" + figures_block(figs, str(out))),
            section("5. Evidências contrárias à hipótese principal (H0)",
                    (f"{len(h0)} células satisfazem H0 (variabilidade irrelevante pelo critério pré-fixado). Menores sigma: "
                     f"{sorted(h0['sigma'].unique().tolist())}. Ver `grid.csv`.") if len(h0) else
                    "Nenhuma célula satisfez H0 nesta grade; grade pode não incluir sigmas suficientemente baixos."),
            section("6. Interpretação (condicional)",
                    "A discrepância relevante aparece **a partir de certo sigma**; abaixo dele, não. Este experimento não diz qual é o sigma real. "
                    "A decisão sobre se a nota é 'estável o bastante' exige calibrar sigma (notas por avaliador ou taxa real de terceiro corretor) "
                    "— ver exp003 e `docs/DADOS_NECESSARIOS.md`. Diferenças entre M0 e M1 indicam o quanto a discretização importa.")]
    (out / "report.md").write_text("\n".join(body), encoding="utf-8")
    return {"grid": grid, "sigma_critico": crit_df, "compare": cmp_df, "p1000": p1000_df, "figures": figs, "manifest": manifest}
