# 📊 Análise Estatística: Caracterizando a Atividade de Code Review no GitHub

**Autores:** Ana Luiza Machado Alves, Lucas Henrique Chaves de Barros, Raquel Inez de Almeida Calazans  
**Disciplina:** Laboratório de Experimentação de Software  
**Data:** Outubro de 2025

---

## 1. Introdução

Este documento apresenta uma análise estatística abrangente da atividade de code review em repositórios populares do GitHub. O objetivo é identificar quais fatores influenciam (i) o **feedback final das revisões** (se um PR é aceito/merged ou não) e (ii) o **número de revisões** realizadas em um PR.

Analisamos um total de **947.735 Pull Requests** coletados de repositórios diversos, abrangendo diferentes linguagens de programação, domínios de aplicação e tamanhos de projetos.

### 1.1. Hipóteses Informais

Antes de realizar as análises, elaboramos hipóteses informais sobre os resultados esperados:

#### Grupo 1: Feedback Final das Revisões (Status do PR)

**H1.1 - Tamanho do PR:**  
Esperamos que PRs maiores tenham **menor taxa de aprovação**. A justificativa é que PRs maiores aumentam a carga cognitiva dos revisores, dificultam a identificação de bugs e podem indicar mudanças muito abrangentes ou mal estruturadas.

**H1.2 - Tempo de Análise:**  
Esperamos que PRs com **maior tempo de análise** tenham **menor probabilidade de serem merged**. Tempos longos podem indicar problemas de qualidade, falta de consenso, necessidade de múltiplas alterações ou até abandono do PR.

**H1.3 - Descrição do PR:**  
Esperamos que PRs com **descrições mais longas e detalhadas** tenham **maior taxa de aprovação**. Descrições completas facilitam o entendimento do contexto, justificam as mudanças e demonstram profissionalismo.

**H1.4 - Interações:**  
Esperamos uma relação **complexa** com as interações. Por um lado, muitas interações podem indicar problemas que precisam ser resolvidos (correlação negativa). Por outro, podem demonstrar engajamento construtivo. Nossa hipótese inicial é que **mais interações levam a menor taxa de merge**, pois indicam necessidade de múltiplas correções.

#### Grupo 2: Número de Revisões

**H2.1 - Tamanho do PR:**  
Esperamos que PRs maiores recebam **mais revisões**, pois mudanças extensas exigem maior escrutínio e múltiplas rodadas de feedback.

**H2.2 - Tempo de Análise:**  
Esperamos que PRs com **maior tempo de análise** tenham **mais revisões**, refletindo um processo iterativo mais longo de feedback e correções.

**H2.3 - Descrição do PR:**  
Esperamos que descrições mais longas **não tenham forte correlação** com o número de revisões, ou uma correlação positiva fraca, indicando que PRs bem documentados podem facilitar revisões mais focadas.

**H2.4 - Interações:**  
Esperamos uma **forte correlação positiva** entre interações e número de revisões, já que mais discussões naturalmente levam a mais rodadas de revisão.

---

## 2. Metodologia

### 2.1. Coleta de Dados

Os dados foram coletados utilizando a **API GraphQL do GitHub**, conforme descrito no relatório técnico principal. Foram selecionados repositórios populares de diferentes domínios, com limite de até 150 PRs por repositório para garantir representatividade sem viés excessivo de projetos específicos.

### 2.2. Variáveis Analisadas

Para responder às questões de pesquisa, definimos as seguintes variáveis:

**Variáveis Independentes:**

- **Tamanho do PR** (`pr_size`): Soma de linhas adicionadas e removidas (additions + deletions)
- **Tempo de Análise** (`analysis_time_hours`): Tempo em horas entre a criação e o fechamento/merge do PR
- **Tamanho da Descrição** (`description_length`): Número de caracteres no corpo (body) do PR
- **Interações** (`interactions`): Número total de comentários e discussões no PR

**Variáveis Dependentes:**

- **Status do PR** (`is_merged`): Variável binária (1 = merged, 0 = fechado sem merge)
- **Número de Revisões** (`num_reviews`): Contagem de revisões formais realizadas

### 2.3. Método Estatístico

Utilizamos o **Coeficiente de Correlação de Spearman (ρ)** para todas as análises. Esta escolha se justifica por três razões principais:

