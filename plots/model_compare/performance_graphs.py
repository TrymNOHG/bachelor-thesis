import matplotlib.pyplot as plt
from parse_snapshot import parse_all_snapshots, Snapshot
from adjustText import adjust_text

def generic_scatter(snapshots: list[Snapshot],
                    x_metric: str,
                    y_metric: str,
                    x_label: str,
                    y_label: str,
                    title=None,
                    axis_abs_low=False,
                    axis_abs_high=False):

    if title is None:
        title = x_metric + " and " + y_metric
    labels = []
    x = []
    y = []
    texts = []
    for snapshot in snapshots:
        model_name = "Node 4144: `" + snapshot.model_name.split("_")[3] + "s`"
        labels.append(model_name)
        x.append(snapshot.data[x_metric])
        y.append(snapshot.data[y_metric])

    plt.scatter(x, y, color="blue")

    if axis_abs_low:
        plt.ylim(bottom=0)
        plt.xlim(left=0)
    if axis_abs_high:
        plt.ylim(top=1)
        plt.xlim(right=1)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)

    for label, x_pos, y_pos in zip(labels, x, y):
        texts.append(plt.text(x_pos, y_pos, label, ha='right', va='top'))

    adjust_text(texts, only_move={'points':'y', 'texts':'y'}, arrowprops=dict(arrowstyle="->", color='r', lw=0.5))

    plt.grid(True)
    plt.savefig(f"plots/model_compare/{title}.png")
    plt.close()


def compute_and_auc(snapshots: list[Snapshot]):
    generic_scatter(snapshots,
                    x_metric="Compute per Analysis",
                    y_metric="AUC",
                    x_label="Compute time per prediction",
                    y_label="ROC AUC Score",
                    title="Compute - Performance")


def tpr_and_fpr(snapshots: list[Snapshot]):
    generic_scatter(snapshots,
                    x_metric="False Positive Rate",
                    y_metric="True Positive Rate",
                    x_label="False Positive Rate",
                    y_label="True Positive Rate")


if __name__ == "__main__":
    snapshots = parse_all_snapshots("model-snapshots/interval_data")
    compute_and_auc(snapshots)
    tpr_and_fpr(snapshots)
