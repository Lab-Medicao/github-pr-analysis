import os
import pandas as pd
from glob import glob


def summarize_csvs(input_folder, output_file):
    csv_files = glob(os.path.join(input_folder, '*.csv'))
    summary_rows = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        for col in df.select_dtypes(include='number').columns:
            data = df[col].dropna()
            if len(data) == 0:
                continue
            row = {
                'file': os.path.basename(csv_file),
                'column': col,
                'count': len(data),
                'mean': data.mean(),
                'median': data.median(),
                'mode': data.mode().iloc[0] if not data.mode().empty else None,
                'min': data.min(),
                'max': data.max(),
                'variance': data.var(),
                'std_dev': data.std()
            }
            summary_rows.append(row)
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(output_file, index=False)


if __name__ == '__main__':
    input_folder = os.path.join(os.path.dirname(__file__), 'datasets')
    output_file = os.path.join(os.path.dirname(__file__), 'summary.csv')
    summarize_csvs(input_folder, output_file)
