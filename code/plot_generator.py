import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from matplotlib.gridspec import GridSpec

# Configurações de estilo
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11


def load_data():
    """Carrega os dados processados e resultados das análises"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_folder = os.path.join(script_dir, 'results')

    df = pd.read_csv(os.path.join(results_folder, 'processed_data.csv'))

    with open(os.path.join(results_folder, 'correlations.json'), 'r', encoding='utf-8') as f:
        correlations = json.load(f)

    with open(os.path.join(results_folder, 'descriptive_stats.json'), 'r', encoding='utf-8') as f:
        descriptive_stats = json.load(f)

    return df, correlations, descriptive_stats


def plot_correlation_heatmap(correlations, output_folder):
    """Gera heatmap das correlações"""
    # Preparar dados para o heatmap
    metrics = ['Tamanho do PR', 'Tempo de Análise (horas)',
               'Tamanho da Descrição', 'Número de Interações (comentários)']
    outcomes = ['Status (Merged)', 'Número de Revisões']

    corr_matrix = np.zeros((len(metrics), len(outcomes)))

    for i, metric in enumerate(metrics):
        for j, outcome in enumerate(outcomes):
            key = f"{metric} vs {outcome}"
            if key in correlations:
                corr_matrix[i, j] = correlations[key]['correlation']

    # Criar heatmap
    fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.imshow(corr_matrix, cmap='RdBu_r',
                   aspect='auto', vmin=-0.6, vmax=0.6)

    ax.set_xticks(np.arange(len(outcomes)))
    ax.set_yticks(np.arange(len(metrics)))
    ax.set_xticklabels(outcomes)
    ax.set_yticklabels(metrics)

    # Rotacionar labels
    plt.setp(ax.get_xticklabels(), rotation=45,
             ha="right", rotation_mode="anchor")

    # Adicionar valores nas células
    for i in range(len(metrics)):
        for j in range(len(outcomes)):
            text = ax.text(j, i, f'{corr_matrix[i, j]:.3f}',
                           ha="center", va="center", color="black", fontweight='bold')

    ax.set_title('Correlações de Spearman: Variáveis vs Resultados',
                 fontsize=14, fontweight='bold', pad=20)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Coeficiente de Correlação (ρ)', rotation=270, labelpad=20)

    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'correlation_heatmap.png'),
                dpi=300, bbox_inches='tight')
    print("✅ Heatmap de correlações salvo!")
    plt.close()


def plot_correlation_bars(correlations, output_folder):
    """Gera gráficos de barras para correlações por grupo"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # RQs 1-4: Status (Merged)
    metrics_status = ['Tamanho do PR', 'Tempo de Análise (horas)',
                      'Tamanho da Descrição', 'Número de Interações (comentários)']
    corrs_status = []

    for metric in metrics_status:
        key = f"{metric} vs Status (Merged)"
        if key in correlations:
            corrs_status.append(correlations[key]['correlation'])

    colors_status = ['#d62728' if c < 0 else '#2ca02c' for c in corrs_status]

    axes[0].barh(metrics_status, corrs_status,
                 color=colors_status, alpha=0.7, edgecolor='black')
    axes[0].set_xlabel('Correlação de Spearman (ρ)', fontsize=12)
    axes[0].set_title('RQ01-04: Fatores vs Status do PR (Merged)',
                      fontsize=13, fontweight='bold')
    axes[0].axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    axes[0].grid(axis='x', alpha=0.3)

    # Adicionar valores
    for i, v in enumerate(corrs_status):
        axes[0].text(v + (0.01 if v > 0 else -0.01), i, f'{v:.3f}',
                     va='center', ha='left' if v > 0 else 'right', fontweight='bold')

    # RQs 5-8: Número de Revisões
    metrics_reviews = metrics_status
    corrs_reviews = []

    for metric in metrics_reviews:
        key = f"{metric} vs Número de Revisões"
        if key in correlations:
            corrs_reviews.append(correlations[key]['correlation'])

    colors_reviews = ['#1f77b4'] * len(corrs_reviews)

    axes[1].barh(metrics_reviews, corrs_reviews,
                 color=colors_reviews, alpha=0.7, edgecolor='black')
    axes[1].set_xlabel('Correlação de Spearman (ρ)', fontsize=12)
    axes[1].set_title('RQ05-08: Fatores vs Número de Revisões',
                      fontsize=13, fontweight='bold')
    axes[1].axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    axes[1].grid(axis='x', alpha=0.3)

    # Adicionar valores
    for i, v in enumerate(corrs_reviews):
        axes[1].text(v + 0.01, i, f'{v:.3f}',
                     va='center', ha='left', fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'correlation_bars.png'),
                dpi=300, bbox_inches='tight')
    print("✅ Gráficos de barras de correlações salvos!")
    plt.close()


