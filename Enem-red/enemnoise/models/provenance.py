"""Proveniência de valores: OBSERVADO < ESTIMADO < SIMULADO < HIPOTÉTICO.

Regra de herança: um resultado leva o "pior" rótulo (maior valor) de suas entradas.
Nunca apresentar uma simulação como evidência empírica.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Iterable


class Provenance(IntEnum):
    OBSERVADO = 0   # dado efetivamente observado
    ESTIMADO = 1    # parâmetro derivado de dado real
    SIMULADO = 2    # saída de simulação
    HIPOTETICO = 3  # valor de experimentação sem lastro empírico

    @property
    def label(self) -> str:
        return {0: "OBSERVADO", 1: "ESTIMADO", 2: "SIMULADO", 3: "HIPOTÉTICO"}[int(self)]


def combine(*provs: Provenance) -> Provenance:
    return max(provs) if provs else Provenance.SIMULADO


def result_label(inputs: Iterable[Provenance]) -> str:
    """Rótulo de um resultado de simulação dadas as proveniências das entradas."""
    worst = max(list(inputs) or [Provenance.SIMULADO])
    if worst >= Provenance.HIPOTETICO:
        return "SIMULADO (parâmetros HIPOTÉTICOS)"
    if worst == Provenance.ESTIMADO:
        return "SIMULADO (parâmetros ESTIMADOS de dados reais)"
    return "SIMULADO"


@dataclass(frozen=True)
class Tagged:
    value: Any
    provenance: Provenance
    note: str = ""
