"""Modelos de erro de avaliação concorrentes (cada um com ModelCard).

Todos partem de:  y*_ijc = theta_ic' + beta_j + u_ij + eps_ijc
  theta' = (1-shrink)*theta + shrink*2,5   (tendência central do avaliador)
  beta_j  : viés do avaliador j (perfil + N(0, sigma_beta^2))
  u_ij    : efeito avaliador x redação (halo), compartilhado pelas 5 competências
  eps_ijc : ruído residual, sd = sigma_c * kappa_j (* fator de nível no M1H)

e diferem na conversão para pontos (to_points) e no ruído (noise_sd).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from ..models.competency import MAX_LEVEL, STEP, NoiseParams


@dataclass(frozen=True)
class ModelCard:
    key: str
    name: str
    hypothesis: str
    justification: str
    parameters: str
    limitations: str
    implications: str

    def to_markdown(self) -> str:
        return (f"# {self.key} — {self.name}\n\n"
                f"**Hipótese.** {self.hypothesis}\n\n**Justificativa.** {self.justification}\n\n"
                f"**Parâmetros.** {self.parameters}\n\n**Limitações.** {self.limitations}\n\n"
                f"**Implicações.** {self.implications}\n\n"
                f"_Todos os parâmetros são HIPOTÉTICOS até calibração com dados reais._\n")


class ErrorModel(ABC):
    card: ModelCard
    discrete: bool = True

    def noise_sd(self, theta: np.ndarray, params: NoiseParams) -> np.ndarray:
        return np.asarray(params.sigma_c, dtype=float)[None, :]

    @abstractmethod
    def to_points(self, y: np.ndarray) -> np.ndarray: ...

    def latent_obs(self, theta, rng, beta, kappa, shrink, params: NoiseParams) -> np.ndarray:
        n = theta.shape[0]
        y = theta * (1.0 - shrink[:, None]) + 2.5 * shrink[:, None] + beta[:, None]
        y = y + rng.normal(0.0, params.sigma_u, (n, 1))
        y = y + rng.normal(0.0, 1.0, (n, theta.shape[1])) * self.noise_sd(theta, params) * kappa[:, None]
        return y

    def observe(self, theta, rng, beta, kappa, shrink, params: NoiseParams) -> np.ndarray:
        return self.to_points(self.latent_obs(theta, rng, beta, kappa, shrink, params))


class M0Normal(ErrorModel):
    discrete = False
    card = ModelCard(
        "M0", "Normal contínua truncada em [0,200]",
        "A nota por competência é contínua: 40*y* com ruído gaussiano, truncada em 0..200.",
        "Linha de base clássica (teoria clássica dos testes); permite comparar com o modelo discreto.",
        "sigma_c, sigma_u, sigma_beta (em níveis).",
        "Ignora que a nota real só assume 6 níveis por competência; subestima saltos de 40 pontos.",
        "Se M0 e M1 divergem nas conclusões, a discretização importa e M0 não deve ser usado sozinho.")

    def to_points(self, y):
        return np.clip(STEP * y, 0.0, STEP * MAX_LEVEL)


class M1Ordinal(ErrorModel):
    discrete = True
    card = ModelCard(
        "M1", "Ordinal por limiares sobre variável latente",
        "O avaliador observa y* e atribui o nível k tal que k-0,5 < y* <= k+0,5 (limiares equidistantes).",
        "Reflete a escala real de 6 níveis (0,40,...,200) por competência.",
        "sigma_c, sigma_u, sigma_beta; limiares fixos em k±0,5 (premissa).",
        "Limiares equidistantes são hipótese; níveis reais podem ter 'larguras' diferentes.",
        "Torna a discrepância mínima observável igual a 40 pontos em uma competência.")

    def to_points(self, y):
        return STEP * np.clip(np.floor(y + 0.5), 0, MAX_LEVEL)


class M1HOrdinalHet(M1Ordinal):
    card = ModelCard(
        "M1H", "Ordinal com ruído crescente no desempenho (heterocedástico)",
        "O ruído cresce com o nível latente: sd = sigma_c*(1 + het_slope*theta/5). Hipótese inspirada no deck "
        "(mais subjetividade no topo) — TRATADA COMO HIPÓTESE, não como fato.",
        "Permite testar se a instabilidade concentra-se no topo da escala.",
        "sigma_c, sigma_u, sigma_beta, het_slope.",
        "A forma funcional do crescimento é arbitrária; sem dados não há como validá-la.",
        "Se resultados no topo só aparecem sob M1H, a conclusão depende da hipótese de heterocedasticidade.")

    def noise_sd(self, theta, params):
        base = np.asarray(params.sigma_c, dtype=float)[None, :]
        return base * (1.0 + params.het_slope * np.clip(theta, 0, MAX_LEVEL) / MAX_LEVEL)


MODELS = {"M0": M0Normal(), "M1": M1Ordinal(), "M1H": M1HOrdinalHet()}


def get_model(key: str) -> ErrorModel:
    try:
        return MODELS[key]
    except KeyError:
        raise ValueError(f"modelo desconhecido: {key}. Opções: {sorted(MODELS)}")
