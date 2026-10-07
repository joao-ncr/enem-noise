# A nota da redação do ENEM é tão exata quanto parece?

Um projeto aberto que usa o computador para fazer uma pergunta simples:

> **Se a mesma redação fosse corrigida por outras pessoas, a nota seria a mesma? E, se não fosse, isso poderia mudar quem passa e quem não passa?**

Aqui você encontra um simulador, os resultados que ele gerou e, principalmente, uma explicação honesta do que esses resultados **dizem** e do que **não dizem**.

---

## Leia isto antes de tudo

- **Este projeto não acusa ninguém.** Não afirma que o ENEM é injusto nem que é perfeito.
- **Tudo o que está nos resultados abaixo é simulação.** É um experimento de computador, não uma medição do ENEM real.
- **Ainda não sabemos o quanto os corretores realmente divergem.** Essa informação não é pública. Por isso os resultados são do tipo *"se os corretores divergirem tanto, então acontece isto"*.
- O objetivo não é provar que existe problema. Se a simulação mostrasse que a variação é pequena e não importa, isso também seria um resultado válido.

---

## A ideia em poucas palavras

Pense em duas pessoas medindo o mesmo móvel com uma régua. Se a régua for boa, as duas chegam quase no mesmo número. Se a régua for mais "elástica", os números podem diferir um pouco, e essa diferença pode ser decisiva se o móvel precisar caber num vão exato.

Corrigir redação é mais difícil do que medir um móvel, porque envolve julgamento. Duas pessoas competentes podem dar notas ligeiramente diferentes, sem que nenhuma esteja "errada". A pergunta é: **quão diferentes, com que frequência, e isso importa para a classificação?**

### Como o ENEM corrige (regras públicas)

- Cada redação é lida por **dois corretores**, de forma independente.
- Cada um dá nota de 0 a 200 para cada uma das **5 competências**, sempre em "degraus" de 40 pontos (0, 40, 80, 120, 160, 200).
- Se os dois forem parecidos, a nota final é a média.
- Se **discordarem muito** (mais de 100 pontos no total, ou mais de 80 em uma competência), entra um **terceiro corretor**. Se ele concordar com um dos dois, vale a média dos dois mais próximos. Se não concordar com nenhum, uma banca decide.

(Conferimos essas regras em reportagens sobre a Cartilha de 2025. Vale confirmar no documento oficial.)

### O que o simulador faz

1. Criamos uma redação com uma "qualidade verdadeira" definida por nós (por exemplo, nível 160 em todas as competências).
2. Sorteamos dois corretores. Cada um "enxerga" essa qualidade com um pouco de imprecisão: um pode ser mais rigoroso, outro mais generoso, e todos oscilam um pouco de critério para critério.
3. Aplicamos a regra do ENEM, com terceiro corretor e banca quando for o caso.
4. **Repetimos isso 100 mil vezes** com a mesma redação e olhamos todas as notas que saíram.

É como jogar um dado muitas vezes para descobrir quanto ele "pende". A técnica se chama Monte Carlo, mas a ideia é só essa: repetir muito para ver o padrão.

### O botão que não conhecemos

O simulador tem um "botão" que controla **o quanto os corretores divergem entre si**. Chamamos de σ (a letra grega sigma). Não sabemos qual é o valor real, então testamos vários:

| Cenário | Como imaginar |
|---|---|
| σ = 0,10 | Corretores quase sempre concordam |
| σ = 0,35 | Divergência moderada: cada corretor "sente" o texto com imprecisão de cerca de um terço de degrau |
| σ = 0,75 | Divergência grande |

---

## O que as simulações mostraram

Todos os exemplos abaixo são de uma redação cuja qualidade verdadeira corresponde a **800 pontos** (nível 160 em todas as competências).

### 1. Quanto uma mesma redação pode variar

| Corretores divergem... | 95% das notas ficaram entre | Precisou de terceiro corretor |
|---|---|---|
| quase nada (σ = 0,10) | 780 e 820 | 2% das vezes |
| pouco (σ = 0,20) | 760 e 840 | 4% das vezes |
| moderado (σ = 0,35) | 720 e 880 | 15% das vezes |
| bastante (σ = 0,50) | 700 e 900 | 25% das vezes |
| muito (σ = 0,75) | 680 e 900 | 37% das vezes |

**Em português simples:** se os corretores divergirem pouco, a nota é muito estável. Se divergirem de forma moderada, a mesma redação pode ter notas espalhadas por uns 160 pontos. A diferença entre "estável" e "instável" depende inteiramente de um número que ainda não conhecemos.

### 2. Duas redações quase iguais: quem fica na frente?

Imagine a redação A e a redação B. A é **um degrau melhor em uma única competência** (40 pontos de diferença verdadeira). Qual tira nota maior?

| Corretores divergem... | A tira mais que B | B tira mais que A (inversão) | Empate |
|---|---|---|---|
| quase nada | 98% | 0,1% | 2% |
| moderado | 74% | 15% | 11% |
| muito | 64% | 28% | 9% |

**Em português simples:** com divergência moderada, a redação que era melhor perde para a pior em cerca de 1 vez em cada 7 sorteios de corretores. Isso é "sorte do sorteio", não mérito.

### 3. A própria escala tem um efeito

