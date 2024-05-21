import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import numpy as np
from adjustText import adjust_text

COLORBLIND_SAFE_COLORS = [
    "#000000", # Black
    "#FFA500", # Distinct Orange
    "#56B4E9", # Sky Blue
    "#009E73", # Green
    "#F0E442", # Yellow (Bright)
    "#0072B2", # Blue
    "#D32F2F", # Red
    "#999999", # Gray
    "#964B00", # Brown
    "#8A2BE2", # Blue Violet
    "#FF69B4", # Hot Pink
    "#40E0D0", # Turquoise
]



def extract_regex(input):
    filename, sort_regex = input
    match = re.search(sort_regex, filename)
    if match:
        return int(match.group(1))
    return 0


def load_data(directory, sort_regex=None):
    data_frames = []
    file_tuples = [(filename, sort_regex) for filename in os.listdir(directory)]
    sorted_file_tuples = sorted(file_tuples, key=extract_regex, reverse=False) if sort_regex is not None else file_tuples    
    sorted_files = [filename for filename, _ in sorted_file_tuples]
    for filename in sorted_files:
        if filename.endswith('.csv'):
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath, header=None, names=['Metric', 'Value'])
            df['Model Name'] = df.loc[df['Metric'] == 'Model name', 'Value'].iloc[0]
            df = df.pivot(index='Model Name', columns='Metric', values='Value').reset_index()
            data_frames.append(df)
    return pd.concat(data_frames, ignore_index=True)


def interval_data_name_format(row):
    model_name = "Node 4144: `" + row['Model Name'].split("_")[3] + "s`"
    return model_name

def plot_metrics(data, x_metric, y_metric, output_dir, legend_title=None, title=None, axis_abs_low=False, axis_abs_high=False, name_format=None,  show_numbers=True, x_unit=None, y_unit=None):
    plt.figure(figsize=(14, 8))
    texts = []
    for i, row in data.iterrows():
        if name_format is not None:
            model_name = name_format(row)
        else:
            model_name = row['Model Name']
        x = pd.to_numeric(row[x_metric], errors='coerce')
        y = pd.to_numeric(row[y_metric], errors='coerce')
        plt.scatter(x, y, label=f"{i+1}. {model_name}", s=300, color=COLORBLIND_SAFE_COLORS[i % len(COLORBLIND_SAFE_COLORS)])
        if show_numbers:
            text = plt.text(x, y, str(i+1), fontsize=16)
            texts.append(text)


    if axis_abs_low:
        plt.ylim(bottom=0)
        plt.xlim(left=0)
    if axis_abs_high:
        plt.ylim(top=1)
        plt.xlim(right=1)


    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    
    if x_unit is not None:
        plt.xlabel(x_metric+ f" ({x_unit})", fontsize=18)
    else:
        plt.xlabel(x_metric, fontsize=18)

    if y_unit is not None:
        plt.ylabel(y_metric + f" ({y_unit})", fontsize=18)
    else:
         plt.ylabel(y_metric, fontsize=18)

    if title is None:
        title = f'{x_metric} vs {y_metric}'
    plt.title(title, fontsize=24)
    plt.grid(True)

    if legend_title is not None:
        plt.legend(title=legend_title, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12, title_fontsize=14)
    else:
        plt.legend(title="Model Names", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=24, title_fontsize=28)

    plt.tight_layout()

    if show_numbers:
        adjust_text(
            texts,
            arrowprops=dict(arrowstyle='->', color='black', lw=0.5),
            expand_text=(1.2, 1.4),
            expand_objects=(1.2, 1.4),
            force_text=(0.5, 1.0),
            force_objects=(0.5, 1.0),
            lim=1000
        )    
    plt.savefig(f'{output_dir}/{title}.png')
    plt.close()


def plot_bar(data, metric, output_dir, xaxis_title=None, title=None, name_format=None):
    plt.figure(figsize=(14, 8))
    if metric in data.columns:
        metric_data = data[['Model Name', metric]]
        metric_data = metric_data.dropna(subset=[metric])
        metric_data[metric] = pd.to_numeric(metric_data[metric], errors='coerce')
        
        if name_format is not None:
            metric_data['Formatted Model Name'] = metric_data.apply(name_format, axis=1)
        else:
            metric_data['Formatted Model Name'] = metric_data['Model Name']

        grouped_data = metric_data.groupby('Formatted Model Name')[metric].mean()

        grouped_data = grouped_data.sort_values(ascending=False)

        grouped_data.plot(kind='bar', edgecolor='black')
        
        plt.title(title if title else f'Bar Plot of {metric}', fontsize=24)

        y_min = grouped_data.min()
        y_max = grouped_data.max()
        if abs(y_max - y_min) < 0.1 * y_max:
            plt.ylim(y_min - 0.05 * y_max, y_max + 0.05 * y_max)

        if xaxis_title is not None:
            plt.xlabel(xaxis_title, fontsize=18)
        else:
            plt.xlabel('Model Name', fontsize=18)
        
        plt.ylabel(metric, fontsize=18)
        plt.xticks(rotation=45, fontsize=14)
        plt.yticks(fontsize=14)
        plt.grid(True, axis='y')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/BarPlot_{metric}.png')
        plt.close()
    else:
        print(f"Metric '{metric}' not found in the dataset. Check if the metric name is correct.")


