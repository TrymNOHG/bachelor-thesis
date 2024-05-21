import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import numpy as np

def extract_interval(filename):
    match = re.search(r'_interval_(\d+)_', filename)
    if match:
        return int(match.group(1))
    return 0

def load_data(directory):
    data_frames = []
    sorted_files = sorted(os.listdir(directory), key=extract_interval, reverse=False)
    for filename in sorted_files:
        if filename.endswith('.csv'):
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath, header=None, names=['Metric', 'Value'])
            df['Model Name'] = df.loc[df['Metric'] == 'Model name', 'Value'].iloc[0]
            df = df.pivot(index='Model Name', columns='Metric', values='Value').reset_index()
            data_frames.append(df)
    return pd.concat(data_frames, ignore_index=True)

def plot_metrics(data, x_metric, y_metric, title=None, axis_abs_low=False, axis_abs_high=False):
    plt.figure(figsize=(14, 8))
    for _, row in data.iterrows():
        model_name = "Node 4144: `" + row['Model Name'].split("_")[3] + "s`"
        x = pd.to_numeric(row[x_metric], errors='coerce')
        y = pd.to_numeric(row[y_metric], errors='coerce')
        plt.scatter(x, y, label=model_name, s=200)
    
    if axis_abs_low:
        plt.ylim(bottom=0)
        plt.xlim(left=0)
    if axis_abs_high:
        plt.ylim(top=1)
        plt.xlim(right=1)
    
    plt.xlabel(x_metric, fontsize=18)
    plt.ylabel(y_metric, fontsize=18)
    if title is None:
        title = f'{x_metric} vs {y_metric}'
    plt.title(title, fontsize=24)
    plt.grid(True)

    plt.legend(title="Model Names", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f'interval_data_plots/{title}.png')


def plot_bar(data, metric, title=None):
    plt.figure(figsize=(14, 8))
    if metric in data.columns:
        metric_data = data[['Model Name', metric]]
        metric_data = metric_data.dropna(subset=[metric])
        metric_data[metric] = pd.to_numeric(metric_data[metric], errors='coerce')
        
        metric_data['Formatted Model Name'] = metric_data['Model Name'].apply(lambda x: "Node 4144: `" + x.split("_")[3] + "s`" if len(x.split("_")) > 3 else x)

        grouped_data = metric_data.groupby('Formatted Model Name')[metric].mean()

        grouped_data = grouped_data.sort_values(ascending=False)

        colors = plt.cm.viridis(np.linspace(0, 1, len(grouped_data)))

        grouped_data.plot(kind='bar', color=colors, edgecolor='black')
        
        plt.title(title if title else f'Bar Plot of {metric} by Model')
        plt.xlabel('Model Name')
        plt.ylabel(metric)
        plt.xticks(rotation=45)
        plt.grid(True, axis='y')
        plt.tight_layout()
        plt.savefig(f'interval_data_plots/BarPlot_{metric}.png')
    else:
        print(f"Metric '{metric}' not found in the dataset. Check if the metric name is correct.")




def main():
    directory = 'model-snapshots/interval_data_snapshots'
    data = load_data(directory)

    metrics = ['Accuracy', 'Precision', 'Recall', 'Specificity', 'F1 Score', 'AUC', 'True Negative Rate',
               'False Positive Rate', 'False Negative Rate', 'True Positive Rate', 'Total Samples', 
               'Compute per Analysis', 'Disk', 'RAM', 'Train Time']
    for metric in metrics:
        data[metric] = pd.to_numeric(data[metric], errors='coerce')

    plot_metrics(data, 'F1 Score', 'AUC')
    plot_metrics(data, 'F1 Score', 'AUC', title='F1 Score vs AUC (Absolute)', axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'Precision', 'Recall')
    plot_metrics(data, 'Precision', 'Recall', title='Precision vs Recall (Absolute)', axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'False Positive Rate', 'True Positive Rate', title='FPR vs TPR')
    plot_metrics(data, 'False Negative Rate', 'True Negative Rate', title='FNR vs TNR')
    plot_metrics(data, 'False Positive Rate', 'True Positive Rate', title='FPR vs TPR (Absolute)', axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'False Negative Rate', 'True Negative Rate', title='FNR vs TNR (Absolute)', axis_abs_low=True, axis_abs_high=True)

    plot_bar(data, 'Accuracy')
    plot_bar(data, 'Precision')
    plot_bar(data, 'Recall')
    plot_bar(data, 'Specificity')
    plot_bar(data, 'F1 Score')
    plot_bar(data, 'AUC')
    plot_bar(data, 'True Negative Rate')
    plot_bar(data, 'False Positive Rate')
    plot_bar(data, 'False Negative Rate')
    plot_bar(data, 'True Positive Rate')

if __name__ == "__main__":
    main()