def plot_descriptive_comparison(descriptive_stats, output_folder):
    """Gera gráficos comparando medianas entre PRs merged e não merged"""
    metrics = {
        'pr_size': 'Tamanho do PR\n(linhas)',
        'analysis_time_hours': 'Tempo de Análise\n(horas)',
        'description_length': 'Tamanho da Descrição\n(caracteres)',
        'interactions': 'Interações\n(comentários)',
        'num_reviews': 'Número de\nRevisões'
    }

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()

    for idx, (metric, label) in enumerate(metrics.items()):
        merged_median = descriptive_stats[metric]['merged']['median']
        not_merged_median = descriptive_stats[metric]['not_merged']['median']

        categories = ['Merged', 'Não Merged']
        values = [merged_median, not_merged_median]
        colors = ['#2ca02c', '#d62728']

        bars = axes[idx].bar(categories, values, color=colors,
                             alpha=0.7, edgecolor='black', linewidth=1.5)
        axes[idx].set_ylabel('Mediana', fontsize=11)
        axes[idx].set_title(label, fontsize=12, fontweight='bold')
        axes[idx].grid(axis='y', alpha=0.3)

        # Adicionar valores nas barras
        for bar in bars:
            height = bar.get_height()
            axes[idx].text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}',
                           ha='center', va='bottom', fontweight='bold', fontsize=10)

        # Adicionar diferença percentual
        if merged_median > 0:
            diff_pct = ((not_merged_median - merged_median) /
                        merged_median) * 100
            axes[idx].text(0.5, max(values) * 0.9,
                           f'Δ: {diff_pct:+.1f}%',
                           ha='center', transform=axes[idx].transData,
                           bbox=dict(boxstyle='round',
                                     facecolor='wheat', alpha=0.5),
                           fontsize=9)

    # Remover o último subplot (temos 5 métricas, 6 espaços)
    fig.delaxes(axes[5])

    plt.suptitle('Comparação de Medianas: PRs Merged vs Não Merged',
                 fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder,
                'descriptive_comparison.png'), dpi=300, bbox_inches='tight')
    print("✅ Gráfico de comparação de medianas salvo!")
    plt.close()


def plot_distributions(df, output_folder):
    """Gera gráficos de distribuição das variáveis principais"""
    metrics = {
        'pr_size': 'Tamanho do PR (linhas)',
        'analysis_time_hours': 'Tempo de Análise (horas)',
        'interactions': 'Interações (comentários)',
        'num_reviews': 'Número de Revisões'
    }

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for idx, (metric, label) in enumerate(metrics.items()):
        # Filtrar outliers extremos para melhor visualização (usando IQR)
        Q1 = df[metric].quantile(0.25)
        Q3 = df[metric].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 3 * IQR
        upper = Q3 + 3 * IQR

        df_filtered = df[(df[metric] >= lower) & (df[metric] <= upper)]

        merged = df_filtered[df_filtered['is_merged'] == 1][metric]
        not_merged = df_filtered[df_filtered['is_merged'] == 0][metric]

        # Violin plot
        parts = axes[idx].violinplot([merged, not_merged],
                                     positions=[1, 2],
                                     showmeans=True, showmedians=True,
                                     widths=0.7)

        # Colorir violinos
        colors = ['#2ca02c', '#d62728']
        for pc, color in zip(parts['bodies'], colors):
            pc.set_facecolor(color)
            pc.set_alpha(0.6)

        axes[idx].set_xticks([1, 2])
        axes[idx].set_xticklabels(['Merged', 'Não Merged'])
        axes[idx].set_ylabel(label, fontsize=11)
        axes[idx].set_title(
            f'Distribuição: {label}', fontsize=12, fontweight='bold')
        axes[idx].grid(axis='y', alpha=0.3)

        # Adicionar estatísticas
        stats_text = f'Merged: μ={merged.mean():.1f}, m={merged.median():.1f}\n'
        stats_text += f'Não Merged: μ={not_merged.mean():.1f}, m={not_merged.median():.1f}'
        axes[idx].text(0.02, 0.98, stats_text,
                       transform=axes[idx].transAxes,
                       verticalalignment='top',
                       bbox=dict(boxstyle='round',
                                 facecolor='wheat', alpha=0.5),
                       fontsize=8)

    plt.suptitle('Distribuições das Variáveis: PRs Merged vs Não Merged',
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'distributions.png'),
                dpi=300, bbox_inches='tight')
    print("✅ Gráfico de distribuições salvo!")
    plt.close()