Como as notas só vêm em degraus de 40, duas redações com qualidade bem próxima podem cair no mesmo degrau ou em degraus diferentes por uma diferença minúscula. Na simulação, **mesmo com corretores perfeitos e sem nenhum erro**, cerca de **2 em cada 100** pares de redações aparecem em ordem trocada. Isso vem só do formato da escala, não de erro humano.

### 4. E a nota 1000?

Pegamos um texto "perfeito" (nível máximo nas 5 competências) e perguntamos: quantas vezes ele tira 1000?

| Corretores divergem... | Chance de tirar 1000 |
|---|---|
| quase nada | 96% |
| pouco | 79% |
| moderado | 42% |
| bastante | 20% |
| muito | 8% |

**Em português simples:** para tirar 1000, os dois corretores precisam dar 200 nas cinco competências. Quanto mais eles divergem, mais difícil isso fica, mesmo para um texto sem defeito no modelo. Atenção: isso fala da *chance de um texto no teto*, e não de quantos textos assim existem de fato.

### 5. Efeito em uma classificação

Simulamos 1.000 redações e imaginamos que só o **grupo dos 20% melhores** passa. Quantas vagas seriam ocupadas por candidatos que, na "qualidade verdadeira", não estavam nesse grupo?

| Corretores divergem... | Vagas do grupo ocupadas por outros candidatos |
|---|---|
| pouco (σ = 0,20) | 12% |
| moderado (σ = 0,35) | 14% |
| bastante (σ = 0,60) | 18% |

O ranking geral continua muito parecido com o verdadeiro (correlação acima de 0,94), mas **os candidatos perto da linha de corte são os que mais sofrem**. Quem está longe da linha quase não é afetado.

---

## Resumo: o que dá e o que não dá para concluir

| Dá para dizer | **Não** dá para dizer |
|---|---|
| Com o modelo usado, a regra do ENEM tolera uma divergência pequena sem alterar muito as notas. | Que a divergência real dos corretores do ENEM é pequena ou grande. Esse número é desconhecido. |
| Quando a divergência é moderada ou grande, candidatos próximos da linha de corte podem trocar de posição por sorte. | Que isso acontece de fato no ENEM, nessa proporção. |
| A escala em degraus de 40 já cria algumas trocas de ordem sozinha. | Que alguma correção específica foi injusta ou errada. |
| Tudo depende de um número que só dados reais de correção podem informar. | Que a simulação "prova" qualquer coisa sobre o exame real. |

---

## E agora: dados reais

O ENEM publica os **microdados**: as notas finais de cada candidato por competência. Eles mostram **como as notas se distribuem**, mas **não mostram a nota de cada corretor separadamente**. Por isso eles ajudam a checar se o simulador se parece com a realidade, mas não resolvem sozinhos a pergunta sobre a divergência.

Para descobrir de fato o quanto os corretores divergem, seria preciso acesso a dados de correção por avaliador (anonimizados). Em `docs/DADOS_NECESSARIOS.md` há um passo a passo para usar os microdados do INEP e um modelo de pedido de acesso à informação.

Quando as análises com dados reais forem feitas, os resultados entrarão na pasta `results/` e serão **claramente separados** das simulações.

---

## Como a gente separa simulação de realidade

Tudo no projeto carrega uma etiqueta:

| Etiqueta | Significa |
|---|---|
| **OBSERVADO** | dado real, medido |
| **ESTIMADO** | número calculado a partir de dado real |
| **SIMULADO** | resultado de uma simulação |
| **HIPOTÉTICO** | valor escolhido por nós só para experimentar |

Os gráficos e relatórios exibem essas etiquetas. Uma simulação nunca é apresentada como se fosse evidência.

---

## Como rodar no seu computador

Você precisa de Python 3.10 ou mais novo.

```bash
git clone <endereço-do-repositório>
cd enem-noise
pip install -r requirements.txt

python -m pytest -q              # confere se tudo funciona
python -m enemnoise all          # roda os experimentos (cerca de 1 minuto)
```

Os relatórios aparecem em `results/exp001/report.md`, `results/exp002/report.md` e `results/exp003/report.md`, com gráficos.

Quer testar sua própria redação? Suba a API e abra `http://127.0.0.1:8000/docs`:

```bash
python -m enemnoise serve
```

---

## Glossário rápido

- **Competência**: cada um dos 5 critérios de avaliação da redação.
- **Qualidade verdadeira**: nota "ideal" que definimos no computador para a redação; no mundo real ela não existe como número exato.
- **σ (sigma)**: o quanto os corretores divergem entre si. Quanto maior, mais a nota varia.
- **Inversão**: quando uma redação melhor tira nota menor que uma pior.
- **Terceiro corretor**: avaliador extra acionado quando os dois primeiros discordam muito.
- **Monte Carlo**: repetir uma simulação milhares de vezes para enxergar o padrão.
- **Linha de corte**: nota mínima para passar ou entrar num grupo.

---

## Para quem quer ir mais fundo

A explicação técnica completa (modelos estatísticos, estrutura do código, testes, API) está em [`docs/README_TECNICO.md`](docs/README_TECNICO.md). As premissas e limitações estão em `docs/assumptions.md` e `docs/limitations.md`. Cada experimento tem um **pré-registro** em `experiments/`, escrito antes de rodar, para que os critérios não sejam ajustados depois de ver os resultados.

Contribuições são bem-vindas, especialmente: revisão das regras de correção, dados anonimizados e ideias de como testar melhor.
