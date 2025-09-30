# GitHub Code Review & Pull Requests Analysis

Este repositório contém ferramentas para coleta e análise de pull requests de repositórios populares do GitHub. O projeto foca na extração de dados de PRs para análise de padrões de desenvolvimento, tempo de revisão e características de contribuição em projetos open source.

## Índice

- [Descrição](#descrição)
- [Requisitos](#requisitos)
- [Configuração](#configuração)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Dados Coletados](#dados-coletados)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Descrição

Este projeto automatiza a coleta de dados de pull requests dos repositórios mais populares do GitHub (com mais de 10.000 stars). O foco é em PRs que foram mergeados ou fechados e que passaram por pelo menos uma revisão, com duração mínima de 1 hora.

### Funcionalidades

- 🔍 **Coleta Automatizada**: Busca repositórios populares via GraphQL API do GitHub
- 📊 **Filtragem Inteligente**: Seleciona apenas PRs com pelo menos 1 revisão e duração ≥ 1h
- 💾 **Exportação por Repositório**: Gera um CSV individual para cada repositório
- 🔄 **Recuperação de Erros**: Sistema robusto com retry e backoff exponencial
- 📈 **Progresso Visual**: Barras de progresso detalhadas para acompanhamento

### Métricas Coletadas

Para cada pull request, são extraídas as seguintes informações:

- Número do PR
- Título
- Autor
- Data de criação
- Data de fechamento/merge
- Quantidade de revisões
- Tempo total em aberto (em horas)

## Requisitos

- Python >= 3.8
- Token de acesso pessoal do GitHub
- Bibliotecas: `requests`, `tqdm`

## Configuração

1. **Obtenha um token do GitHub**:

   - Acesse GitHub Settings > Developer settings > Personal access tokens
   - Gere um novo token com permissões para leitura de repositórios públicos

2. **Configure o token `GITHUB_TOKEN` nas variáveis de ambiente do seu sistema**:

   ```bash
   export GITHUB_TOKEN=seu_token_aqui
   ```

   No Windows (cmd):

   ```cmd
   set GITHUB_TOKEN=seu_token_aqui
   ```

3. **Instale as dependências**:

   ```bash
   pip install -r requirements.txt
   ```

## Execução Básica

```bash
cd code
python collector.py
```

### Funcionamento do Script

1. **Busca Repositórios**: Coleta os 200 repositórios com mais stars no GitHub
2. **Filtragem**: Seleciona apenas repos com mais de 100 PRs
3. **Coleta de PRs**: Para cada repositório, extrai todos os PRs mergeados/fechados
4. **Processamento**: Filtra PRs com ≥1 revisão e duração ≥1h
5. **Exportação**: Salva os dados em CSV individual por repositório

### Parâmetros Configuráveis

No arquivo `collector.py`, você pode ajustar:

```python
# Quantidade de repositórios para processar
repo_count < 200  # Linha 151

# Filtro de PRs mínimos por repositório
if repo_node["pullRequests"]["totalCount"] < 100:  # Linha 158

# Filtro de revisões mínimas
if node["reviews"]["totalCount"] < 1:  # Linha 103

# Filtro de duração mínima (em segundos)
if delta.total_seconds() >= 3600:  # Linha 113 (1 hora)
```

## Estrutura do Projeto

```bash
github-pr-analysis/
├── README.md           # Documentação principal
├── REPORT.md          # Relatório de análise
└── code/
    ├── collector.py    # Script principal de coleta
    ├── dataset_prs.csv # Dataset consolidado
    ├── datasets/       # CSVs individuais por repositório
    │   ├── microsoft_vscode.csv
    │   ├── facebook_react.csv
    │   └── ...
    └── queries/        # Queries GraphQL
        ├── pr_query.graphql
        └── repo_query.graphql
```

## Dados Coletados

### Formato dos CSVs

Cada arquivo CSV contém as seguintes colunas:

| Coluna             | Descrição                                |
| ------------------ | ---------------------------------------- |
| `number`           | Número do pull request                   |
| `title`            | Título do pull request                   |
| `author`           | Login do autor                           |
| `createdAt`        | Data/hora de criação (ISO 8601)          |
| `closedOrMergedAt` | Data/hora de fechamento/merge (ISO 8601) |
| `reviewsCount`     | Quantidade de revisões recebidas         |
| `hoursOpen`        | Tempo total em aberto (em horas)         |

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request
