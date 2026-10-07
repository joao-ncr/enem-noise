# Premissas (todas HIPOTÉTICAS salvo indicação)

1. **Escala latente:** 1 unidade = 1 nível (40 pts); limiares em k±0,5. Sigma em níveis.
2. **Ruído gaussiano** na escala latente, com componentes: viés do avaliador (β_j), efeito avaliador×redação (u_ij, "halo")
   e ruído residual por competência (ε_ijc).
3. **Avaliadores independentes**, sorteados de um painel a cada correção (nenhum "avaliador fixo" por candidato).
4. **Desempenho latente θ por competência é fixo e conhecido** em cada experimento (limitação: o "verdadeiro" é do modelo).
5. **T\* (nota latente)** = 40·Σ clip(θ,0,5), contínua. (No documento de design inicial, T* era a nota esperada de um
   avaliador de referência; optou-se pela versão contínua para evitar empates artificiais — a diferença é a "inversão por
   discretização", reportada como linha de base no exp002.)
6. **Regra 2025** (fontes secundárias; confirmar na Cartilha): ver `simulation/scoring.py`. **Banca** modelada como mediana
   por competência de três novas avaliações (HIPÓTESE). Zeros por anulação não são modelados.
7. **População de redações** (exp002/003): θ ~ N(mu, tau) com fator geral (rho), refletida em [0,5].
8. **Parâmetros de perfis de avaliador** (rigoroso/permissivo etc.) são exemplos; **não** descrevem avaliadores reais.
9. **Hipóteses do deck** (C3/C4 mais ruidosas; ruído maior no topo; "efeito de fadiga/ordem") são tratadas como hipóteses a
   testar: M1H e `NoiseParams.deck_heterogeneous`. Fadiga/efeito de ordem **não** estão modelados (exigiria dados de
   sequência de correção).
