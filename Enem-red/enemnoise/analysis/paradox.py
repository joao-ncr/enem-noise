"""ParadoxDetector: procura automaticamente as 6 situações do briefing.

Os limiares abaixo são FIXADOS A PRIORI (HIPOTÉTICOS) e vêm de `ParadoxThresholds`; não devem ser
ajustados depois de ver resultados. O detector também é testado contra cenários de baixo ruído
(taxa de falso positivo), para garantir que ele não "acusa paradoxo em tudo".
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Optional, Sequence


@dataclass(frozen=True)
class ParadoxThresholds:
    inversion_p: float = 0.05            # P1: P(inversão de ranking) >= 5%
    small_delta_points: float = 20.0     # P2: "pequena alteração" = até 20 pontos latentes
    small_change_dp: float = 0.10        # P2: |ΔP(F>=corte)| >= 10 p.p.
    overlap: float = 0.50                # P3: coeficiente de sobreposição >= 0.5 com latentes distintos
    boundary_p: float = 0.05             # P4: min(P(F>=c), 1-P(F>=c)) >= 5% (candidato na fronteira)
    instability_modal_band: float = 0.90 # P5: faixa modal com prob < 90% => resultado classificatório instável
    nonprop_ratio: float = 2.0           # P6: razão consequência-por-ponto (menor pert. / maior pert.)
    nonprop_min_dp: float = 0.05         # P6: ΔP mínimo da menor perturbação


@dataclass
class Finding:
    id: int
    name: str
    triggered: bool
    value: Optional[float]
    threshold: float
    detail: str
    provenance: str

    def to_dict(self):
        return asdict(self)


class ParadoxDetector:
    def __init__(self, thresholds: Optional[ParadoxThresholds] = None):
        self.t = thresholds or ParadoxThresholds()

    # P1 -------------------------------------------------------------------------------
    def inversion(self, cmp: dict) -> Finding:
        v = cmp.get("p_ranking_inversion")
        trig = v is not None and v >= self.t.inversion_p
        return Finding(1, "Inversão de ranking", bool(trig), v, self.t.inversion_p,
                       f"{cmp['a']} vs {cmp['b']}: ordem latente {cmp.get('latent_order', 'n/d')}; "
                       f"P(inversão)={v if v is None else round(v, 4)}; P(empate)={cmp['p_tie']:.4f}", cmp["provenance"])

    # P2 -------------------------------------------------------------------------------
    def small_change_big_consequence(self, sens: dict) -> Finding:
        best, best_row = 0.0, None
        for r in sens["rows"]:
            if abs(r["delta_latent_points"]) <= self.t.small_delta_points:
                for c, dp in r["delta_p_cutoff"].items():
                    if abs(dp) > abs(best):
                        best, best_row = dp, (r["perturbation"], c)
        trig = abs(best) >= self.t.small_change_dp
        return Finding(2, "Pequena alteração, grande consequência", bool(trig), abs(best), self.t.small_change_dp,
                       f"Maior |ΔP(F>=corte)| para perturbação <= {self.t.small_delta_points:g} pts: {best:+.4f} "
                       f"({best_row})", sens["provenance"])

    # P3 -------------------------------------------------------------------------------
    def overlap(self, cmp: dict) -> Finding:
        v = cmp["overlap_coefficient"]
        trig = cmp["latent_diff"] != 0 and v >= self.t.overlap
        return Finding(3, "Sobreposição de distribuições", bool(trig), v, self.t.overlap,
                       f"Diferença latente {cmp['latent_diff']:+.0f} pts, sobreposição={v:.3f}", cmp["provenance"])

    # P4 -------------------------------------------------------------------------------
    def boundary(self, stats: dict, cutoff: float, provenance: str) -> Finding:
        p = stats["classification_impact"][str(cutoff)]["p_ge"]
        v = min(p, 1 - p)
        return Finding(4, "Fronteira classificatória", bool(v >= self.t.boundary_p), v, self.t.boundary_p,
                       f"Corte {cutoff:g}: P(F>=corte)={p:.4f}; probabilidade do lado minoritário={v:.4f}", provenance)

    # P5 -------------------------------------------------------------------------------
    def instability(self, stats: dict, provenance: str) -> Finding:
        modal = max(stats["band_probs"].values())
        return Finding(5, "Instabilidade classificatória (faixas)", bool(modal < self.t.instability_modal_band),
                       modal, self.t.instability_modal_band,
                       f"Faixa mais provável tem prob {modal:.4f}; terceiro corretor em {stats['p_third_rater']:.1%}", provenance)

    # P6 -------------------------------------------------------------------------------
    def nonproportionality(self, sens: dict) -> Finding:
        rows = [r for r in sens["rows"] if r["delta_latent_points"] != 0 and r["delta_p_cutoff"]]
        if len(rows) < 2:
            return Finding(6, "Não proporcionalidade", False, None, self.t.nonprop_ratio,
                           "Requer >= 2 perturbações de tamanhos distintos.", sens["provenance"])
        rows.sort(key=lambda r: abs(r["delta_latent_points"]))
        s, l = rows[0], rows[-1]
        ds = max(abs(x) for x in s["delta_p_cutoff"].values()); dl = max(abs(x) for x in l["delta_p_cutoff"].values())
        cs, cl = ds / abs(s["delta_latent_points"]), dl / abs(l["delta_latent_points"])
        ratio = cs / cl if cl > 0 else float("inf") if cs > 0 else 0.0
        trig = ds >= self.t.nonprop_min_dp and ratio >= self.t.nonprop_ratio
        return Finding(6, "Não proporcionalidade", bool(trig), ratio, self.t.nonprop_ratio,
                       f"Consequência por ponto: menor pert.={cs:.5f}/pt, maior pert.={cl:.5f}/pt", sens["provenance"])

    def scan(self, cmp: Optional[dict] = None, sens: Optional[dict] = None, stats: Optional[dict] = None,
             cutoffs: Sequence[float] = ()) -> List[Finding]:
        out: List[Finding] = []
        if cmp:
            out += [self.inversion(cmp), self.overlap(cmp)]
        if sens:
            out += [self.small_change_big_consequence(sens), self.nonproportionality(sens)]
        if stats is not None:
            prov = (cmp or sens or {}).get("provenance", "SIMULADO (parâmetros HIPOTÉTICOS)")
            out += [self.boundary(stats, c, prov) for c in cutoffs if str(c) in stats["classification_impact"]]
            out.append(self.instability(stats, prov))
        return out
