# enemnoise — variabilidade de nota na redação do ENEM (simulação Monte Carlo)

Ferramenta de **investigação científica computacional**: testa (não assume) se diferentes avaliações plausíveis de uma
mesma redação podem produzir notas distintas o bastante para afetar ranking e classificação.

> **Leia isto primeiro.** Nenhum dado real foi usado. Todo resultado é **SIMULADO** e depende de parâmetros
> **HIPOTÉTICOS** (principalmente o ruído de avaliação σ, que é desconhecido). Os resultados são **mapas condicionais**
> ("se σ for X, então Y"), **não** evidência sobre o ENEM real. Para estimar σ são necessários dados que não são públicos:
> veja [`docs/DADOS_NECESSARIOS.md`](docs/DADOS_NECESSARIOS.md).

Rótulos obrigatórios em tudo (API, figuras, relatórios): **OBSERVADO · ESTIMADO · SIMULADO · HIPOTÉTICO**
(`enemnoise/models/provenance.py`; um resultado herda o "pior" rótulo de suas entradas).

## Instalação e uso rápido
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt            # ou: pip install -e ".[dev]"
python -m pytest -q                        # 43 testes (unitários, propriedades, estatísticos, API)
python -m enemnoise all --quick            # experimentos em versão rápida  -> results/*/report.md
python -m enemnoise all                    # versão completa (~1 min)
python -m enemnoise serve                  # API em http://127.0.0.1:8000/docs
```
Experimentos individuais: `python experiments/exp001_single_essay/run.py [--quick]` (idem exp002, exp003).

## Dados reais (única etapa manual)
Baixe os microdados do ENEM 2025 no INEP e rode `python -m enemnoise real-target --microdata data/raw/<arquivo>.csv` e
`python -m enemnoise exp003 --microdata data/raw/<arquivo>.csv`. Detalhes, limites e modelo de pedido LAI para notas
por avaliador em `docs/DADOS_NECESSARIOS.md`.

## O que está implementado
| Módulo | Conteúdo |
|---|---|
| `models/` | Essay (θ por competência), Competency/NoiseParams, EvaluatorProfile/Panel, Provenance, GradeBatch |
| `simulation/` | `SimulationEngine`; modelos de erro **M0** (normal truncada), **M1** (ordinal, 6 níveis), **M1H** (ordinal heterocedástico) com ModelCards; regra de nota **inep_2025** (+ variante inclusiva, + média simples); Monte Carlo reprodutível por blocos |
| `analysis/` | confiabilidade (ICC(1,1)/(1,k), SEM, Bland–Altman, kappa), comparação (P(A>B), empate, inversão, sobreposição), ranking (Spearman/Kendall, inversões por diferença latente, deslocamento, troca no topo), sensibilidade (latente e observada, números aleatórios comuns), **ParadoxDetector** (6 paradoxos, limiares fixados a priori, testado contra falso positivo), divergência entre modelos |
| `providers/` | `DataProvider` → `SimulatedDataProvider`, `RealDataProvider` (microdados INEP), `ExternalAPIDataProvider` (stub) |
| `calibration.py` | filtro de consistência modelo × alvos observáveis (não é estimador; inclui teste de má especificação) |
| `api/` | `POST /simulate /compare /sensitivity /scenario`, `GET /scenario /meta /runs`, `GET /runs/{id}`, `POST /runs/{id}/replay` |
| `visualization/` | distribuição, boxplot, sobreposição, heatmap competência×σ, latente×observada, ranking×ranking, inversão×gap, fronteira, sensibilidade (todas com selo de proveniência) |
| `experiments/` | exp001 (uma redação, pré-registrado), exp002 (ranking 10/100/1000), exp003 (confiabilidade + calibração) |

## Exemplo de API
```bash
curl -X POST localhost:8000/simulate -H 'content-type: application/json' -d '{
  "essay_profile": {"points": [160,160,160,160,160]},
  "evaluator_profile": {"preset": "misto"},
  "model": "M1", "scoring_rule": "inep_2025",
  "parameters": {"sigma": 0.35, "sigma_u": 0.15, "sigma_beta": 0.1},
  "iterations": 100000, "seed": 42, "cutoffs": [700, 800]}'
```
A resposta traz `distribution`, `statistics`, `classification_impact`, `paradoxes` e `run_manifest` (seed, versões,
timestamp, hash). `POST /runs/{run_id}/replay` re-executa e confirma `reproduced: true`.

## Resultados incluídos (SIMULADOS, HIPOTÉTICOS — ver `results/`)
Gerados com os pré-registros de `experiments/*/prereg.md`. Leitura cuidadosa:

- **exp001:** com os critérios pré-fixados, H1 (variabilidade relevante) vale em 104 de 120 células; H0 vale em 16, todas
  nos menores σ. A conclusão é um **mapa em função de σ**: abaixo de certo σ a variabilidade é irrelevante pelo critério;
  acima, não. O σ real é desconhecido.
- **Duas redações a 40 pts de distância** (um nível em uma competência): P(inversão) de ≈2% (σ=0,1) a ≈30% (σ=0,75) em M1.
- **exp002:** mesmo com Spearman ≥ 0,90, há inversões locais; P(inversão) decresce com a diferença latente. **Parte das
  inversões (≈2–3%) ocorre sem nenhum ruído**, só pela escala de 6 níveis (efeito da escala, não do avaliador).
- **exp003:** o filtro por marginais recupera σ quando o modelo está certo e **erra ~2×** quando o modelo está errado
  (σ escolhido 0,75 vs verdadeiro 0,35). Moral: sem notas por avaliador, σ não é determinável com confiança.
- Evidência contrária à hipótese de "discrepância grande" está listada em cada relatório (seção 5 do exp001).

## Reprodutibilidade
Seed + parâmetros + versões + timestamp + hash da configuração e do resultado em cada execução (`data/simulated/<run_id>/`
e `results/*/manifest.json`). Blocos de 100.000 linhas com `SeedSequence(seed, spawn_key=(i,))`.

## Estrutura
```
enem-noise/
├── enemnoise/ (api · simulation · models · analysis · visualization · providers · experiments · calibration.py · registry.py · cli.py)
├── experiments/exp00X_*/ (config.yaml · prereg.md · run.py)
├── data/{raw,processed,simulated}/   results/   docs/   scripts/   tests/{unit,property,statistical,api}/
└── README.md · pyproject.toml · requirements.txt · Makefile
```
O pacote Python fica sob `enemnoise/` (em vez de pastas soltas na raiz) para permitir `pip install -e .`.

## Limitações e premissas
`docs/assumptions.md` e `docs/limitations.md`. Em especial: a regra de consolidação foi extraída de fontes secundárias
(confirmar na Cartilha oficial); fadiga/efeito de ordem não estão modelados; "verdade" (T*) é definição do modelo.
