"""Competências da redação e parâmetros de ruído.

Escala latente: 1 unidade = 1 nível de competência (40 pontos). Os limiares entre níveis
ficam em k±0,5, de modo que a distância entre limiares vizinhos é 1. Assim, sigma é medido
em "níveis" (sigma=0,5 = meio nível = 20 pontos). Esta padronização é uma PREMISSA declarada.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .provenance import Provenance

N_COMP = 5
MAX_LEVEL = 5          # níveis 0..5 -> 0, 40, 80, 120, 160, 200 pontos
STEP = 40
MAX_SCORE = 1000.0
LEVEL_POINTS = tuple(STEP * k for k in range(MAX_LEVEL + 1))
COMPETENCY_NAMES = (
    "C1 – Domínio da modalidade escrita formal",
    "C2 – Compreensão da proposta e repertório",
    "C3 – Seleção e organização de informações (projeto de texto)",
    "C4 – Mecanismos linguísticos de coesão",
    "C5 – Proposta de intervenção",
)


@dataclass(frozen=True)
class NoiseParams:
    """Parâmetros de variabilidade de avaliação (todos em níveis; HIPOTÉTICOS por padrão)."""

    sigma_c: tuple = (0.35,) * N_COMP  # ruído residual por competência (eps_ijc)
    sigma_u: float = 0.15              # efeito avaliador x redação (halo, u_ij)
    sigma_beta: float = 0.1            # dispersão do viés entre avaliadores (beta_j)
    het_slope: float = 0.8             # só usado no modelo M1H (ruído cresce com desempenho)
    provenance: Provenance = Provenance.HIPOTETICO

    def __post_init__(self):
        sc = tuple(float(x) for x in self.sigma_c)
        if len(sc) != N_COMP:
            raise ValueError(f"sigma_c precisa ter {N_COMP} valores")
        if min(sc) < 0 or self.sigma_u < 0 or self.sigma_beta < 0 or self.het_slope < 0:
            raise ValueError("parâmetros de ruído devem ser >= 0")
        object.__setattr__(self, "sigma_c", sc)

    @classmethod
    def uniform(cls, sigma: float, sigma_u: float = 0.15, sigma_beta: float = 0.1,
                het_slope: float = 0.8, provenance: Provenance = Provenance.HIPOTETICO):
        return cls((sigma,) * N_COMP, sigma_u, sigma_beta, het_slope, provenance)

    @classmethod
    def deck_heterogeneous(cls, base: float = 0.5, **kw):
        """Hipótese do deck (C3/C4 mais subjetivas que C1/C5). HIPOTÉTICA, a testar."""
        f = (0.7, 1.0, 1.4, 1.4, 0.7)
        return cls(tuple(base * x for x in f), **kw)

    def with_sigma(self, idx: int, value: float) -> "NoiseParams":
        s = list(self.sigma_c)
        s[idx] = value
        return NoiseParams(tuple(s), self.sigma_u, self.sigma_beta, self.het_slope, self.provenance)

    def to_dict(self) -> dict:
        return {"sigma_c": list(self.sigma_c), "sigma_u": self.sigma_u, "sigma_beta": self.sigma_beta,
                "het_slope": self.het_slope, "provenance": self.provenance.name}

    @classmethod
    def from_dict(cls, d: dict) -> "NoiseParams":
        d = dict(d)
        prov = Provenance[d.pop("provenance", "HIPOTETICO")]
        if "sigma" in d:
            s = d.pop("sigma")
            d["sigma_c"] = (s,) * N_COMP
        return cls(provenance=prov, **d)


@dataclass(frozen=True)
class Competency:
    index: int            # 0..4
    name: str
    sigma: float
    provenance: Provenance

    @property
    def scale(self) -> tuple:
        return LEVEL_POINTS


def competencies(params: NoiseParams) -> list:
    return [Competency(i, COMPETENCY_NAMES[i], params.sigma_c[i], params.provenance) for i in range(N_COMP)]
