from __future__ import annotations

from fastapi import FastAPI

from .. import __version__
from .routes.endpoints import router

app = FastAPI(
    title="enemnoise API",
    version=__version__,
    description=("Simulação Monte Carlo da variabilidade de notas da redação do ENEM. "
                 "TODOS os resultados são SIMULADOS; parâmetros padrão são HIPOTÉTICOS."),
)
app.include_router(router)


@app.get("/", tags=["meta"])
def root():
    return {"name": "enemnoise", "version": __version__, "docs": "/docs",
            "aviso": "Resultados simulados não são evidência empírica sobre o ENEM real."}