1. **Não-parametricidade:** Não assume distribuição normal dos dados, adequado para dados de repositórios que tipicamente apresentam distribuições assimétricas (long-tail)
2. **Robustez a outliers:** Menos sensível a valores extremos, comuns em métricas de software (PRs muito grandes ou muito longos)
3. **Medição de relações monotônicas:** Captura relações que não são necessariamente lineares, mas seguem uma tendência consistente de aumento ou diminuição

**Interpretação dos valores de correlação:**

- ρ próximo de 0: correlação fraca/inexistente
- 0.1 ≤ |ρ| < 0.3: correlação fraca
- 0.3 ≤ |ρ| < 0.5: correlação moderada
- |ρ| ≥ 0.5: correlação forte

**Significância estatística:**

- Utilizamos α = 0.05 como limiar de significância
- Com n = 947.735, virtualmente todas as correlações são estatisticamente significantes
- Portanto, focamos na **magnitude prática** das correlações, não apenas na significância estatística

### 2.4. Análise Descritiva

Para cada variável, calculamos estatísticas descritivas separadas para:

- PRs merged (aceitos)
- PRs não merged (rejeitados/fechados)
- Conjunto geral de dados

As principais métricas reportadas são:

- **Mediana:** Valor central da distribuição, robusto a outliers
- **Média:** Valor médio, sensível a outliers mas útil para comparação
- **Desvio padrão:** Medida de dispersão dos dados
- **Mínimo e máximo:** Limites dos valores observados

---

## 3. Resultados

> 💡 **Nota:** Para melhor compreensão dos resultados, consulte os gráficos disponíveis na pasta `docs/charts/`:
>
> - `correlation_heatmap.png` - Visualização geral de todas as correlações
> - `correlation_bars.png` - Comparação visual entre grupos de RQs
> - `descriptive_comparison.png` - Comparação de medianas entre PRs merged e não merged
> - `distributions.png` - Distribuições das variáveis principais
> - `scatter_correlations.png` - Relações entre variáveis
> - `summary_dashboard.png` - Dashboard completo com todas as descobertas

### 3.1. Estatísticas Descritivas Gerais

Analisamos **947.735 Pull Requests**, distribuídos da seguinte forma:

| Métrica                               | Geral | PRs Merged | PRs Não Merged |
| ------------------------------------- | ----- | ---------- | -------------- |
| **Tamanho do PR (linhas)**            |       |            |                |
| - Mediana                             | 37    | 38         | 36             |
| **Tempo de Análise (horas)**          |       |            |                |
| - Mediana                             | 48.14 | 33.49      | 147.10         |
| **Tamanho da Descrição (caracteres)** |       |            |                |
| - Mediana                             | 324   | 318        | 340            |
| **Interações (comentários)**          |       |            |                |
| - Mediana                             | 3     | 3          | 5              |
| **Número de Revisões**                |       |            |                |
| - Mediana                             | 2     | 2          | 2              |

**Observações iniciais:**

- PRs não merged levam **4.4x mais tempo** para serem fechados (mediana de 147h vs 33h)
- PRs não merged têm **67% mais interações** (mediana de 5 vs 3)
- O tamanho do PR é similar entre merged e não merged (diferença de apenas 2 linhas na mediana)
- Descrições de PRs não merged são ligeiramente mais longas (340 vs 318 caracteres)

### 3.2. Análise de Correlações

Todas as correlações reportadas são estatisticamente significantes (p < 0.001) devido ao grande tamanho amostral.

> 📊 **Visualização:** Veja `correlation_heatmap.png` e `correlation_bars.png` para uma representação visual completa das correlações.

#### 3.2.1. RQ01: Tamanho do PR vs Feedback Final

**Correlação de Spearman: ρ = 0.0109**

- **Magnitude:** Correlação positiva **muito fraca**, praticamente inexistente
- **Interpretação:** O tamanho do PR tem **impacto mínimo** na probabilidade de merge
- **Significado prático:** Embora estatisticamente significante, o efeito é negligível do ponto de vista prático

#### 3.2.2. RQ02: Tempo de Análise vs Feedback Final

**Correlação de Spearman: ρ = -0.2571**

