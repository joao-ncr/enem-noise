# Pré-registro — Experimento 003 (confiabilidade e consistência com alvos)

1. ICC(1,1), ICC(1,2), SEM e kappa quadrático por sigma sobre população HIPOTÉTICA (50.000 redações).
2. Filtro de consistência: para cada sigma, ajustar (tau, rho, mu) e medir a distância entre a marginal simulada e a
   marginal-alvo (Wasserstein por competência + diferença de DP do total). "Consistente" = distância ≤ 1,25 × mínimo.
3. Alvo: sintético (sigma verdadeiro = 0,35) por padrão; **real** (microdados) quando `--microdata` é informado.
4. Teste de má especificação: alvo gerado por M1H + painel misto, ajustado por M1 + neutro. Reportar a diferença
   entre sigma verdadeiro e escolhido, sem ajustar o procedimento depois.
Interpretação: o filtro NÃO é um estimador; só estreita a faixa plausível sob o modelo.
