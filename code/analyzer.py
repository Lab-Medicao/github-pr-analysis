import os
import pandas as pd
import numpy as np
from glob import glob
from scipy import stats
import json
import matplotlib.pyplot as plt
import seaborn as sns


def load_all_datasets(input_folder):
    """Carrega todos os CSVs e agrega em um único DataFrame"""
    csv_files = glob(os.path.join(input_folder, '*.csv'))
    all_data = []

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            df['repository'] = os.path.basename(csv_file).replace('.csv', '')
            all_data.append(df)
        except Exception as e:
            print(f"Erro ao ler {csv_file}: {e}")

    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df


def calculate_pr_size(row):
    """Calcula o tamanho do PR (adições + deleções)"""
    additions = row.get('additions', 0) if pd.notna(
        row.get('additions')) else 0
    deletions = row.get('deletions', 0) if pd.notna(
        row.get('deletions')) else 0
    return additions + deletions


def calculate_analysis_time(row):
    """Calcula o tempo de análise em horas"""
    created = pd.to_datetime(row.get('created_at'), errors='coerce')
    closed = pd.to_datetime(row.get('closed_at'), errors='coerce')

    if pd.isna(created) or pd.isna(closed):
        return None

    return (closed - created).total_seconds() / 3600  # em horas


def has_description(row):
    """Verifica se o PR tem descrição (binário: 1 ou 0)"""
    body = row.get('body', '')
    if pd.isna(body) or body == '' or body is None:
        return 0
    return 1


def description_length(row):
    """Retorna o tamanho da descrição"""
    body = row.get('body', '')
    if pd.isna(body) or body == '' or body is None:
        return 0
    return len(str(body))


def prepare_data(df):
    """Prepara os dados calculando as métricas necessárias"""
    # Tamanho do PR (já temos additions e deletions)
    df['pr_size'] = (df['additions'].fillna(0) + df['deletions'].fillna(0))

    # Tempo de análise (já temos hoursOpen)
    df['analysis_time_hours'] = df['hoursOpen'].fillna(0)

    # Tamanho da descrição (já temos bodyLength)
    df['description_length'] = df['bodyLength'].fillna(0)

    # Descrição (binária)
    df['has_description'] = (df['bodyLength'] > 0).astype(int)

    # Status binário (já temos merged)
    df['is_merged'] = df['merged'].fillna(False).astype(int)

    # Número de interações (já temos interactionsCount)
    df['interactions'] = df['interactionsCount'].fillna(0)

    # Número de revisões (já temos reviewsCount)
    df['num_reviews'] = df['reviewsCount'].fillna(0)

    return df


def analyze_correlations(df):
    """Calcula correlações de Spearman entre variáveis"""

    # Variáveis independentes
    independent_vars = {
        'pr_size': 'Tamanho do PR',
        'analysis_time_hours': 'Tempo de Análise (horas)',
        'description_length': 'Tamanho da Descrição',
        'interactions': 'Número de Interações (comentários)'
    }

    # Variáveis dependentes
    dependent_vars = {
        'is_merged': 'Status (Merged)',
        'num_reviews': 'Número de Revisões'
    }

    results = {}

    for indep_key, indep_name in independent_vars.items():
        for dep_key, dep_name in dependent_vars.items():
            # Filtrar valores válidos
            valid_data = df[[indep_key, dep_key]].dropna()

            if len(valid_data) < 3:
                continue

            # Calcular correlação de Spearman
            corr, p_value = stats.spearmanr(
                valid_data[indep_key], valid_data[dep_key])

            results[f"{indep_name} vs {dep_name}"] = {
                'correlation': float(corr),
                'p_value': float(p_value),
                'n_samples': int(len(valid_data)),
                'significant': bool(p_value < 0.05)
            }

    return results