- **Magnitude:** Correlação negativa **fraca a moderada**
- **Interpretação:** Quanto maior o tempo de análise, **menor a probabilidade de merge**
- **Significado prático:** Esta é a correlação mais forte com o status de merge, indicando que PRs que levam muito tempo tendem a ser fechados sem merge

#### 3.2.3. RQ03: Descrição do PR vs Feedback Final

**Correlação de Spearman: ρ = -0.0210**

- **Magnitude:** Correlação negativa **muito fraca**
- **Interpretação:** Descrições mais longas têm **correlação negativa muito fraca** com merge
- **Significado prático:** O tamanho da descrição não é um fator relevante para aprovação

#### 3.2.4. RQ04: Interações vs Feedback Final

**Correlação de Spearman: ρ = -0.2453**

- **Magnitude:** Correlação negativa **fraca a moderada**
- **Interpretação:** Mais interações estão associadas a **menor probabilidade de merge**
- **Significado prático:** Interações extensivas indicam problemas ou discussões que podem levar à rejeição

#### 3.2.5. RQ05: Tamanho do PR vs Número de Revisões

**Correlação de Spearman: ρ = 0.3419**

- **Magnitude:** Correlação positiva **moderada**
- **Interpretação:** PRs maiores recebem **mais revisões**
- **Significado prático:** Esta é uma correlação moderadamente forte, indicando que o tamanho influencia o processo de revisão

#### 3.2.6. RQ06: Tempo de Análise vs Número de Revisões

**Correlação de Spearman: ρ = 0.3509**

- **Magnitude:** Correlação positiva **moderada**
- **Interpretação:** Quanto maior o tempo de análise, **mais revisões** são realizadas
- **Significado prático:** Processos de revisão mais longos acumulam mais rodadas de feedback

#### 3.2.7. RQ07: Descrição do PR vs Número de Revisões

**Correlação de Spearman: ρ = 0.1291**

- **Magnitude:** Correlação positiva **fraca**
- **Interpretação:** Descrições mais longas têm **leve associação** com mais revisões
- **Significado prático:** O tamanho da descrição tem impacto limitado no número de revisões

#### 3.2.8. RQ08: Interações vs Número de Revisões

**Correlação de Spearman: ρ = 0.5842**

- **Magnitude:** Correlação positiva **forte**
- **Interpretação:** Esta é a **correlação mais forte** observada em todo o estudo
- **Significado prático:** Interações e revisões estão fortemente conectadas, formando um ciclo de feedback iterativo

---

## 4. Discussão

### 4.1. Confronto com as Hipóteses Iniciais

#### H1.1 - Tamanho do PR e Status (REFUTADA)

**Hipótese:** PRs maiores teriam menor taxa de aprovação  
**Resultado:** ρ = 0.0109 (correlação praticamente nula)

**Discussão:**  
Surpreendentemente, o tamanho do PR **não tem impacto significativo** na probabilidade de merge. A mediana de PRs merged (38 linhas) é virtualmente idêntica à de PRs não merged (36 linhas). Isso contradiz a intuição de que PRs menores seriam mais facilmente aceitos.

**Possíveis explicações:**

1. **Qualidade sobre quantidade:** O que importa é a qualidade da mudança, não seu tamanho
2. **Contexto do projeto:** Em projetos maduros, mudanças grandes podem ser normais e bem aceitas quando necessárias
3. **Revisão eficiente:** Ferramentas modernas de code review facilitam a análise de PRs grandes
4. **Seleção de amostra:** PRs muito grandes podem ter sido filtrados antes da submissão

#### H1.2 - Tempo de Análise e Status (CONFIRMADA)

**Hipótese:** Maior tempo de análise levaria a menor taxa de merge  
**Resultado:** ρ = -0.2571 (correlação negativa moderada)

**Discussão:**  
Esta hipótese foi **confirmada** com a correlação mais forte observada para o status de merge. A mediana de tempo para PRs não merged é **4.4x maior** (147h vs 33h).

**Interpretação:**

- PRs que demoram muito provavelmente encontram problemas significativos
- Tempos longos podem indicar falta de consenso ou abandono
- É o **melhor preditor individual** do status de merge entre as variáveis analisadas

#### H1.3 - Descrição do PR e Status (REFUTADA)

