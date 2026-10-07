# Pré-registro — Experimento 002 (ranking latente × observado)

População **HIPOTÉTICA** (mu=[3,2;3,2;3,0;3,0;3,0], tau=0,9, rho=0,7), tamanhos 10/100/1000, 50 replicações,
sigma ∈ {0,2; 0,35; 0,6}, sigma_u=0,15, modelo M1, painel neutro, regra inep_2025.

Medidas (todas definidas antes da execução): Spearman e Kendall (latente × observado), deslocamento médio de posição,
P(inversão) entre pares com latente distinto, P(empate), P(inversão) atribuível **só à discretização** (avaliador
perfeito, sem ruído — linha de base), fração do grupo "top 20%" substituída.
Sem hipótese direcional pré-fixada além de: a P(inversão) deve crescer com sigma e decrescer com a diferença latente
(verificação de sanidade do simulador, coberta por testes). Resultado condicional às premissas.
