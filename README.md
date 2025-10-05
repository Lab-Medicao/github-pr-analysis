# 🧠 GitHub Code Review & Pull Requests Analysis  
### *Caracterizando a Atividade de Code Review no GitHub*

---

## 📋 Sumário

- [1. Informações do Grupo](#1-informações-do-grupo)  
- [2. Introdução](#2-introdução)  
- [3. Descrição Técnica do Projeto](#3-descrição-técnica-do-projeto)  
- [4. Requisitos e Configuração](#4-requisitos-e-configuração)  
- [5. Estrutura do Projeto](#5-estrutura-do-projeto)  
- [6. Metodologia de Coleta e Análise](#6-metodologia-de-coleta-e-análise)  
- [7. Métricas e Questões de Pesquisa](#7-métricas-e-questões-de-pesquisa)  
- [8. Resultados e Discussão](#8-resultados-e-discussão)  
- [9. Conclusão](#9-conclusão)  
- [10. Contribuição](#10-contribuição)  
- [11. Referências](#11-referências)  
- [12. Apêndices](#12-apêndices)  

---

## 1. 🧑‍💻 Informações do Grupo

| Campo | Informação |
|-------|-------------|
| **🎓 Curso:** | Engenharia de Software |
| **📘 Disciplina:** | Laboratório de Experimentação de Software |
| **🗓 Período:** | 6° Período |
| **👨‍🏫 Professor:** | Prof. Dr. João Paulo Carneiro Aramuni |
| **👥 Membros:** | Ana Luiza Machado Alves, Lucas Henrique Chaves de Barros, Raquel Inez de Almeida Calazans |

---

## 2. 🧩 Introdução

O presente projeto tem como objetivo **analisar a atividade de code review em repositórios populares do GitHub**, identificando padrões que influenciam o processo de merge de *pull requests (PRs)*.  
A pesquisa combina **automação da coleta de dados via API GraphQL do GitHub** e **análises quantitativas** sobre métricas de revisão, tempo, interações e qualidade das contribuições.

---

### 2.1. Questões de Pesquisa (Research Questions – RQs)

As perguntas de pesquisa foram estruturadas em dois grupos principais:

#### 🔹 Grupo 1 — Feedback Final das Revisões
| Código | Questão |
|--------|----------|
| **RQ01** | Qual a relação entre o tamanho dos PRs e o feedback final das revisões? |
| **RQ02** | Qual a relação entre o tempo de análise dos PRs e o feedback final das revisões? |
| **RQ03** | Qual a relação entre a descrição dos PRs e o feedback final das revisões? |
| **RQ04** | Qual a relação entre as interações nos PRs e o feedback final das revisões? |

#### 🔹 Grupo 2 — Número de Revisões
| Código | Questão |
|--------|----------|
| **RQ05** | Qual a relação entre o tamanho dos PRs e o número de revisões realizadas? |
| **RQ06** | Qual a relação entre o tempo de análise dos PRs e o número de revisões realizadas? |
| **RQ07** | Qual a relação entre a descrição dos PRs e o número de revisões realizadas? |
| **RQ08** | Qual a relação entre as interações nos PRs e o número de revisões realizadas? |

---

### 2.2. Hipóteses Informais (IH)

As hipóteses estabelecem expectativas sobre o comportamento dos PRs com base nas RQs.  
Por exemplo, **PRs maiores e com menos descrições claras** tendem a **ser rejeitados ou exigirem mais revisões**, enquanto **PRs detalhados e com mais interações** têm **maior chance de aprovação**.

---

## 3. ⚙️ Descrição Técnica do Projeto

Este repositório contém scripts e consultas que automatizam a **coleta, filtragem e exportação de dados de pull requests** de repositórios populares do GitHub (com mais de 10.000 estrelas).

### Funcionalidades Principais

- 🔍 **Coleta Automatizada:** via **GitHub GraphQL API**  
- 📊 **Filtragem Inteligente:** PRs com ≥1 revisão e duração ≥1 hora  
- 💾 **Exportação Individual:** CSV por repositório  
- 🔄 **Sistema Resiliente:** retry e backoff exponencial  
- 📈 **Progresso Visual:** barras de progresso detalhadas  

### Métricas Coletadas

| Campo | Descrição |
|--------|------------|
| `number` | Número do PR |
| `title` | Título |
| `author` | Autor |
| `createdAt` | Data de criação |
| `closedOrMergedAt` | Data de fechamento/merge |
| `reviewsCount` | Número de revisões |
| `hoursOpen` | Tempo total em aberto (h) |

---

## 4. 🧩 Requisitos e Configuração

### Requisitos

- **Python ≥ 3.8**  
- **Token de acesso do GitHub (GITHUB_TOKEN)**  
- Bibliotecas: `requests`, `tqdm`

### Configuração

1. Gere seu token em  
   `Settings > Developer Settings > Personal Access Tokens`
2. Exporte o token como variável de ambiente:
   ```bash
   export GITHUB_TOKEN=seu_token_aqui
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
4. Execute o script:
   ```bash
   cd code
   python collector.py
## 5. 🧱 Estrutura do Projeto
   ```bash
      github-pr-analysis/
      ├── README.md
      ├── REPORT.md
      └── code/
         ├── collector.py
         ├── dataset_prs.csv
         ├── datasets/
         │   ├── microsoft_vscode.csv
         │   ├── facebook_react.csv
         │   └── ...
         └── queries/
            ├── pr_query.graphql
            └── repo_query.graphql
```

## 6. 🧮 Metodologia de Coleta e Análise

O processo foi dividido nas seguintes etapas:

1. **Coleta de Dados:** realizada via **GitHub GraphQL API**, utilizando repositórios top-*N* por número de estrelas.  
2. **Filtragem:** exclusão de repositórios arquivados, inativos ou com *pull requests* (PRs) irrelevantes.  
3. **Normalização:** conversão de datas, remoção de valores nulos e padronização das linguagens de programação.  
4. **Cálculo de Métricas:** derivação de tempo de revisão, número de revisões e interações por PR.  
5. **Visualização:** geração de gráficos e tabelas exploratórias para análise dos resultados.  

---

## 7. 📊 Métricas e Questões de Pesquisa

### 7.1. Métricas de Laboratório (LM)

| **Código** | **Métrica** | **Descrição** |
|-------------|--------------|----------------|
| **LM01** | Tamanho | Linhas adicionadas/removidas |
| **LM02** | Tempo de Análise | Diferença entre criação e merge |
| **LM03** | Descrição | Tamanho do corpo do PR |
| **LM04** | Interações | Número de comentários e participantes |

---

### 7.2. Métricas Adicionais (AM)

| **Código** | **Métrica** | **Descrição** |
|-------------|--------------|----------------|
| **AM01** | Linguagem Primária | Linguagem principal do repositório |
| **AM02** | Forks/PRs Aceitas | Relação entre forks e merges |
| **AM03** | Evolução Temporal | Histórico de releases e PRs |
| **AM04** | Big Numbers | Quantidade de stars, forks, commits e releases |

---

## 8. 📈 Resultados e Discussão

Os resultados incluem **estatísticas descritivas**, **gráficos exploratórios** e **análises relacionais** entre métricas e hipóteses.

- **Distribuição por Linguagem:** Python, JavaScript e Java dominam os repositórios analisados.  
- **Correlação entre Tamanho e Revisões:** PRs maiores tendem a ter mais revisões e maior tempo de merge.  
- **Interações e Aprovação:** PRs com descrições detalhadas e mais interações apresentam maior taxa de aprovação.  
- **Evolução Temporal:** repositórios mais maduros apresentam PRs menores e revisões mais rápidas.  

> As hipóteses **IH01–IH04** foram majoritariamente **confirmadas**, especialmente aquelas que relacionam **descrição e interações** com **aprovação de PRs**.

---

## 9. 🏁 Conclusão

O projeto permitiu **caracterizar o comportamento de revisões no GitHub**, revelando padrões claros:

- Repositórios populares possuem **processos de revisão estruturados e colaborativos**.  
- PRs **menores e bem documentados** tendem a ser **aprovados mais rapidamente**.  
- A **atividade de revisão** é fortemente influenciada pelo **engajamento dos revisores** e pela **clareza das descrições**.  

### 🧩 Desafios enfrentados

- Limites da API GraphQL e paginação de grandes volumes de dados.  
- Normalização de campos inconsistentes entre repositórios.  
- Processamento paralelo de repositórios de grande porte.  

### 🚀 Trabalhos futuros

- Ampliar a análise para **métricas de qualidade de código**.  
- Integrar **dashboards interativos** (ex.: Power BI, Plotly Dash).  
- Estudar **diferenças entre linguagens e ecossistemas**.  

---
