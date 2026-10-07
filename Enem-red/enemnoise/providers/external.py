"""Provedor de API externa (futuro). Stub: documenta o contrato esperado."""
from __future__ import annotations

from .base import CalibrationTarget, DataProvider


class ExternalAPIDataProvider(DataProvider):
    """Contrato futuro: GET {base_url}/calibration-target -> JSON compatível com CalibrationTarget;
    GET {base_url}/rater-scores -> notas por avaliador (se o INEP/pesquisadores as disponibilizarem)."""

    name = "external"

    def __init__(self, base_url: str, token: str = ""):
        self.base_url, self.token = base_url, token

    def calibration_target(self) -> CalibrationTarget:
        raise NotImplementedError("ExternalAPIDataProvider ainda não implementado (ver docs/DADOS_NECESSARIOS.md).")
