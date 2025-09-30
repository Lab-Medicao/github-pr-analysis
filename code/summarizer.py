import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
from statistics import mode, multimode
import warnings

warnings.filterwarnings('ignore')

def calculate_statistics(data_series, column_name):
    """
    Calcula estatísticas descritivas para uma série de dados.
    
    Args:
        data_series: pandas Series com os dados
        column_name: nome da coluna para identificação
    
    Returns:
        dict: dicionário com as estatísticas calculadas
    """
    if data_series.empty or data_series.isna().all():
        return {
            f'{column_name}_median': np.nan,
            f'{column_name}_mean': np.nan,
            f'{column_name}_mode': np.nan,
            f'{column_name}_min': np.nan,
            f'{column_name}_max': np.nan,
            f'{column_name}_variance': np.nan,
            f'{column_name}_std': np.nan
        }
    

    clean_data = data_series.dropna()
    
    if clean_data.empty:
        return {
            f'{column_name}_median': np.nan,
            f'{column_name}_mean': np.nan,
            f'{column_name}_mode': np.nan,
            f'{column_name}_min': np.nan,
            f'{column_name}_max': np.nan,
            f'{column_name}_variance': np.nan,
            f'{column_name}_std': np.nan
        }
    

    try:
    
        try:
            mode_value = mode(clean_data)
        except:
        
            modes = multimode(clean_data)
            mode_value = modes[0] if modes else np.nan
    except:
    
        pandas_mode = clean_data.mode()
        mode_value = pandas_mode.iloc[0] if not pandas_mode.empty else np.nan
    
    return {
        f'{column_name}_median': clean_data.median(),
        f'{column_name}_mean': clean_data.mean(),
        f'{column_name}_mode': mode_value,
        f'{column_name}_min': clean_data.min(),
        f'{column_name}_max': clean_data.max(),
        f'{column_name}_variance': clean_data.var(),
        f'{column_name}_std': clean_data.std()
    }

def extract_repo_name(filename):
    """
    Extrai o nome do repositório do nome do arquivo CSV.
    
    Args:
        filename: nome do arquivo (ex: 'facebook_react.csv')
    
    Returns:
        str: nome do repositório (ex: 'facebook/react')
    """
    base_name = Path(filename).stem
    if '_' in base_name:
        parts = base_name.split('_', 1)
        return f"{parts[0]}/{parts[1]}"
    return base_name

def process_csv_files(datasets_dir):
    """
    Processa todos os arquivos CSV no diretório datasets.
    
    Args:
        datasets_dir: caminho para o diretório com os CSVs
    
    Returns:
        list: lista de dicionários com estatísticas para cada repositório
    """
    csv_files = glob.glob(os.path.join(datasets_dir, "*.csv"))
    results = []
    
    print(f"Encontrados {len(csv_files)} arquivos CSV para processar...")
    
    for i, csv_file in enumerate(csv_files, 1):
        filename = os.path.basename(csv_file)
        repo_name = extract_repo_name(filename)
        
        print(f"Processando {i}/{len(csv_files)}: {repo_name}")
        
        try:
        
            df = pd.read_csv(csv_file)
            
        
            required_columns = ['reviewsCount', 'hoursOpen']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"  ⚠️  Colunas faltando em {filename}: {missing_columns}")
                continue
            
        
            df['reviewsCount'] = pd.to_numeric(df['reviewsCount'], errors='coerce')
            df['hoursOpen'] = pd.to_numeric(df['hoursOpen'], errors='coerce')
            
        
            stats = {'repository': repo_name, 'total_prs': len(df)}
            
            stats.update(calculate_statistics(df['reviewsCount'], 'reviews'))
            stats.update(calculate_statistics(df['hoursOpen'], 'hours_open'))
            
            results.append(stats)
            
        except Exception as e:
            print(f"  ❌ Erro ao processar {filename}: {str(e)}")
            continue
    
    return results

def main():
    """Função principal do script."""

    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(script_dir, "datasets")
    output_file = os.path.join(script_dir, "results/summary_results.csv")
    
    print("🔍 Iniciando sumarização dos dados de PRs...")
    print(f"📁 Diretório de datasets: {datasets_dir}")
    
    if not os.path.exists(datasets_dir):
        print(f"❌ Diretório {datasets_dir} não encontrado!")
        return
    

    results = process_csv_files(datasets_dir)
    
    if not results:
        print("❌ Nenhum resultado foi processado com sucesso!")
        return
    

    summary_df = pd.DataFrame(results)
    

    column_order = ['repository', 'total_prs']
    

    reviews_columns = [col for col in summary_df.columns if col.startswith('reviews_')]
    column_order.extend(sorted(reviews_columns))
    

    hours_columns = [col for col in summary_df.columns if col.startswith('hours_open_')]
    column_order.extend(sorted(hours_columns))
    

    summary_df = summary_df[column_order]
    

    summary_df.to_csv(output_file, index=False, float_format='%.2f')
    
    print(f"\n✅ Sumarização concluída!")
    print(f"📊 {len(results)} repositórios processados")
    print(f"💾 Resultado salvo em: {output_file}")
    

    print(f"\n📈 Estatísticas gerais:")
    print(f"   Total de PRs analisados: {summary_df['total_prs'].sum():,}")
    print(f"   Média de PRs por repositório: {summary_df['total_prs'].mean():.1f}")
    print(f"   Mediana de reviews por PR (geral): {summary_df['reviews_median'].median():.2f}")
    print(f"   Mediana de horas abertas por PR (geral): {summary_df['hours_open_median'].median():.2f}")
    

    print(f"\n🔍 Primeiras 5 linhas do resultado:")
    print(summary_df.head().to_string(index=False))

if __name__ == "__main__":
    main()