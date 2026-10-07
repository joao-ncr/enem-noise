# Pré-registro — Experimento 001 (uma redação, muitas avaliações)

Escrito **antes** da execução completa. Limiares são **HIPOTÉTICOS** e não podem ser ajustados após ver resultados;
qualquer critério adicional entra como análise exploratória, marcada como tal.

## Pergunta
Para uma mesma redação, quão dispersa é a nota final sob avaliação por pares sorteados, e com que frequência essa
dispersão é grande o bastante para cruzar um corte situado a 40 pontos da média?

## Hipóteses
- **H0 (variabilidade irrelevante):** DP(nota final) < 40 pts **e** P(|nota − E[nota]| ≥ 40 pts) < 5%.
- **H1 (variabilidade relevante):** caso contrário.
- O desvio é medido em torno da **média simulada** (ruído puro), separando viés de variância. O desvio em relação ao
  latente T* é reportado como secundário (`p_err40_vs_latente`, `vies`).

## Desfechos
- Primário: DP e quantis 2,5%/97,5% da nota final; P(nota ≥ corte) para cortes 600/700/800.
- Secundários: taxa de terceiro corretor e de banca; gap médio entre os dois primeiros avaliadores;
  A=[4,4,4,4,4] × B=[4,4,3,4,4] (P(A>B), P(empate), P(inversão), sobreposição); P(nota=1000 | θ).

## Desenho
Grade: modelos {M0, M1} × painéis {neutro, misto, alta_variabilidade} × sigma {0,1; 0,2; 0,35; 0,5; 0,75} ×
sigma_u {0; 0,15} × redações {nível 3 (T*=600), nível 4 (T*=800)}; 100.000 iterações por célula; seed 20261007.
Resultado reportado como **mapa em função de sigma** e **sigma crítico** (menor sigma da grade com H1).

## O que este experimento NÃO pode concluir
Qual é o sigma real do ENEM. Para isso é preciso calibrar (exp003 + docs/DADOS_NECESSARIOS.md).

## Registro de alterações antes da execução completa
- A grade de sigma ganhou o valor 0,1 (para que a região de H0 apareça) após um teste rápido de fumaça com 10.000
  iterações; nenhum critério (H0/H1, limiares) foi alterado.