**Hipótese:** Descrições mais longas levariam a maior taxa de aprovação  
**Resultado:** ρ = -0.0210 (correlação negativa muito fraca)

**Discussão:**  
Contra nossa expectativa, descrições mais longas têm uma **correlação negativa** (embora mínima) com merge. PRs não merged têm descrições ligeiramente mais longas (340 vs 318 caracteres na mediana).

**Possíveis explicações:**

1. **Descrições defensivas:** Desenvolvedores podem escrever descrições longas para PRs problemáticos
2. **Qualidade vs quantidade:** Descrições concisas podem ser mais efetivas que longas
3. **Overhead cognitivo:** Descrições muito longas podem dificultar a revisão
4. **Efeito confundidor:** PRs complexos que tendem a ser rejeitados podem exigir descrições mais longas

#### H1.4 - Interações e Status (CONFIRMADA)

**Hipótese:** Mais interações levariam a menor taxa de merge  
**Resultado:** ρ = -0.2453 (correlação negativa moderada)

**Discussão:**  
A hipótese foi **confirmada**. PRs não merged têm 67% mais interações (mediana de 5 vs 3). A correlação é a segunda mais forte para predição de status.

**Interpretação:**

- Muitas interações frequentemente indicam **problemas a resolver**
- Discussões extensas podem sinalizar **falta de consenso**
- Não necessariamente significa má qualidade, mas indica **complexidade** do processo

#### H2.1 - Tamanho do PR e Número de Revisões (CONFIRMADA)

**Hipótese:** PRs maiores receberiam mais revisões  
**Resultado:** ρ = 0.3419 (correlação positiva moderada)

**Discussão:**  
Hipótese **confirmada** com correlação moderada. PRs maiores naturalmente exigem mais escrutínio e rodadas de revisão.

**Implicações:**

- Desenvolvedores devem **esperar mais iterações** em PRs grandes
- Incentiva a prática de **dividir PRs grandes** em menores para agilizar o processo

#### H2.2 - Tempo de Análise e Número de Revisões (CONFIRMADA)

**Hipótese:** Maior tempo de análise levaria a mais revisões  
**Resultado:** ρ = 0.3509 (correlação positiva moderada)

**Discussão:**  
Hipótese **confirmada**. Esta é a correlação positiva mais forte com número de revisões (exceto interações).

**Interpretação:**

- Processos iterativos naturalmente **acumulam tempo e revisões**
- Cada revisão adiciona tempo ao processo, criando um **ciclo de feedback**

#### H2.3 - Descrição do PR e Número de Revisões (PARCIALMENTE CONFIRMADA)

**Hipótese:** Descrições longas teriam correlação fraca ou inexistente com revisões  
**Resultado:** ρ = 0.1291 (correlação positiva fraca)

**Discussão:**  
A hipótese foi **parcialmente confirmada**. Há uma correlação positiva, mas fraca.

**Interpretação:**

- Descrições mais longas podem indicar PRs mais **complexos** que necessitam mais revisões
- O efeito é limitado, sugerindo que a descrição não é fator determinante

#### H2.4 - Interações e Número de Revisões (CONFIRMADA FORTEMENTE)

**Hipótese:** Forte correlação positiva entre interações e revisões  
**Resultado:** ρ = 0.5842 (correlação positiva FORTE)

**Discussão:**  
Esta é a **correlação mais forte** encontrada em todo o estudo. Hipótese **fortemente confirmada**.

**Interpretação:**

- Interações e revisões formam um **ciclo iterativo natural**
- Cada revisão gera discussão, que leva a nova revisão
- É a **relação mais previsível** observada

### 4.2. Principais Descobertas

1. **Tamanho não importa (para merge):** Contrariando a sabedoria convencional, o tamanho do PR tem impacto negligível na aprovação

2. **Tempo é o fator crítico:** O tempo de análise é o melhor preditor de rejeição (ρ = -0.26)

3. **Interações duplo-papel:** Interações predizem tanto rejeição (ρ = -0.25) quanto mais revisões (ρ = 0.58)

4. **Descrição superestimada:** O tamanho da descrição tem efeito mínimo em ambos os resultados

5. **Ciclo virtuoso/vicioso:** PRs entram em ciclos onde mais tempo → mais revisões → mais interações → menor chance de merge