def main():
    directory = 'model-snapshots/interval_data_snapshots'
    data = load_data(directory, r'.*interval_(\d+)*.')

    metrics = ['Accuracy', 'Precision', 'Recall', 'Specificity', 'F1 Score', 'AUC', 'True Negative Rate',
               'False Positive Rate', 'False Negative Rate', 'True Positive Rate', 'Total Samples', 
               'Compute per Analysis', 'Disk', 'RAM', 'Train Time', 'Area under the Precision - Recall']
    for metric in metrics:
        data[metric] = pd.to_numeric(data[metric], errors='coerce')

    plot_metrics(data, 'F1 Score', 'AUC', 'images/interval_data_plots', legend_title='Granularity', name_format=interval_data_name_format)
    plot_metrics(data, 'F1 Score', 'AUC', 'images/interval_data_plots', legend_title='Granularity', title='F1 Score vs AUC (Absolute)', axis_abs_low=True, axis_abs_high=True, name_format=interval_data_name_format)
    plot_metrics(data, 'Precision', 'Recall', 'images/interval_data_plots', legend_title='Granularity', name_format=interval_data_name_format)
    plot_metrics(data, 'Precision', 'Recall', 'images/interval_data_plots', legend_title='Granularity', title='Precision vs Recall (Absolute)', axis_abs_low=True, axis_abs_high=True, name_format=interval_data_name_format)
    plot_metrics(data, 'False Positive Rate', 'True Positive Rate', 'images/interval_data_plots', legend_title='Granularity', title='FPR vs TPR', name_format=interval_data_name_format)
    plot_metrics(data, 'False Negative Rate', 'True Negative Rate', 'images/interval_data_plots', legend_title='Granularity', title='FNR vs TNR', name_format=interval_data_name_format)
    plot_metrics(data, 'False Positive Rate', 'True Positive Rate', 'images/interval_data_plots', legend_title='Granularity', title='FPR vs TPR (Absolute)', axis_abs_low=True, axis_abs_high=True, name_format=interval_data_name_format)
    plot_metrics(data, 'False Negative Rate', 'True Negative Rate', 'images/interval_data_plots', legend_title='Granularity', title='FNR vs TNR (Absolute)', axis_abs_low=True, axis_abs_high=True, name_format=interval_data_name_format)

    for metric in metrics:
        plot_bar(data, metric, 'images/interval_data_plots', name_format=interval_data_name_format)


def central_vs_distributed():
    directory = 'model-snapshots/model-scope/total'
    data = load_data(directory)
    metrics = ['Accuracy', 'Precision', 'Recall', 'Specificity', 'F1 Score', 'AUC', 'AUPRC', 'True Negative Rate',
               'False Positive Rate', 'False Negative Rate', 'True Positive Rate', 'Total Samples', 
               'Compute per Analysis', 'Disk', 'RAM']
    for metric in metrics:
        data[metric] = pd.to_numeric(data[metric], errors='coerce')

    plot_metrics(data, 'F1 Score', 'AUC', 'images/model_scope/total')
    plot_metrics(data, 'F1 Score', 'AUC', 'images/model_scope/total', title='F1 Score vs AUC (Absolute)', axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'Recall', 'Precision', 'images/model_scope/total', title='Precision vs Recall')
    plot_metrics(data, 'Recall', 'Precision', 'images/model_scope/total', title='Precision vs Recall (Absolute)', show_numbers=False, axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'False Positive Rate', 'True Positive Rate', 'images/model_scope/total', title='TPR vs FPR')
    plot_metrics(data, 'False Negative Rate', 'True Negative Rate', 'images/model_scope/total', title='TNR vs FNR')
    plot_metrics(data, 'False Negative Rate', 'True Positive Rate', 'images/model_scope/total', title='TPR vs FNR')
    plot_metrics(data, 'False Positive Rate', 'True Positive Rate', 'images/model_scope/total', title='TPR vs FPR (Absolute)', show_numbers=False, axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'False Negative Rate', 'True Negative Rate', 'images/model_scope/total', title='TNR vs FNR (Absolute)', show_numbers=False, axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'False Negative Rate', 'True Positive Rate', 'images/model_scope/total', title='TPR vs FNR (Absolute)', show_numbers=False, axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'Compute per Analysis', 'F1 Score', 'images/model_scope/total', title='F1 Score and compute time per analysis')
    plot_metrics(data, 'Compute per Analysis', 'Disk', 'images/model_scope/total', title='Disk space required and compute time per analysis', x_unit="seconds per analysis", y_unit="GB")

