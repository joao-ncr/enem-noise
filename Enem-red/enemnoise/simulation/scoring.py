"""Regra de atribuição da nota final (módulo plugável e versionado).

Regra 2025 conforme fontes secundárias (CONFIRMAR NA CARTILHA OFICIAL antes de usar como EVIDÊNCIA):
  * Dois avaliadores independentes; discrepância se |T1-T2| > 100 ou |s1c-s2c| > 80 em alguma competência.
  * Terceiro avaliador em caso de discrepância; se convergir com pelo menos um dos dois, nota final =
    média das duas notas totais mais próximas (aqui: média por competência do par mais próximo).
  * Se o terceiro não convergir com nenhum, banca de três avaliadores. Modelagem da banca (HIPÓTESE):
    mediana por competência de três novas avaliações.
Zeros por anulação (fuga ao tema, <8 linhas etc.) NÃO são modelados.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import numpy as np


@dataclass(frozen=True)
class ScoringRule:
    name: str
    total_threshold: float = 100.0
    comp_threshold: float = 80.0
    total_inclusive: bool = False   # True: discrepância se |dT| >= 100 (algumas fontes dizem "100 ou mais")
    third_rater: bool = True
    description: str = ""


RULES = {
    "inep_2025": ScoringRule("inep_2025", description="Regra 2025 (fontes secundárias): limiares estritos (>100, >80)."),
    "inep_2025_inclusive": ScoringRule("inep_2025_inclusive", total_inclusive=True,
                                       description="Variante: |dT| >= 100 já é discrepância."),
    "simple_mean": ScoringRule("simple_mean", third_rater=False,
                               description="Média simples dos dois avaliadores, sem terceiro corretor."),
}


def get_rule(name: str) -> ScoringRule:
    try:
        return RULES[name]
    except KeyError:
        raise ValueError(f"regra desconhecida: {name}. Opções: {sorted(RULES)}")


def is_discrepant(rule: ScoringRule, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    dt = np.abs(a.sum(axis=1) - b.sum(axis=1))
    tot = dt >= rule.total_threshold if rule.total_inclusive else dt > rule.total_threshold
    comp = (np.abs(a - b) > rule.comp_threshold).any(axis=1)
    return tot | comp


def consolidate(rule: ScoringRule, s1: np.ndarray, s2: np.ndarray,
                third_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None,
                banca_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None
                ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Retorna (final_por_competencia (N,5), usou_terceiro (N,), usou_banca (N,))."""
    n = s1.shape[0]
    final = (s1 + s2) / 2.0
    used_third = np.zeros(n, dtype=bool)
    used_banca = np.zeros(n, dtype=bool)
    if not rule.third_rater or third_fn is None:
        return final, used_third, used_banca

    idx = np.flatnonzero(is_discrepant(rule, s1, s2))
    if idx.size == 0:
        return final, used_third, used_banca

    a, b = s1[idx], s2[idx]
    s3 = third_fn(idx)
    c13 = ~is_discrepant(rule, a, s3)
    c23 = ~is_discrepant(rule, b, s3)
    t3 = s3.sum(axis=1)
    d13 = np.abs(a.sum(axis=1) - t3)
    d23 = np.abs(b.sum(axis=1) - t3)
    pick13 = c13 & (~c23 | (d13 <= d23))
    pick23 = c23 & ~pick13
    converged = pick13 | pick23
    fin = np.where(pick13[:, None], (a + s3) / 2.0, (b + s3) / 2.0)

    no_conv = ~converged
    if no_conv.any() and banca_fn is not None:
        bidx = idx[no_conv]
        sb = banca_fn(bidx)                       # (m,3,5)
        fin[no_conv] = np.median(sb, axis=1)
        used_banca[bidx] = True
    final[idx] = fin
    used_third[idx] = True
    return final, used_third, used_banca
