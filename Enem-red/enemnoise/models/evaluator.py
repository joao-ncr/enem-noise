"""Perfis HIPOTÉTICOS de avaliadores. Não representam avaliadores reais do ENEM."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .provenance import Provenance


@dataclass(frozen=True)
class EvaluatorProfile:
    name: str
    beta: float = 0.0     # viés (negativo = rigoroso, positivo = permissivo), em níveis
    kappa: float = 1.0    # multiplicador do ruído (>1 = mais variável)
    shrink: float = 0.0   # tendência central: puxa a avaliação para o nível 2,5
    weight: float = 1.0   # peso no sorteio do painel
    provenance: Provenance = Provenance.HIPOTETICO

    def to_dict(self) -> dict:
        return {"name": self.name, "beta": self.beta, "kappa": self.kappa, "shrink": self.shrink,
                "weight": self.weight, "provenance": self.provenance.name}

    @classmethod
    def from_dict(cls, d: dict) -> "EvaluatorProfile":
        d = dict(d)
        d["provenance"] = Provenance[d.get("provenance", "HIPOTETICO")]
        return cls(**d)


PRESET_PROFILES = {
    "neutro": EvaluatorProfile("neutro"),
    "rigoroso": EvaluatorProfile("rigoroso", beta=-0.3),
    "permissivo": EvaluatorProfile("permissivo", beta=0.3),
    "alta_variabilidade": EvaluatorProfile("alta_variabilidade", kappa=1.6),
    "baixa_variabilidade": EvaluatorProfile("baixa_variabilidade", kappa=0.6),
    "tendencia_central": EvaluatorProfile("tendencia_central", shrink=0.25),
}


def panel_names() -> list:
    return sorted(list(PRESET_PROFILES) + ["misto"])


@dataclass(frozen=True)
class Panel:
    """Conjunto de perfis do qual os avaliadores são sorteados (independentemente) a cada correção."""

    profiles: tuple
    name: str = "custom"

    def __post_init__(self):
        object.__setattr__(self, "profiles", tuple(self.profiles))
        if not self.profiles:
            raise ValueError("painel vazio")

    @property
    def weights(self) -> np.ndarray:
        w = np.array([p.weight for p in self.profiles], dtype=float)
        return w / w.sum()

    @property
    def betas(self): return np.array([p.beta for p in self.profiles])
    @property
    def kappas(self): return np.array([p.kappa for p in self.profiles])
    @property
    def shrinks(self): return np.array([p.shrink for p in self.profiles])

    @classmethod
    def preset(cls, name: str) -> "Panel":
        if name == "misto":
            return cls((PRESET_PROFILES["rigoroso"], PRESET_PROFILES["permissivo"]), "misto")
        if name in PRESET_PROFILES:
            return cls((PRESET_PROFILES[name],), name)
        raise ValueError(f"painel desconhecido: {name}. Opções: {panel_names()}")

    @classmethod
    def from_dict(cls, d) -> "Panel":
        if isinstance(d, str):
            return cls.preset(d)
        if "preset" in d:
            return cls.preset(d["preset"])
        return cls(tuple(EvaluatorProfile.from_dict(p) for p in d["profiles"]), d.get("name", "custom"))

    def to_dict(self) -> dict:
        return {"name": self.name, "profiles": [p.to_dict() for p in self.profiles]}