def central_vs_distributed_split():
    directory = 'model-snapshots/model-scope/split'
    data = load_data(directory)
    metrics = ['Accuracy', 'Precision', 'Recall', 'Specificity', 'F1 Score', 'AUC', 'AUPRC', 'True Negative Rate',
               'False Positive Rate', 'False Negative Rate', 'True Positive Rate', 'Compute per Analysis', 'Disk', 'RAM']
    for metric in metrics:
        data[metric] = pd.to_numeric(data[metric], errors='coerce')

    plot_metrics(data, 'F1 Score', 'AUC', 'images/model_scope/split')
    plot_metrics(data, 'F1 Score', 'AUC', 'images/model_scope/split', title='F1 Score vs AUC (Absolute)', axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'Recall', 'Precision', 'images/model_scope/split', title='Precision vs Recall')
    plot_metrics(data, 'Recall', 'Precision', 'images/model_scope/split', title='Precision vs Recall (Absolute)', show_numbers=False, axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'False Positive Rate', 'True Positive Rate', 'images/model_scope/split', title='TPR vs FPR')
    plot_metrics(data, 'False Negative Rate', 'True Negative Rate', 'images/model_scope/split', title='TNR vs FNR')
    plot_metrics(data, 'False Negative Rate', 'True Positive Rate', 'images/model_scope/split', title='TPR vs FNR')
    plot_metrics(data, 'False Positive Rate', 'True Positive Rate', 'images/model_scope/split', show_numbers=False, title='TPR vs FPR (Absolute)', axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'False Negative Rate', 'True Negative Rate', 'images/model_scope/split', show_numbers=False, title='TNR vs FNR (Absolute)', axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'False Negative Rate', 'True Positive Rate', 'images/model_scope/split', show_numbers=False, title='TPR vs FNR (Absolute)', axis_abs_low=True, axis_abs_high=True)


def central_vs_distributed_per_node():
    directory = 'model-snapshots/model-scope/centralized-per-node'
    data = load_data(directory)
    metrics = ['Accuracy', 'Precision', 'Recall', 'Specificity', 'F1 Score', 'AUC', 'AUPRC', 'True Negative Rate',
               'False Positive Rate', 'False Negative Rate', 'True Positive Rate']
    for metric in metrics:
        data[metric] = pd.to_numeric(data[metric], errors='coerce')

    plot_metrics(data, 'F1 Score', 'AUC', 'images/model_scope/centralized-per-node')
    plot_metrics(data, 'F1 Score', 'AUC', 'images/model_scope/centralized-per-node', title='F1 Score vs AUC (Absolute)', axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'Recall', 'Precision', 'images/model_scope/centralized-per-node', title='Precision vs Recall')
    plot_metrics(data, 'Recall', 'Precision', 'images/model_scope/centralized-per-node', title='Precision vs Recall (Absolute)', show_numbers=False, axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'False Positive Rate', 'True Positive Rate', 'images/model_scope/centralized-per-node', title='TPR vs FPR')
    plot_metrics(data, 'False Negative Rate', 'True Negative Rate', 'images/model_scope/centralized-per-node', title='TNR vs FNR')
    plot_metrics(data, 'False Negative Rate', 'True Positive Rate', 'images/model_scope/centralized-per-node', title='TPR vs FNR')
    plot_metrics(data, 'False Positive Rate', 'True Positive Rate', 'images/model_scope/centralized-per-node', title='TPR vs FPR (Absolute)', show_numbers=False, axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'False Negative Rate', 'True Negative Rate', 'images/model_scope/centralized-per-node', title='TNR vs FNR (Absolute)', show_numbers=False, axis_abs_low=True, axis_abs_high=True)
    plot_metrics(data, 'False Negative Rate', 'True Positive Rate', 'images/model_scope/centralized-per-node', title='TPR vs FNR (Absolute)', show_numbers=False, axis_abs_low=True, axis_abs_high=True)


if __name__ == "__main__":
    # oslo_compare()
    central_vs_distributed()
    # central_vs_distributed_split()
    central_vs_distributed_per_node()