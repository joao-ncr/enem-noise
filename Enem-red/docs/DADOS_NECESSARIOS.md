# Dados necessários e como obtê-los (o que eu não consegui fazer sozinho)

O ambiente em que o projeto foi construído **não tinha acesso ao site do INEP** (domínio bloqueado), então nenhum dado
real foi baixado. Tudo o que o programa produz hoje é **SIMULADO** com parâmetros **HIPOTÉTICOS**. Para passar a
**ESTIMADO/OBSERVADO**, faça o seguinte (≈10 minutos):

## 1. Microdados do ENEM 2025 (público)
1. Baixe "Microdados do ENEM 2025" no portal de dados abertos do INEP
   (https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem — confirme a URL atual).
2. Extraia o CSV (ex.: `DADOS/MICRODADOS_ENEM_2025.csv`) para `data/raw/`.
3. Rode:
   ```bash
   python -m enemnoise real-target --microdata data/raw/MICRODADOS_ENEM_2025.csv --year ENEM-2025
   python -m enemnoise exp003 --microdata data/raw/MICRODADOS_ENEM_2025.csv --year ENEM-2025
   ```
   Colunas usadas: `NU_NOTA_COMP1..5`, `NU_NOTA_REDACAO`, `TP_STATUS_REDACAO` (1 = sem problemas). Se os nomes mudarem,
   ajuste `RealDataProvider(comp_cols=..., total_col=..., status_col=...)`. Separador `;`, encoding `latin-1` (padrão INEP).
4. O alvo calculado é **[OBSERVADO]** (marginais da nota FINAL). Confira também o nº de notas 1000 (a imprensa reportou 10
   para o ENEM 2025 — verificar no seu arquivo; a coluna de total pode ter valores 1000 exatos).

## 2. O que os microdados NÃO trazem (e por que importa)
Não há nota **por avaliador**. Sem ela, sigma (ruído de avaliação) só pode ser **filtrado**, não estimado, e o filtro é
sensível à especificação do modelo (ver `results/exp003/report.md`, seção 2b).
Dados que **fecham** essa lacuna, em ordem de valor:

| Dado | Para quê | Como tentar |
|---|---|---|
| Notas por competência de cada avaliador (1º, 2º, 3º) por redação anonimizada | ICC real, sigma, vieses, taxa real de discrepância | Pedido de acesso à informação ao INEP (Lei 12.527/2011, plataforma Fala.BR) |
| Taxa real de acionamento do 3º corretor e da banca | Calibrar sigma pelo p_terceiro simulado | Mesmo pedido; ou relatórios/estudos do INEP |
| Regra oficial de consolidação (Cartilha da Redação 2025) | Confirmar `inep_2025` | Cartilha oficial (PDF) |
| Espelhos de redação de candidatos voluntários | Checagem de ordem de grandeza (amostra **enviesada**) | Coleta voluntária, anonimizada (LGPD) |

### Modelo de pedido (LAI)
> Solicito, em formato aberto e anonimizado, para o ENEM 2025: (a) a nota atribuída a cada uma das cinco competências por
> cada avaliador (1º, 2º e, quando houver, 3º e banca) para cada redação, sem identificação do candidato nem do
> avaliador; (b) o número de redações com terceira correção e com correção por banca; (c) a regra vigente de
> consolidação da nota final. Finalidade: pesquisa sobre confiabilidade da avaliação.

## 3. Quando houver notas por avaliador
Implemente `RealDataProvider.rater_scores()` (formato `(N,2,5)`), estime ICC com `analysis/reliability.py` e substitua os
`NoiseParams` hipotéticos por estimados (`Provenance.ESTIMADO`). Os relatórios passam a rotular o resultado como
"SIMULADO (parâmetros ESTIMADOS de dados reais)".
