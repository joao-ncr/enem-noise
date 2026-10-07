> **Atenção:** todos os números abaixo são **SIMULADOS** e dependem de parâmetros **HIPOTÉTICOS**. Não constituem evidência empírica sobre o ENEM real. Valem como mapa condicional às premissas listadas.

## 1. Confiabilidade por sigma (população HIPOTÉTICA)

| sigma | ICC(1,1)_total | ICC(1,2)_total | SEM_total_pts | DP_obs_total | p_terceiro | kappa_C3 | ICC_C1 | ICC_C3 | ICC_C5 |
|---|---|---|---|---|---|---|---|---|---|
| 0.1500 | 0.9174 | 0.9569 | 45.7641 | 159.2587 | 0.1243 | 0.8560 | 0.8540 | 0.8560 | 0.8541 |
| 0.2500 | 0.9042 | 0.9497 | 49.4763 | 159.8690 | 0.1490 | 0.8156 | 0.8115 | 0.8156 | 0.8126 |
| 0.3500 | 0.8875 | 0.9404 | 53.9545 | 160.8334 | 0.1835 | 0.7649 | 0.7622 | 0.7649 | 0.7629 |
| 0.5000 | 0.8537 | 0.9211 | 62.1830 | 162.5695 | 0.2513 | 0.6791 | 0.6746 | 0.6791 | 0.6759 |
| 0.7500 | 0.7792 | 0.8759 | 78.0234 | 166.0565 | 0.3919 | 0.5318 | 0.5258 | 0.5318 | 0.5274 |
| 1.0000 | 0.6933 | 0.8189 | 94.1387 | 169.9977 | 0.5535 | 0.4068 | 0.3980 | 0.4068 | 0.4005 |

ICC(1,1): fração da variância observada (por avaliador) que é variância real entre redações. SEM = erro padrão de medida de UM avaliador.

## 2. Filtro de consistência com alvo observável

Alvo: **SIMULADO (alvo SINTÉTICO — apenas demonstração do método)** — SINTÉTICO (sigma verdadeiro=0.35, gerador=M1/neutro). Distância: média das distâncias de Wasserstein por competência + diferença de DP do total.

| sigma | distance | tau | rho | p_third | p_banca | consistent |
|---|---|---|---|---|---|---|
| 0.1500 | 3.3444 | 0.9000 | 0.7000 | 0.1216 | 0.0004 | False |
| 0.2500 | 1.7502 | 0.9000 | 0.7000 | 0.1460 | 0.0010 | False |
| 0.3500 | 0.4735 | 0.9000 | 0.7000 | 0.1804 | 0.0029 | True |
| 0.5000 | 2.0932 | 0.9000 | 0.7000 | 0.2450 | 0.0086 | False |
| 0.7500 | 4.4987 | 0.9000 | 0.7000 | 0.3896 | 0.0549 | False |

Sigmas consistentes (tolerância 25%): [0.35].  
**Conjunto estreito?** True.  
Faixa estreita de sigma consistente SOB ESTE MODELO (vale só se a especificação estiver correta; confira com a taxa real de terceiro corretor e com o teste de má especificação).

## 2b. Teste de má especificação (alvo sintético gerado por M1H + painel misto; ajustado com M1 + painel neutro)

Sigma verdadeiro do gerador = 0.35. Sigma escolhido pelo ajuste = 0.75; consistentes: [0.5, 0.75].

| sigma | distance | tau | rho | p_third | consistent |
|---|---|---|---|---|---|
| 0.1500 | 5.2393 | 1.1000 | 0.5000 | 0.1213 | False |
| 0.2500 | 4.1600 | 1.1000 | 0.5000 | 0.1442 | False |
| 0.3500 | 3.6450 | 1.1000 | 0.5000 | 0.1785 | False |
| 0.5000 | 2.4220 | 0.9000 | 0.7000 | 0.2462 | True |
| 0.7500 | 2.3404 | 0.9000 | 0.7000 | 0.3846 | True |

Se o sigma escolhido difere do verdadeiro, a calibração por marginal é **sensível à especificação** — com dados reais, trate o resultado como faixa, não como valor.

## 3. Como tornar isto uma estimativa

Ver `docs/DADOS_NECESSARIOS.md`: notas por avaliador, taxa real de terceiro corretor e distribuição real por competência permitem fixar sigma e migrar de HIPOTÉTICO para ESTIMADO.

## Manifesto

```
experiment: exp003_reliability_calibration
seed: 20261009
iterations: 50000
model_version: enemnoise-model-0.1.0
data_version: simulated-v0
timestamp_utc: 2026-10-07T19:18:25.546941+00:00
config_hash: 68f257cdf22638b333dab4e9e9653e96834199351fd9971a115976ce635c0fef
numpy: 2.4.4
python: 3.12.3
```
