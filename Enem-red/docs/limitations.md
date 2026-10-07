# Limitações

- Nenhum dado real foi usado: todos os resultados são condicionais a parâmetros hipotéticos (ver DADOS_NECESSARIOS.md).
- O sigma real do ENEM é desconhecido; a calibração por marginais é um **filtro** sensível à especificação
  (exp003, seção 2b: com modelo errado, o sigma escolhido ficou 2× o verdadeiro).
- "Inversão de ranking" é relativa à definição de T* **do modelo**; não existe "verdade" observável da qualidade textual.
- Efeitos não modelados: fadiga/ordem de leitura, calibração entre avaliadores ao longo do tempo, treinamento, zeros por
  anulação, dependência entre 1º e 2º avaliador, diferenças entre lotes de correção.
- P(nota = 1000) real (~10 em milhões de redações) é um evento de cauda extrema; o simulador só estima P(1000 | θ). Combinar com
  uma distribuição realista de θ no topo exige dados reais.
- Com N grande, qualquer diferença é "estatisticamente significativa": usar tamanhos de efeito e critérios práticos
  pré-fixados (feito nos pré-registros).
- A regra de consolidação foi extraída de fontes secundárias; uma divergência entre fontes ("superior a 100" × "100 ou
  mais") é testada como variante (`inep_2025_inclusive`).
