from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, model_validator


class EssayIn(BaseModel):
    id: str = "essay"
    theta: Optional[List[float]] = Field(None, description="Níveis latentes 0..5 por competência (5 valores)")
    points: Optional[List[float]] = Field(None, description="Alternativa: pontos 0..200 por competência")

    @model_validator(mode="after")
    def _check(self):
        v = self.theta if self.theta is not None else self.points
        if v is None or len(v) != 5:
            raise ValueError("informe theta (níveis) ou points (pontos) com 5 valores")
        return self


class PanelIn(BaseModel):
    preset: Optional[str] = None
    name: str = "custom"
    profiles: Optional[List[Dict[str, Any]]] = None

    @model_validator(mode="after")
    def _check(self):
        if not self.preset and not self.profiles:
            self.preset = "neutro"
        return self


class ParametersIn(BaseModel):
    sigma: Optional[float] = Field(None, ge=0, description="atalho: mesmo sigma nas 5 competências")
    sigma_c: Optional[List[float]] = None
    sigma_u: float = Field(0.15, ge=0)
    sigma_beta: float = Field(0.1, ge=0)
    het_slope: float = Field(0.8, ge=0)


class SimulateRequest(BaseModel):
    essay_profile: EssayIn
    evaluator_profile: PanelIn = PanelIn()
    model: str = "M1"
    scoring_rule: str = "inep_2025"
    parameters: ParametersIn = ParametersIn(sigma=0.35)
    iterations: int = Field(10_000, ge=100, le=2_000_000)
    seed: int = 12345
    cutoffs: List[float] = []
    return_scores: int = Field(0, ge=0, le=5000, description="Tamanho da amostra de notas a devolver")
    persist: bool = True


class CompareRequest(BaseModel):
    essays: List[EssayIn] = Field(..., min_length=2, max_length=10)
    evaluator_profile: PanelIn = PanelIn()
    model: str = "M1"
    scoring_rule: str = "inep_2025"
    parameters: ParametersIn = ParametersIn(sigma=0.35)
    iterations: int = Field(20_000, ge=100, le=1_000_000)
    seed: int = 12345
    persist: bool = True


class SensitivityRequest(BaseModel):
    essay_profile: EssayIn
    perturbations: List[Dict[str, float]] = Field(..., min_length=1, max_length=20,
                                                  description='Ex.: [{"2": 0.5}] = +0,5 nível (20 pts) na C3')
    evaluator_profile: PanelIn = PanelIn()
    model: str = "M1"
    scoring_rule: str = "inep_2025"
    parameters: ParametersIn = ParametersIn(sigma=0.35)
    iterations: int = Field(20_000, ge=100, le=1_000_000)
    seed: int = 12345
    cutoffs: List[float] = []
    persist: bool = True


class ScenarioRequest(BaseModel):
    name: str
    iterations: int = Field(20_000, ge=100, le=1_000_000)
    seed: int = 12345
    persist: bool = True
