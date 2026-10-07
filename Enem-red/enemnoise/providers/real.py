"""Provedor de DADOS REAIS: microdados do ENEM (INEP), baixados MANUALMENTE pelo usuário.

O ambiente de desenvolvimento deste projeto não tem acesso ao site do INEP; por isso este provedor lê um
arquivo local. Colunas esperadas (nomes padrão dos microdados; configuráveis):
  NU_NOTA_COMP1..NU_NOTA_COMP5, NU_NOTA_REDACAO, TP_STATUS_REDACAO (1 = sem problemas)
Os microdados públicos trazem a nota FINAL por competência, não a nota de cada avaliador.
Resultados derivados são ESTIMADOS/OBSERVADOS, nunca confundir com os SIMULADOS.
"""
from __future__ import annotations

import os
from typing import Optional

import numpy as np
import pandas as pd

from ..models.provenance import Provenance
from .base import CalibrationTarget, DataProvider
from .simulated import target_from_finals

COMP_COLS = [f"NU_NOTA_COMP{i}" for i in range(1, 6)]


class RealDataProvider(DataProvider):
    name = "real"

    def __init__(self, path: str, year_label: str = "ENEM-?", sep: str = ";", encoding: str = "latin-1",
                 comp_cols=None, total_col: str = "NU_NOTA_REDACAO", status_col: str = "TP_STATUS_REDACAO",
                 valid_status: int = 1, nrows: Optional[int] = None):
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Arquivo não encontrado: {path}. Baixe os microdados do ENEM no portal do INEP "
                f"(ver docs/DADOS_NECESSARIOS.md) e coloque em data/raw/.")
        self.path, self.year_label = path, year_label
        self.data_version = f"{year_label}:{os.path.basename(path)}:{os.path.getsize(path)}"
        self.comp_cols = comp_cols or COMP_COLS
        self.total_col, self.status_col, self.valid_status = total_col, status_col, valid_status
        usecols = list(self.comp_cols) + [total_col, status_col]
        self.df = pd.read_csv(path, sep=sep, encoding=encoding, usecols=usecols, nrows=nrows)

    def calibration_target(self, exclude_zero: bool = True) -> CalibrationTarget:
        df = self.df.dropna(subset=list(self.comp_cols) + [self.total_col])
        df = df[df[self.status_col] == self.valid_status]
        n_all = len(df)
        n_1000 = int((df[self.total_col] == 1000).sum())
        p_zero = float((df[self.total_col] == 0).mean())
        if exclude_zero:
            df = df[df[self.total_col] > 0]
        t = target_from_finals(df[self.comp_cols].to_numpy(float), f"{self.year_label} (microdados INEP)",
                               Provenance.OBSERVADO, n_1000=n_1000, p_zero=p_zero)
        t.extra = {"n_valid_status_including_zero": n_all, "exclude_zero": exclude_zero}
        return t
