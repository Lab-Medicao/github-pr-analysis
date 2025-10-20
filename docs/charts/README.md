# 📊 Gráficos da Análise Estatística

Esta pasta contém todas as visualizações geradas a partir da análise de **947.735 Pull Requests** de repositórios populares do GitHub.

## 📁 Arquivos Disponíveis

### 1. `correlation_heatmap.png`

**Heatmap de Correlações de Spearman**

Visualização matricial mostrando todas as correlações entre:

- Variáveis independentes (Tamanho, Tempo, Descrição, Interações)
- Variáveis dependentes (Status do PR, Número de Revisões)

**Como interpretar:**

- Cores vermelhas: correlações negativas
- Cores azuis: correlações positivas
- Intensidade da cor: magnitude da correlação

---

### 2. `correlation_bars.png`

**Gráficos de Barras de Correlações**

Dois painéis comparando correlações:

- **Esquerda:** RQ01-04 (Fatores → Status do PR)
- **Direita:** RQ05-08 (Fatores → Número de Revisões)

**Destaques:**

- Barras verdes: correlações positivas
- Barras vermelhas: correlações negativas
- Comprimento: magnitude da correlação

---

### 3. `descriptive_comparison.png`

**Comparação de Medianas: Merged vs Não Merged**

Cinco painéis comparando medianas entre PRs aceitos e rejeitados:

1. Tamanho do PR (linhas)
2. Tempo de Análise (horas)
3. Tamanho da Descrição (caracteres)
4. Interações (comentários)
5. Número de Revisões

**Principais achados:**

- PRs não merged levam **4.4x mais tempo** (147h vs 33h)
- PRs não merged têm **67% mais interações** (5 vs 3)
- Tamanho do PR é praticamente igual (38 vs 36 linhas)

---

### 4. `distributions.png`

**Distribuições das Variáveis Principais**

Violin plots mostrando a distribuição completa das variáveis:

- Tamanho do PR
- Tempo de Análise
- Interações
- Número de Revisões

**Como interpretar:**

- Verde: PRs merged
- Vermelho: PRs não merged
- Largura: densidade da distribuição
- Linha preta central: mediana
- Linha pontilhada: média

---

### 5. `scatter_correlations.png`

**Scatter Plots das Principais Correlações**

Quatro painéis mostrando relações entre variáveis:

1. **Interações vs Revisões** (ρ = 0.58) - correlação mais forte
2. **Tempo vs Revisões** (ρ = 0.35)
3. **Tamanho vs Revisões** (ρ = 0.34)
4. **Tempo vs Status** (histograma comparativo)

**Insights visuais:**

- Relação clara entre interações e revisões
- PRs não merged têm tempos mais longos e dispersos
- Tamanho tem relação moderada com revisões

---

### 6. `summary_dashboard.png`

**Dashboard Completo - Visão Geral**

Dashboard integrado com todas as principais descobertas:

- Top 3 correlações positivas
- Top 3 correlações negativas
- Maiores diferenças percentuais nas medianas
- Comparação visual de todas as métricas
- Estatísticas gerais do estudo
- Interpretação completa das correlações