### 4.3. Limitações do Estudo

1. **Causalidade:** Correlações não implicam causalidade. Pode haver variáveis confundidoras não medidas.

2. **Heterogeneidade:** Diferentes projetos têm culturas de revisão diferentes, não capturadas na análise agregada.

3. **Métricas proxy:** "Interações" como comentários pode não capturar toda a complexidade do processo de revisão.

4. **Viés de seleção:** Repositórios populares podem não representar o desenvolvimento de software em geral.

5. **Dados temporais:** Não analisamos tendências temporais ou sazonalidade.

### 4.4. Implicações Práticas

**Para Desenvolvedores:**

- ✅ **Não tema PRs grandes** quando necessários - tamanho não afeta aprovação
- ⚠️ **Responda rapidamente** ao feedback - tempo longo prediz rejeição
- 💬 **Minimize discussões desnecessárias** - muitas interações correlacionam com rejeição
- 📝 **Descrições concisas** parecem tão efetivas quanto longas

**Para Revisores:**

- ⏱️ **Priorize feedback rápido** - tempos longos levam a abandono
- 🎯 **Foque em qualidade** - tamanho do PR não deve ser critério primário
- 🔄 **Minimize rodadas de revisão** - cada iteração adicional reduz chance de merge

**Para Projetos:**

- 📊 **Monitore tempo de análise** como métrica de saúde do processo
- 🤖 **Automatize revisões** para reduzir tempo de feedback
- 📋 **Estabeleça SLAs** para revisão de PRs
- 🔍 **Investigue PRs com muitas interações** - podem precisar de intervenção

---

## 5. Conclusão

Este estudo analisou 947.735 Pull Requests para identificar fatores que influenciam o sucesso e a eficiência do processo de code review. Utilizando o coeficiente de correlação de Spearman, encontramos evidências que desafiam algumas crenças comuns:

**Principais Conclusões:**

1. **O tamanho do PR não é um fator significativo** para aprovação (ρ = 0.01), contrariando a sabedoria convencional de que "PRs menores são sempre melhores".

2. **O tempo de análise é o preditor mais importante** de rejeição (ρ = -0.26), sugerindo que feedback rápido é crucial.

3. **Interações têm papel ambíguo:** predizem tanto rejeição (ρ = -0.25) quanto mais revisões (ρ = 0.58), indicando que discussões extensas podem ser tanto problemáticas quanto parte natural de processos iterativos.

4. **Descrições longas não garantem aprovação** (ρ = -0.02), sugerindo que qualidade supera quantidade.

5. **O número de revisões é fortemente influenciado** por interações (ρ = 0.58), tamanho (ρ = 0.34) e tempo (ρ = 0.35).

**Contribuição Científica:**

Este trabalho contribui para a literatura de engenharia de software empírica ao fornecer evidências quantitativas sobre práticas de code review em larga escala, utilizando métodos estatísticos robustos e uma amostra significativa.

**Trabalhos Futuros:**

- Análise temporal da evolução das métricas
- Segmentação por linguagem de programação e domínio
- Estudo qualitativo das interações para categorizar tipos de discussão
- Modelagem preditiva usando machine learning
- Análise de impacto da experiência dos desenvolvedores

---

## Referências

1. Dados coletados via GitHub GraphQL API (2025)
2. Análise estatística com Python (pandas, scipy, numpy)
3. Método de correlação: Spearman's rank correlation coefficient
4. Ferramentas: Python 3.13, pandas, scipy.stats

---

## Apêndice: Reprodutibilidade

Todos os dados, scripts e análises estão disponíveis no repositório:

- **Código de coleta:** `code/collector.py`
- **Código de análise:** `code/analyzer.py`
- **Dados brutos:** `code/datasets/`
- **Resultados:** `code/results/`

**Execução:**

```bash
# Coletar dados
python collector.py --max-prs 150

# Analisar dados
python analyzer.py
```

**Ambiente:**

- Python 3.13+
- Dependências: pandas, numpy, scipy, requests, tqdm

---

**Documento gerado em:** 16 de Outubro de 2025  
**Total de PRs analisados:** 947.735  
**Método estatístico:** Correlação de Spearman  
**Nível de significância:** α = 0.05
