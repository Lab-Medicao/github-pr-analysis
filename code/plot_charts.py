import argparse
import os
from typing import List, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_summary(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # Normalize expected numeric columns (best-effort if present)
    for col in [
        "total_prs",
        "reviews_mean",
        "reviews_median",
        "reviews_mode",
        "reviews_min",
        "reviews_max",
        "reviews_std",
        "reviews_variance",
        "hours_open_mean",
        "hours_open_median",
        "hours_open_mode",
        "hours_open_min",
        "hours_open_max",
        "hours_open_std",
        "hours_open_variance",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def pearsonr_safe(x: pd.Series, y: pd.Series) -> float:
    x = pd.to_numeric(x, errors="coerce")
    y = pd.to_numeric(y, errors="coerce")
    mask = x.notna() & y.notna()
    if mask.sum() < 3:
        return np.nan
    return float(np.corrcoef(x[mask], y[mask])[0, 1])


def scatter_with_trend(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    subtitle: str,
    xlabel: str,
    ylabel: str,
    out_path: str,
    color_by: str = "total_prs",
    cmap: str = "viridis",
) -> None:
    plt.figure(figsize=(10, 7))
    plot_df = df[[x_col, y_col, "repository"] + ([color_by] if color_by in df.columns else [])].dropna()
    if plot_df.empty:
        _placeholder_chart(
            f"{title}\n{subtitle}",
            "Dados insuficientes para traçar este gráfico.",
            out_path,
        )
        return

    sizes = None
    colors = None
    if color_by in plot_df.columns:
        colors = plot_df[color_by]
        # Normalize sizes to make dots easier to see
        sizes = 50 + 150 * (plot_df[color_by] - plot_df[color_by].min()) / (
            (plot_df[color_by].max() - plot_df[color_by].min() + 1e-9)
        )

    sc = plt.scatter(
        plot_df[x_col],
        plot_df[y_col],
        c=colors,
        s=sizes if sizes is not None else 60,
        cmap=cmap,
        edgecolor="black",
        alpha=0.8,
        linewidths=0.5,
    )

    # Trendline (linear)
    r = pearsonr_safe(plot_df[x_col], plot_df[y_col])
    try:
        z = np.polyfit(plot_df[x_col], plot_df[y_col], 1)
        p = np.poly1d(z)
        xs = np.linspace(plot_df[x_col].min(), plot_df[x_col].max(), 100)
        plt.plot(xs, p(xs), color="#D62728", linewidth=2, label=f"Tendência (linear)")
    except Exception:
        pass

    plt.title(title, fontsize=13, fontweight="bold")
    plt.suptitle(subtitle, fontsize=10, y=0.94)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if color_by in plot_df.columns:
        cbar = plt.colorbar(sc)
        cbar.set_label(color_by)

    legend_extra = f"Pearson r = {r:.2f}" if not np.isnan(r) else "Pearson r = n/d"
    plt.legend(title=legend_extra, loc="best")
    plt.grid(True, alpha=0.2)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(out_path, dpi=160)
    plt.close()


def correlation_heatmap(
    df: pd.DataFrame, cols: List[str], title: str, subtitle: str, out_path: str
) -> None:
    use_cols = [c for c in cols if c in df.columns]
    if len(use_cols) < 2:
        _placeholder_chart(
            f"{title}\n{subtitle}",
            "Dados insuficientes para matriz de correlação.",
            out_path,
        )
        return
    corr = df[use_cols].corr(method="pearson")

    plt.figure(figsize=(10, 8))
    im = plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    plt.colorbar(im, fraction=0.046, pad=0.04)
    plt.xticks(range(len(use_cols)), use_cols, rotation=45, ha="right")
    plt.yticks(range(len(use_cols)), use_cols)
    for i in range(len(use_cols)):
        for j in range(len(use_cols)):
            plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", color="black")
    plt.title(title, fontsize=13, fontweight="bold")
    plt.suptitle(subtitle, fontsize=10, y=0.94)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(out_path, dpi=160)
    plt.close()


def bar_top(df: pd.DataFrame, col: str, title: str, subtitle: str, out_path: str, top_n: int = 25) -> None:
    plot_df = df[["repository", col]].dropna().sort_values(col, ascending=False).head(top_n)
    if plot_df.empty:
        _placeholder_chart(f"{title}\n{subtitle}", "Dados indisponíveis.", out_path)
        return

    plt.figure(figsize=(12, max(6, int(top_n * 0.35))))
    bars = plt.barh(plot_df["repository"], plot_df[col], color=plt.cm.tab20(np.linspace(0, 1, len(plot_df))))
    plt.gca().invert_yaxis()
    plt.title(title, fontsize=13, fontweight="bold")
    plt.suptitle(subtitle, fontsize=10, y=0.94)
    plt.xlabel(col)
    plt.ylabel("Repositório")
    # Annotate values
    for b in bars:
        w = b.get_width()
        plt.text(w, b.get_y() + b.get_height() / 2, f" {w:.2f}", va="center")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(out_path, dpi=160)
    plt.close()


def histogram(df: pd.DataFrame, col: str, bins: int, title: str, subtitle: str, out_path: str) -> None:
    series = pd.to_numeric(df[col], errors="coerce") if col in df.columns else pd.Series(dtype=float)
    series = series.dropna()
    if series.empty:
        _placeholder_chart(f"{title}\n{subtitle}", "Sem dados para histograma.", out_path)
        return
    plt.figure(figsize=(9, 6))
    plt.hist(series, bins=bins, color="#1f77b4", alpha=0.8, edgecolor="white")
    plt.title(title, fontsize=13, fontweight="bold")
    plt.suptitle(subtitle, fontsize=10, y=0.94)
    plt.xlabel(col)
    plt.ylabel("Frequência")
    plt.grid(True, alpha=0.2)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(out_path, dpi=160)
    plt.close()


def _placeholder_chart(title: str, message: str, out_path: str) -> None:
    plt.figure(figsize=(9, 5))
    plt.title(title, fontsize=13, fontweight="bold")
    plt.text(0.5, 0.5, message, ha="center", va="center", fontsize=12)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def generate_rq_charts(df: pd.DataFrame, out_dir: str) -> List[Tuple[str, str]]:
    """
    Generate charts for each Research Question (RQ01..RQ08). Returns list of (rq, path).
    Notes on available data:
    - This summary contains review statistics and time-open statistics at repository level only.
    - We currently don't have PR 'size', 'description richness', or 'interaction counts' columns.
      When these columns are later added (e.g., pr_size_mean, desc_len_mean, interactions_mean),
      this function will automatically plot them.
    """
    outputs = []

    # Define proxies/columns
    has_time = "hours_open_mean" in df.columns
    has_reviews = "reviews_mean" in df.columns
    has_pr_size = "pr_size_mean" in df.columns
    has_desc = "desc_len_mean" in df.columns
    has_inter = "interactions_mean" in df.columns
    has_feedback_rate = "approved_rate" in df.columns or "merge_rate" in df.columns
    feedback_label = "approved_rate" if "approved_rate" in df.columns else ("merge_rate" if "merge_rate" in df.columns else None)

    # RQ01 – Tamanho do PR vs feedback final
    if has_pr_size and has_feedback_rate:
        p = os.path.join(out_dir, "RQ01_pr_size_vs_feedback.png")
        scatter_with_trend(
            df,
            x_col="pr_size_mean",
            y_col=feedback_label,
            title="RQ01: Tamanho do PR vs Feedback das revisões",
            subtitle=f"Proxy de feedback final: {feedback_label} (taxa por repositório)",
            xlabel="Tamanho médio do PR (linhas/arquivos)",
            ylabel="Feedback final (taxa)",
            out_path=p,
        )
    else:
        p = os.path.join(out_dir, "RQ01_pr_size_vs_feedback.png")
        _placeholder_chart(
            "RQ01: Tamanho do PR vs Feedback das revisões",
            "Colunas necessárias ausentes (esperado: pr_size_mean e approved_rate|merge_rate)",
            p,
        )
    outputs.append(("RQ01", p))

    # RQ02 – Tempo de Análise vs feedback final
    if has_time and has_feedback_rate:
        p = os.path.join(out_dir, "RQ02_time_vs_feedback.png")
        scatter_with_trend(
            df,
            x_col="hours_open_mean",
            y_col=feedback_label,
            title="RQ02: Tempo de análise vs Feedback das revisões",
            subtitle=f"Proxy de feedback final: {feedback_label} (taxa por repositório)",
            xlabel="Tempo de análise (horas abertas - média)",
            ylabel="Feedback final (taxa)",
            out_path=p,
        )
    else:
        p = os.path.join(out_dir, "RQ02_time_vs_feedback.png")
        _placeholder_chart(
            "RQ02: Tempo de análise vs Feedback das revisões",
            "Colunas necessárias ausentes (esperado: hours_open_mean e approved_rate|merge_rate)",
            p,
        )
    outputs.append(("RQ02", p))

    # RQ03 – Descrição do PR vs feedback final
    if has_desc and has_feedback_rate:
        p = os.path.join(out_dir, "RQ03_desc_vs_feedback.png")
        scatter_with_trend(
            df,
            x_col="desc_len_mean",
            y_col=feedback_label,
            title="RQ03: Descrição do PR vs Feedback das revisões",
            subtitle=f"Proxy de feedback final: {feedback_label} (taxa por repositório)",
            xlabel="Descrição (tamanho médio)",
            ylabel="Feedback final (taxa)",
            out_path=p,
        )
    else:
        p = os.path.join(out_dir, "RQ03_desc_vs_feedback.png")
        _placeholder_chart(
            "RQ03: Descrição do PR vs Feedback das revisões",
            "Colunas necessárias ausentes (esperado: desc_len_mean e approved_rate|merge_rate)",
            p,
        )
    outputs.append(("RQ03", p))

    # RQ04 – Interações no PR vs feedback final
    if has_inter and has_feedback_rate:
        p = os.path.join(out_dir, "RQ04_interactions_vs_feedback.png")
        scatter_with_trend(
            df,
            x_col="interactions_mean",
            y_col=feedback_label,
            title="RQ04: Interações no PR vs Feedback das revisões",
            subtitle=f"Proxy de feedback final: {feedback_label} (taxa por repositório)",
            xlabel="Interações (média)",
            ylabel="Feedback final (taxa)",
            out_path=p,
        )
    else:
        p = os.path.join(out_dir, "RQ04_interactions_vs_feedback.png")
        _placeholder_chart(
            "RQ04: Interações no PR vs Feedback das revisões",
            "Colunas necessárias ausentes (esperado: interactions_mean e approved_rate|merge_rate)",
            p,
        )
    outputs.append(("RQ04", p))

    # RQ05 – Tamanho do PR vs número de revisões
    if "pr_size_mean" in df.columns and has_reviews:
        p = os.path.join(out_dir, "RQ05_pr_size_vs_num_reviews.png")
        scatter_with_trend(
            df,
            x_col="pr_size_mean",
            y_col="reviews_mean",
            title="RQ05: Tamanho do PR vs Número de revisões",
            subtitle="Número de revisões (proxy: média) vs tamanho médio do PR",
            xlabel="Tamanho médio do PR",
            ylabel="Número de revisões (média)",
            out_path=p,
        )
    else:
        p = os.path.join(out_dir, "RQ05_pr_size_vs_num_reviews.png")
        _placeholder_chart(
            "RQ05: Tamanho do PR vs Número de revisões",
            "Colunas necessárias ausentes (esperado: pr_size_mean e reviews_mean)",
            p,
        )
    outputs.append(("RQ05", p))

    # RQ06 – Tempo de análise vs número de revisões
    if has_time and has_reviews:
        p = os.path.join(out_dir, "RQ06_time_vs_num_reviews.png")
        scatter_with_trend(
            df,
            x_col="hours_open_mean",
            y_col="reviews_mean",
            title="RQ06: Tempo de análise vs Número de revisões",
            subtitle="Número de revisões (proxy: média) vs tempo de análise (média)",
            xlabel="Tempo de análise (horas abertas - média)",
            ylabel="Número de revisões (média)",
            out_path=p,
        )
    else:
        p = os.path.join(out_dir, "RQ06_time_vs_num_reviews.png")
        _placeholder_chart(
            "RQ06: Tempo de análise vs Número de revisões",
            "Colunas necessárias ausentes (esperado: hours_open_mean e reviews_mean)",
            p,
        )
    outputs.append(("RQ06", p))

    # RQ07 – Descrição do PR vs número de revisões
    if "desc_len_mean" in df.columns and has_reviews:
        p = os.path.join(out_dir, "RQ07_desc_vs_num_reviews.png")
        scatter_with_trend(
            df,
            x_col="desc_len_mean",
            y_col="reviews_mean",
            title="RQ07: Descrição do PR vs Número de revisões",
            subtitle="Número de revisões (proxy: média) vs tamanho médio da descrição",
            xlabel="Descrição (tamanho médio)",
            ylabel="Número de revisões (média)",
            out_path=p,
        )
    else:
        p = os.path.join(out_dir, "RQ07_desc_vs_num_reviews.png")
        _placeholder_chart(
            "RQ07: Descrição do PR vs Número de revisões",
            "Colunas necessárias ausentes (esperado: desc_len_mean e reviews_mean)",
            p,
        )
    outputs.append(("RQ07", p))

    # RQ08 – Interações vs número de revisões
    if "interactions_mean" in df.columns and has_reviews:
        p = os.path.join(out_dir, "RQ08_interactions_vs_num_reviews.png")
        scatter_with_trend(
            df,
            x_col="interactions_mean",
            y_col="reviews_mean",
            title="RQ08: Interações no PR vs Número de revisões",
            subtitle="Número de revisões (proxy: média) vs interações médias",
            xlabel="Interações (média)",
            ylabel="Número de revisões (média)",
            out_path=p,
        )
    else:
        p = os.path.join(out_dir, "RQ08_interactions_vs_num_reviews.png")
        _placeholder_chart(
            "RQ08: Interações no PR vs Número de revisões",
            "Colunas necessárias ausentes (esperado: interactions_mean e reviews_mean)",
            p,
        )
    outputs.append(("RQ08", p))

    return outputs


def generate_additional_charts(df: pd.DataFrame, out_dir: str, top_n: int) -> List[Tuple[str, str]]:
    outputs = []
    # Correlation heatmap among available summary columns
    corr_cols = [
        "total_prs",
        "reviews_mean",
        "reviews_median",
        "reviews_max",
        "hours_open_mean",
        "hours_open_median",
        "hours_open_max",
    ]
    # Add feedback proxies if available
    if "approved_rate" in df.columns:
        corr_cols.append("approved_rate")
    if "merge_rate" in df.columns:
        corr_cols.append("merge_rate")
    p = os.path.join(out_dir, "correlation_heatmap.png")
    correlation_heatmap(
        df,
        corr_cols,
        title="Matriz de correlação (métricas sumarizadas)",
        subtitle="Correlação de Pearson entre estatísticas de reviews e tempo em aberto",
        out_path=p,
    )
    outputs.append(("heatmap", p))

    # Bars for top repositories by total PRs
    p = os.path.join(out_dir, "top_repositories_by_total_prs.png")
    bar_top(
        df,
        col="total_prs",
        title="Top repositórios por total de PRs",
        subtitle=f"Top {top_n} repositórios com mais PRs analisados",
        out_path=p,
        top_n=top_n,
    )
    outputs.append(("bars_total_prs", p))

    # Bars for highest reviews_mean
    if "reviews_mean" in df.columns:
        p = os.path.join(out_dir, "top_repositories_by_reviews_mean.png")
        bar_top(
            df,
            col="reviews_mean",
            title="Top repositórios por média de reviews",
            subtitle=f"Top {top_n} repositórios com maior média de reviews por PR",
            out_path=p,
            top_n=top_n,
        )
        outputs.append(("bars_reviews_mean", p))

    # Bars for highest hours_open_mean
    if "hours_open_mean" in df.columns:
        p = os.path.join(out_dir, "top_repositories_by_hours_open_mean.png")
        bar_top(
            df,
            col="hours_open_mean",
            title="Top repositórios por tempo de análise (média de horas abertas)",
            subtitle=f"Top {top_n} repositórios com maior tempo médio de análise",
            out_path=p,
            top_n=top_n,
        )
        outputs.append(("bars_hours_open_mean", p))

    # Histograms to visualize distributions
    if "reviews_mean" in df.columns:
        p = os.path.join(out_dir, "hist_reviews_mean.png")
        histogram(
            df,
            col="reviews_mean",
            bins=30,
            title="Distribuição da média de reviews por repositório",
            subtitle="Visualização da dispersão das médias de reviews",
            out_path=p,
        )
        outputs.append(("hist_reviews_mean", p))

    if "hours_open_mean" in df.columns:
        p = os.path.join(out_dir, "hist_hours_open_mean.png")
        histogram(
            df,
            col="hours_open_mean",
            bins=30,
            title="Distribuição do tempo médio de análise (horas abertas)",
            subtitle="Visualização da dispersão do tempo médio de análise por repositório",
            out_path=p,
        )
        outputs.append(("hist_hours_open_mean", p))

    return outputs


def main():
    parser = argparse.ArgumentParser(description="Gerador de gráficos para análise de PRs (sumário de repositórios)")
    parser.add_argument("--csv", required=True, help="Caminho para o CSV de resultados sumarizados")
    parser.add_argument("--out", required=True, help="Diretório de saída para os gráficos")
    parser.add_argument("--top", type=int, default=25, help="Top N repositórios para alguns gráficos")
    args = parser.parse_args()

    ensure_dir(args.out)

    print(f"📥 Lendo sumário: {args.csv}")
    df = load_summary(args.csv)
    print(f"   Linhas: {len(df)} | Colunas: {list(df.columns)}")

    # Keep a top-N slice for readability on some charts, but use full DF when needed
    top_df = df.sort_values("total_prs", ascending=False).head(args.top) if "total_prs" in df.columns else df.copy()
    # Add the repository name explicitly (already present in CSV)
    if "repository" not in top_df.columns and "repository" in df.columns:
        top_df["repository"] = df["repository"]

    print("📈 Gerando gráficos das questões de pesquisa (RQ01..RQ08)...")
    rq_outputs = generate_rq_charts(top_df, args.out)
    for rq, path in rq_outputs:
        print(f"   {rq} -> {path}")

    print("📊 Gerando gráficos adicionais (correlação, distribuições, rankings)...")
    add_outputs = generate_additional_charts(top_df, args.out, args.top)
    for kind, path in add_outputs:
        print(f"   {kind} -> {path}")

    print("✅ Concluído. Gráficos salvos em:", args.out)


if __name__ == "__main__":
    main()
