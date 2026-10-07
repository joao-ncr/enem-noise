# Arquitetura

```
API (FastAPI) ──▶ controllers (funções puras) ──▶ RunRegistry (seed, versões, hashes)
                          │
        DataProvider ─────┤  Simulated | Real (microdados INEP) | External (stub)
                          ▼
              SimulationEngine  =  ErrorModel (M0/M1/M1H) + RaterSampler + ScoringRule (inep_2025…)
                          │ GradeBatch (s1, s2, final_comp, flags 3º corretor/banca)
                          ▼
   analysis: reliability · compare · ranking · sensitivity · paradox · model_check · calibration
                          ▼
         visualization + reporting (rótulos OBSERVADO/ESTIMADO/SIMULADO/HIPOTÉTICO obrigatórios)
```

## Entidades
Essay(θ por competência) — Competency(σ_c) — EvaluatorProfile/Panel(β, κ, shrink) — Evaluation (s_ijc) —
ConsolidatedResult (final, 3º corretor, banca) — Decision (faixa, corte) — ExperimentConfig/Run.

## Modelo (M1, núcleo)
```
y*_ijc = (1-s_j)·θ_ic + s_j·2,5 + β_j + u_ij + ε_ijc
β_j ~ perfil + N(0,σ_β²) ; u_ij ~ N(0,σ_u²) ; ε_ijc ~ N(0,(σ_c κ_j)²)
nota_ijc = 40 · clip(floor(y* + 0,5), 0, 5)
```
## Reprodutibilidade
Blocos de 100.000 linhas com `SeedSequence(seed, spawn_key=(i,))`; manifesto com seed, iterações, parâmetros, versões,
timestamp, hash da configuração e hash do resultado; `POST /runs/{id}/replay` re-executa e compara hashes.

## Mapa de pastas
`enemnoise/api` (routes, schemas, controllers) · `simulation` · `models` · `analysis` · `visualization` · `providers` ·
`experiments` (lógica) · `experiments/` na raiz (config.yaml, prereg.md, run.py) · `data/{raw,processed,simulated}` ·
`results/` · `docs/` · `tests/{unit,statistical,property,api}`.