def plot_scatter_top_correlations(df, output_folder):
    """Gera scatter plots das correlações mais fortes"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 1. Interações vs Número de Revisões (correlação mais forte)
    sample = df.sample(n=min(10000, len(df)), random_state=42)
    axes[0, 0].scatter(sample['interactions'], sample['num_reviews'],
                       alpha=0.3, s=10, c='#1f77b4')
    axes[0, 0].set_xlabel('Interações (comentários)', fontsize=11)
    axes[0, 0].set_ylabel('Número de Revisões', fontsize=11)
    axes[0, 0].set_title('Interações vs Revisões (ρ = 0.58)',
                         fontsize=12, fontweight='bold')
    axes[0, 0].grid(alpha=0.3)

    # 2. Tempo vs Revisões
    axes[0, 1].scatter(sample['analysis_time_hours'], sample['num_reviews'],
                       alpha=0.3, s=10, c='#ff7f0e')
    axes[0, 1].set_xlabel('Tempo de Análise (horas)', fontsize=11)
    axes[0, 1].set_ylabel('Número de Revisões', fontsize=11)
    axes[0, 1].set_title('Tempo vs Revisões (ρ = 0.35)',
                         fontsize=12, fontweight='bold')
    axes[0, 1].grid(alpha=0.3)
    axes[0, 1].set_xlim(0, sample['analysis_time_hours'].quantile(0.95))

    # 3. Tamanho vs Revisões
    axes[1, 0].scatter(sample['pr_size'], sample['num_reviews'],
                       alpha=0.3, s=10, c='#2ca02c')
    axes[1, 0].set_xlabel('Tamanho do PR (linhas)', fontsize=11)
    axes[1, 0].set_ylabel('Número de Revisões', fontsize=11)
    axes[1, 0].set_title('Tamanho vs Revisões (ρ = 0.34)',
                         fontsize=12, fontweight='bold')
    axes[1, 0].grid(alpha=0.3)
    axes[1, 0].set_xlim(0, sample['pr_size'].quantile(0.95))

    # 4. Tempo vs Status (merged)
    merged = sample[sample['is_merged'] == 1]['analysis_time_hours']
    not_merged = sample[sample['is_merged'] == 0]['analysis_time_hours']

    axes[1, 1].hist([merged, not_merged], bins=50, alpha=0.6,
                    label=['Merged', 'Não Merged'],
                    color=['#2ca02c', '#d62728'])
    axes[1, 1].set_xlabel('Tempo de Análise (horas)', fontsize=11)
    axes[1, 1].set_ylabel('Frequência', fontsize=11)
    axes[1, 1].set_title('Tempo vs Status (ρ = -0.26)',
                         fontsize=12, fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.3)
    axes[1, 1].set_xlim(0, 500)

    plt.suptitle('Scatter Plots das Principais Correlações',
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'scatter_correlations.png'),
                dpi=300, bbox_inches='tight')
    print("✅ Scatter plots salvos!")
    plt.close()


def plot_summary_dashboard(correlations, descriptive_stats, output_folder):
    """Gera um dashboard resumido com as principais descobertas"""
    fig = plt.figure(figsize=(18, 10))
    gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

    # 1. Top correlações positivas
    ax1 = fig.add_subplot(gs[0, 0])
    top_pos = [
        ('Interações →\nRevisões', 0.5842),
        ('Tempo →\nRevisões', 0.3509),
        ('Tamanho →\nRevisões', 0.3419)
    ]
    labels, values = zip(*top_pos)
    bars = ax1.barh(labels, values, color='#2ca02c',
                    alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Correlação (ρ)', fontsize=10)
    ax1.set_title('Top 3 Correlações Positivas',
                  fontsize=11, fontweight='bold')
    ax1.set_xlim(0, 0.7)
    for bar in bars:
        width = bar.get_width()
        ax1.text(width + 0.01, bar.get_y() + bar.get_height()/2,
                 f'{width:.3f}', va='center', fontweight='bold', fontsize=9)

    # 2. Top correlações negativas
    ax2 = fig.add_subplot(gs[0, 1])
    top_neg = [
        ('Tempo →\nStatus', -0.2571),
        ('Interações →\nStatus', -0.2453),
        ('Descrição →\nStatus', -0.0210)
    ]
    labels, values = zip(*top_neg)
    bars = ax2.barh(labels, values, color='#d62728',
                    alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Correlação (ρ)', fontsize=10)
    ax2.set_title('Top 3 Correlações Negativas',
                  fontsize=11, fontweight='bold')
    ax2.set_xlim(-0.3, 0)
    for bar in bars:
        width = bar.get_width()
        ax2.text(width - 0.01, bar.get_y() + bar.get_height()/2,
                 f'{width:.3f}', va='center', ha='right', fontweight='bold', fontsize=9)

    # 3. Diferenças mais significativas (medianas)
    ax3 = fig.add_subplot(gs[0, 2])
    time_diff = ((descriptive_stats['analysis_time_hours']['not_merged']['median'] -
                  descriptive_stats['analysis_time_hours']['merged']['median']) /
                 descriptive_stats['analysis_time_hours']['merged']['median'] * 100)
    int_diff = ((descriptive_stats['interactions']['not_merged']['median'] -
                 descriptive_stats['interactions']['merged']['median']) /
                descriptive_stats['interactions']['merged']['median'] * 100)
    size_diff = ((descriptive_stats['pr_size']['not_merged']['median'] -
                  descriptive_stats['pr_size']['merged']['median']) /
                 descriptive_stats['pr_size']['merged']['median'] * 100)

    diffs = [('Tempo', time_diff), ('Interações',
                                    int_diff), ('Tamanho', size_diff)]
    labels, values = zip(*diffs)
    colors = ['#d62728' if v > 0 else '#2ca02c' for v in values]
    bars = ax3.bar(labels, values, color=colors, alpha=0.7, edgecolor='black')
    ax3.set_ylabel('Diferença %\n(Não Merged vs Merged)', fontsize=10)
    ax3.set_title('Maiores Diferenças nas Medianas',
                  fontsize=11, fontweight='bold')
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax3.grid(axis='y', alpha=0.3)
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2, height + (5 if height > 0 else -5),
                 f'{height:.0f}%', ha='center', va='bottom' if height > 0 else 'top',
                 fontweight='bold', fontsize=9)

    # 4-5. Comparação de medianas (principais métricas)
    ax4 = fig.add_subplot(gs[1, :2])
    metrics_labels = ['Tamanho\n(linhas)', 'Tempo\n(horas)', 'Descrição\n(chars)',
                      'Interações', 'Revisões']
    merged_values = [
        descriptive_stats['pr_size']['merged']['median'],
        descriptive_stats['analysis_time_hours']['merged']['median'],
        descriptive_stats['description_length']['merged']['median'],
        descriptive_stats['interactions']['merged']['median'],
        descriptive_stats['num_reviews']['merged']['median']
    ]
    not_merged_values = [
        descriptive_stats['pr_size']['not_merged']['median'],
        descriptive_stats['analysis_time_hours']['not_merged']['median'],
        descriptive_stats['description_length']['not_merged']['median'],
        descriptive_stats['interactions']['not_merged']['median'],
        descriptive_stats['num_reviews']['not_merged']['median']
    ]

    x = np.arange(len(metrics_labels))
    width = 0.35
    bars1 = ax4.bar(x - width/2, merged_values, width, label='Merged',
                    color='#2ca02c', alpha=0.7, edgecolor='black')
    bars2 = ax4.bar(x + width/2, not_merged_values, width, label='Não Merged',
                    color='#d62728', alpha=0.7, edgecolor='black')

    ax4.set_ylabel('Valor (Mediana)', fontsize=11)
    ax4.set_title('Comparação de Medianas: Merged vs Não Merged',
                  fontsize=12, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(metrics_labels)
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)

    # 6. Estatísticas gerais
    ax5 = fig.add_subplot(gs[1, 2])
    ax5.axis('off')

    total_prs = descriptive_stats['pr_size']['overall']['count']
    merged_count = descriptive_stats['pr_size']['merged']['count']
    not_merged_count = descriptive_stats['pr_size']['not_merged']['count']
    merge_rate = (merged_count / total_prs) * 100

    stats_text = f"""
    📊 ESTATÍSTICAS GERAIS
    
    Total de PRs: {total_prs:,}
    
    PRs Merged: {merged_count:,}
    PRs Não Merged: {not_merged_count:,}
    
    Taxa de Merge: {merge_rate:.1f}%
    
    ---
    
    🔍 PRINCIPAIS DESCOBERTAS
    
    • Tamanho do PR não afeta
      significativamente o merge
      (ρ ≈ 0.01)
    
    • Tempo é o melhor preditor
      de rejeição (ρ = -0.26)
    
    • Interações predizem
      fortemente revisões
      (ρ = 0.58)
    """

    ax5.text(0.1, 0.95, stats_text, transform=ax5.transAxes,
             fontsize=10, verticalalignment='top', family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # 7-8. Interpretação das correlações
    ax6 = fig.add_subplot(gs[2, :])
    ax6.axis('off')

    interpretation = """
    💡 INTERPRETAÇÃO DAS CORRELAÇÕES (Teste de Spearman)
    
    GRUPO 1 - FATORES QUE INFLUENCIAM O STATUS (MERGE):
    • Tempo de Análise (ρ = -0.26): Correlação NEGATIVA moderada → PRs que demoram mais tendem a ser REJEITADOS
    • Interações (ρ = -0.25): Correlação NEGATIVA moderada → Mais comentários indicam PROBLEMAS a resolver
    • Tamanho do PR (ρ = 0.01): Correlação INEXISTENTE → Tamanho NÃO afeta aprovação (contraria senso comum!)
    • Descrição (ρ = -0.02): Correlação INEXISTENTE → Descrições longas NÃO garantem aprovação
    
    GRUPO 2 - FATORES QUE INFLUENCIAM O NÚMERO DE REVISÕES:
    • Interações (ρ = 0.58): Correlação POSITIVA FORTE → Mais discussões levam a MAIS revisões (ciclo iterativo)
    • Tempo (ρ = 0.35): Correlação POSITIVA moderada → Processos longos acumulam mais revisões
    • Tamanho (ρ = 0.34): Correlação POSITIVA moderada → PRs maiores exigem mais escrutínio
    • Descrição (ρ = 0.13): Correlação POSITIVA fraca → Descrições longas têm impacto limitado
    """

    ax6.text(0.05, 0.95, interpretation, transform=ax6.transAxes,
             fontsize=9.5, verticalalignment='top', family='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

    plt.suptitle('📊 DASHBOARD DE ANÁLISE: Code Review no GitHub (n=947.735 PRs)',
                 fontsize=16, fontweight='bold', y=0.98)

    plt.savefig(os.path.join(output_folder, 'summary_dashboard.png'),
                dpi=300, bbox_inches='tight')
    print("✅ Dashboard resumido salvo!")
    plt.close()


def main():
    print("📊 Gerando visualizações das análises estatísticas...\n")

    # Carregar dados
    print("📁 Carregando dados...")
    df, correlations, descriptive_stats = load_data()

    # Criar pasta para gráficos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    charts_folder = os.path.join(script_dir, '..', 'docs', 'charts')
    os.makedirs(charts_folder, exist_ok=True)

    print(f"📂 Gráficos serão salvos em: {charts_folder}\n")

    # Gerar gráficos
    print("🎨 Gerando gráficos...\n")

    plot_correlation_heatmap(correlations, charts_folder)
    plot_correlation_bars(correlations, charts_folder)
    plot_descriptive_comparison(descriptive_stats, charts_folder)
    plot_distributions(df, charts_folder)
    plot_scatter_top_correlations(df, charts_folder)
    plot_summary_dashboard(correlations, descriptive_stats, charts_folder)

    print("\n" + "="*80)
    print("✅ TODOS OS GRÁFICOS FORAM GERADOS COM SUCESSO!")
    print("="*80)
    print(f"\n📁 Localização: {charts_folder}")
    print("\n📊 Gráficos gerados:")
    print("   1. correlation_heatmap.png - Heatmap de todas as correlações")
    print("   2. correlation_bars.png - Barras comparando correlações por grupo")
    print("   3. descriptive_comparison.png - Comparação de medianas")
    print("   4. distributions.png - Distribuições das variáveis")
    print("   5. scatter_correlations.png - Scatter plots das principais correlações")
    print("   6. summary_dashboard.png - Dashboard resumido com todas as descobertas")
    print("\n🎉 Pronto para incluir no relatório!")


if __name__ == '__main__':
    main()