def calculate_descriptive_stats(df):
    """Calcula estatísticas descritivas por status de PR"""

    merged_prs = df[df['is_merged'] == 1]
    not_merged_prs = df[df['is_merged'] == 0]

    metrics = ['pr_size', 'analysis_time_hours',
               'description_length', 'interactions', 'num_reviews']

    stats_results = {}

    for metric in metrics:
        merged_data = merged_prs[metric].dropna()
        not_merged_data = not_merged_prs[metric].dropna()

        stats_results[metric] = {
            'merged': {
                'median': merged_data.median(),
                'mean': merged_data.mean(),
                'std': merged_data.std(),
                'min': merged_data.min(),
                'max': merged_data.max(),
                'count': len(merged_data)
            },
            'not_merged': {
                'median': not_merged_data.median(),
                'mean': not_merged_data.mean(),
                'std': not_merged_data.std(),
                'min': not_merged_data.min(),
                'max': not_merged_data.max(),
                'count': len(not_merged_data)
            },
            'overall': {
                'median': df[metric].dropna().median(),
                'mean': df[metric].dropna().mean(),
                'std': df[metric].dropna().std(),
                'min': df[metric].dropna().min(),
                'max': df[metric].dropna().max(),
                'count': len(df[metric].dropna())
            }
        }

    return stats_results


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(script_dir, 'datasets')
    results_folder = os.path.join(script_dir, 'results')
    os.makedirs(results_folder, exist_ok=True)

    print("📊 Carregando dados de todos os repositórios...")
    df = load_all_datasets(input_folder)
    print(f"✅ Total de PRs carregados: {len(df)}")

    print("\n🔧 Preparando dados e calculando métricas...")
    df = prepare_data(df)

    print("\n📈 Calculando correlações (Spearman)...")
    correlations = analyze_correlations(df)

    print("\n📊 Calculando estatísticas descritivas...")
    descriptive_stats = calculate_descriptive_stats(df)

    # Salvar resultados em JSON
    print("\n💾 Salvando resultados...")

    # Converter valores numpy para tipos nativos do Python
    def convert_to_serializable(obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, dict):
            return {key: convert_to_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        return obj

    correlations = convert_to_serializable(correlations)
    descriptive_stats = convert_to_serializable(descriptive_stats)

    with open(os.path.join(results_folder, 'correlations.json'), 'w', encoding='utf-8') as f:
        json.dump(correlations, f, indent=2, ensure_ascii=False)

    with open(os.path.join(results_folder, 'descriptive_stats.json'), 'w', encoding='utf-8') as f:
        json.dump(descriptive_stats, f, indent=2, ensure_ascii=False)

    # Salvar DataFrame processado
    df.to_csv(os.path.join(results_folder, 'processed_data.csv'), index=False)

    # =====================
    # Geração de gráficos por RQ
    # =====================

    # Configs visuais
    sns.set_theme(style="whitegrid", palette="muted")

    charts_folder = os.path.join(script_dir, '..', 'docs', 'charts')
    os.makedirs(charts_folder, exist_ok=True)

    def _annotate_corr(ax, key: str):
        if key in correlations:
            c = correlations[key]
            sig = '✓' if c.get('significant') else '✗'
            ax.text(0.02, 0.98,
                    f"ρ={c.get('correlation', 0):.3f}\nP={c.get('p_value', 1):.3f}\nn={c.get('n_samples', 0)}  {sig}",
                    transform=ax.transAxes,
                    va='top', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    def _violin_status(df_plot: pd.DataFrame, metric_col: str, title: str, ylabel: str, out_name: str, corr_key: str):
        data = df_plot[[metric_col, 'is_merged']].dropna().copy()
        if data.empty:
            return
        # Limitar outliers para melhor visualização (IQR 3.0x)
        Q1 = data[metric_col].quantile(0.25)
        Q3 = data[metric_col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 3 * IQR
        upper = Q3 + 3 * IQR
        data = data[(data[metric_col] >= lower) & (data[metric_col] <= upper)]

        plt.figure(figsize=(10, 7))
        parts = plt.violinplot([
            data[data['is_merged'] == 1][metric_col],
            data[data['is_merged'] == 0][metric_col]
        ], positions=[1, 2], showmeans=True, showmedians=True, widths=0.8)

        for pc, color in zip(parts['bodies'], ['#2ca02c', '#d62728']):
            pc.set_facecolor(color)
            pc.set_alpha(0.6)

        ax = plt.gca()
        ax.set_xticks([1, 2])
        ax.set_xticklabels(['MERGED', 'CLOSED'])
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        _annotate_corr(ax, corr_key)

        plt.tight_layout()
        plt.savefig(os.path.join(charts_folder, out_name),
                    dpi=300, bbox_inches='tight')
        plt.close()

    def _scatter_reviews(df_plot: pd.DataFrame, xcol: str, xlabel: str, title: str, out_name: str, corr_key: str):
        data = df_plot[[xcol, 'num_reviews']].dropna().copy()
        if data.empty:
            return
        # Amostra para performance
        n = len(data)
        if n > 100000:
            data = data.sample(100000, random_state=42)

        # Limitar eixo X ao percentil 99.5 para melhor leitura
        x_cap = data[xcol].quantile(0.995)
        data[xcol] = np.minimum(data[xcol], x_cap)

        plt.figure(figsize=(10, 7))
        ax = sns.regplot(data=data, x=xcol, y='num_reviews',
                         scatter_kws={'alpha': 0.25, 's': 15},
                         line_kws={'color': 'black'})
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Número de Revisões')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(alpha=0.3)
        _annotate_corr(ax, corr_key)

        plt.tight_layout()
        plt.savefig(os.path.join(charts_folder, out_name),
                    dpi=300, bbox_inches='tight')
        plt.close()

    # Mapas de nomes (devem bater com as chaves do JSON de correlações)
    metric_labels = {
        'pr_size': 'Tamanho do PR',
        'analysis_time_hours': 'Tempo de Análise (horas)',
        'description_length': 'Tamanho da Descrição',
        'interactions': 'Número de Interações (comentários)'
    }

    # RQ01–RQ04: fator vs Status (Merged)
    _violin_status(df, 'pr_size',
                   'RQ01: Tamanho do PR × Status (Merged)',
                   'Tamanho do PR (linhas)',
                   'rq01_size_vs_status.png',
                   f"{metric_labels['pr_size']} vs Status (Merged)")

    _violin_status(df, 'analysis_time_hours',
                   'RQ02: Tempo de Análise × Status (Merged)',
                   'Tempo de Análise (horas)',
                   'rq02_time_vs_status.png',
                   f"{metric_labels['analysis_time_hours']} vs Status (Merged)")

    _violin_status(df, 'description_length',
                   'RQ03: Tamanho da Descrição × Status (Merged)',
                   'Tamanho da Descrição (caracteres)',
                   'rq03_description_vs_status.png',
                   f"{metric_labels['description_length']} vs Status (Merged)")

    _violin_status(df, 'interactions',
                   'RQ04: Interações × Status (Merged)',
                   'Interações (comentários)',
                   'rq04_interactions_vs_status.png',
                   f"{metric_labels['interactions']} vs Status (Merged)")

    # RQ05–RQ08: fator vs Número de Revisões
    _scatter_reviews(df, 'pr_size',
                     'Tamanho do PR (linhas)',
                     'RQ05: Tamanho do PR × Número de Revisões',
                     'rq05_size_vs_reviews.png',
                     f"{metric_labels['pr_size']} vs Número de Revisões")

    _scatter_reviews(df, 'analysis_time_hours',
                     'Tempo de Análise (horas)',
                     'RQ06: Tempo de Análise × Número de Revisões',
                     'rq06_time_vs_reviews.png',
                     f"{metric_labels['analysis_time_hours']} vs Número de Revisões")

    _scatter_reviews(df, 'description_length',
                     'Tamanho da Descrição (caracteres)',
                     'RQ07: Tamanho da Descrição × Número de Revisões',
                     'rq07_description_vs_reviews.png',
                     f"{metric_labels['description_length']} vs Número de Revisões")

    _scatter_reviews(df, 'interactions',
                     'Interações (comentários)',
                     'RQ08: Interações × Número de Revisões',
                     'rq08_interactions_vs_reviews.png',
                     f"{metric_labels['interactions']} vs Número de Revisões")

    print("\n" + "="*80)
    print("RESUMO DAS CORRELAÇÕES (Spearman)")
    print("="*80)
    for key, value in correlations.items():
        sig = "✓ Significante" if value['significant'] else "✗ Não significante"
        print(f"\n{key}:")
        print(f"  Correlação: {value['correlation']:.4f}")
        print(f"  P-valor: {value['p_value']:.4f}")
        print(f"  Amostras: {value['n_samples']}")
        print(f"  {sig}")

    print("\n" + "="*80)
    print("ESTATÍSTICAS DESCRITIVAS - MEDIANAS")
    print("="*80)

    metric_names = {
        'pr_size': 'Tamanho do PR',
        'analysis_time_hours': 'Tempo de Análise (horas)',
        'description_length': 'Tamanho da Descrição',
        'interactions': 'Interações (comentários)',
        'num_reviews': 'Número de Revisões'
    }

    for metric, name in metric_names.items():
        print(f"\n{name}:")
        print(
            f"  Geral - Mediana: {descriptive_stats[metric]['overall']['median']:.2f}")
        print(
            f"  Merged - Mediana: {descriptive_stats[metric]['merged']['median']:.2f}")
        print(
            f"  Não Merged - Mediana: {descriptive_stats[metric]['not_merged']['median']:.2f}")

    print("\n✅ Análise concluída! Arquivos salvos em:", results_folder)


if __name__ == '__main__':
    main()
