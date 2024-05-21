from validation.feat_importance import display_mdi_feat_importance
from abc import ABC, abstractmethod
from typing import Literal, Union
import math
import pickle
import time
import os
import csv
import psutil
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import sklearn.model_selection as SKML
from sklearn.metrics import roc_auc_score, PrecisionRecallDisplay, average_precision_score
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from imblearn.under_sampling import RandomUnderSampler, NearMiss
import pandas as pd


class ConfusionMatrix:
    def __init__(self, actual_values: list[bool], predicted_values: list[bool]):
        self.true_positives: float = 0
        self.false_positives: float = 0
        self.true_negatives: float = 0
        self.false_negatives: float = 0

        for pred, actual in zip(predicted_values, actual_values):
            if pred == True and actual == True:
                self.true_positives += 1
            if pred == True and actual == False:
                self.false_positives += 1
            if pred == False and actual == False:
                self.true_negatives += 1
            if pred == False and actual == True:
                self.false_negatives += 1

    def display(self, save_mode=False, file_name="cfm.png"):
        tn_rate, fp_rate, fn_rate, tp_rate = self.as_rates()
        matrix = np.array([[tp_rate, fp_rate],
                           [fn_rate, tn_rate]])

        sns.heatmap(matrix, annot=True, fmt="g", cmap='viridis',
                    xticklabels=['Predicted Positive', 'Predicted Negative'],
                    yticklabels=['Actual Positive', 'Actual Negative'])
        plt.title('Confusion Matrix')
        plt.savefig(file_name)
        if not save_mode:
            plt.show()

    def as_rates(self):
        tn_rate = self.true_negatives / (self.true_negatives + self.false_positives)
        fp_rate = 1 - tn_rate
        fn_rate = self.false_negatives / (self.false_negatives + self.true_positives)
        tp_rate = 1 - fn_rate
        return tn_rate, fp_rate, fn_rate, tp_rate


    def __repr__(self) -> str:
        return (f"ConfusionMatrix(TP={self.true_positives}, FP={self.false_positives}, "
                f"TN={self.true_negatives}, FN={self.false_negatives})")


class BaseModel(ABC):
    """
    Abstract class for a model. All models should inherit from this class.

    Args:
        X: Features
        y: Target values
        undersample_method: Method for undersampling the dataset. Options are 'random' and 'nearmiss'.
    """
    def __init__(self, X, y):
        self.has_trained = False
        self.X = X
        self.X_pre_len = len(X)
        self.y = y
        # self.X, self.y = self.undersample(self.X, self.y)
        self.test_size = 0.2  # Proportion of the dataset that goes into the test spit
        self.X_train, self.X_test, self.y_train, self.y_test = \
                SKML.train_test_split(self.X, self.y, test_size=self.test_size, random_state=420)
        # Undersampling for only the train split
        self.X_train, self.y_train = self.undersample(self.X_train, self.y_train)

    def train(self, take_time=False):
        start_time = time.time()
        self.train_impl()
        self.has_trained = True
        if take_time:
            return time.time() - start_time

    @abstractmethod
    def train_impl(self):
        pass

    @abstractmethod
    def test(self, X) -> list[bool]:
        pass

    @abstractmethod
    def save(self, filename: str):
        pass

    @abstractmethod
    def grid_search(self):
        """
        Returns best model along with best params
        """
        pass

    def default_stratified_grid_search(self, param_grid: dict[str, list], num_folds=5):
        stratified_cv = StratifiedKFold(n_splits=num_folds, shuffle=True, random_state=42)
        grid_search = GridSearchCV(estimator=self.model, param_grid=param_grid, cv=stratified_cv, scoring='f1')
        grid_search.fit(self.X_train, self.y_train)

        best_params = grid_search.best_params_
        print("Best Hyperparameters:", best_params)
        best_score = grid_search.best_score_
        print("Best score:", best_score)
        return grid_search.best_estimator_, grid_search.best_params_

    def benchmark(self, n_samples, n_runs) -> tuple[float, float, float]:
        """
        Returns
            compute_time, disk footprint, RAM footprint
        """
        assert n_samples <= len(self.X_test)
        compute_time = self._compute_time(n_samples, n_runs)
        return compute_time, self._disk_footprint(), self._ram_footprint()

    def _compute_time(self, n_samples, n_runs):
        start = time.perf_counter()
        for _ in range(n_runs):
            self.test(self.X_test[:n_samples])
        end = time.perf_counter()
        return end - start

    def _disk_footprint(self) -> float:
        """
        Calculate the memory footprint of the saved model file.

        Returns:
        float: The memory footprint of the saved model file in bytes.
        """
        tmp_file_name = "model_tmp.pkl"
        self.save(tmp_file_name)

        if not os.path.exists(tmp_file_name):
            raise FileNotFoundError(f"File '{tmp_file_name}' not found.")
        return os.path.getsize(tmp_file_name)

    def _ram_footprint(self) -> float:
        """
        NOTE: Due to "random" GC behaviour, this function is extremely inprecise.
        """
        tmp_file_name = "model_tmp.pkl"
        self.save(tmp_file_name)

        mem_before = psutil.Process().memory_info().rss
        with open(tmp_file_name, "rb") as f:
            loaded_model = pickle.load(f)
            mem_after = psutil.Process().memory_info().rss

        loaded_model = None
        return mem_after - mem_before

    def effective_split_ratio(self):
        # Make sure X_train is defined
        assert self.X_train is not None
        return len(self.X_test) / (len(self.X_train) + len(self.X_test))

    def undersample(self, X: pd.DataFrame, y: pd.DataFrame, undersampling_type: Literal['random', 'nearmiss']='random'):
        if "random" == undersampling_type:
            rus = RandomUnderSampler(random_state=0)
            return rus.fit_resample(X, y)
        elif "nearmiss" == undersampling_type:
            nm = NearMiss()
            return nm.fit_resample(X, y)

    def _accuracy(self, cfm: ConfusionMatrix) -> float:
        """
        Formula:
            accuracy = correct predictions / total predictions
            or
            accuracy = ( true positives + true negatives ) / ( true positives + true negatives +
                                                               false positives + false negatives )
        """
        assert cfm is not None
        return (cfm.true_positives + cfm.true_negatives) / (cfm.true_positives + cfm.true_negatives +

    def _precision(self, cfm: ConfusionMatrix) -> float:
        """
        Precision is a metric that measures the accuracy of the positive predictions made by
        the classifier. Specifically, it's the proportion of true positive predictions out
        of all the predictions that labeled as positive.
        """
        return cfm.true_positives / (cfm.true_positives + cfm.false_positives)

    def _recall(self, cfm: ConfusionMatrix) -> float:
        """
        Recall (also known as sensitivity) measures the ability to correctly identify all the
        relevant instances. Specifically, recall is the proportion of true positive predictions
        out of all actual positives in the data. Same as true positive rate.
        """
        return cfm.true_positives / (cfm.true_positives + cfm.false_negatives)

    def _specificity(self, cfm: ConfusionMatrix) -> float:
        """
        Specificity measures how many of the actual negative items are identified correctly.
        """
        return cfm.true_negatives / (cfm.true_negatives + cfm.false_positives)

    def _f1_score(self, cfm: ConfusionMatrix) -> float:
        """
        The F1 Score represents a balance between precision and recall. It's useful when the class
        distribution is uneven and when false negatives and false positives carry different costs.

        The F1 Score reaches its best value at 1 (perfect precision and recall) and its worst at 0.
        """
        precision = self._precision(cfm)
        recall = self._recall(cfm)

        try:
            return 2 * (precision * recall) / (precision + recall)
        except ZeroDivisionError:
            return 0
        
    def _auprc(self, y_true, y_scores):
        """
        Precision-Recall Curve's Area under Curve.

        The area under curve for the precision-recall curve can be determined through interpolation of the curve. However, multiple research
        papers indicate that this may lead to over-optimistic results. Instead, the average precision score is recommended as an alternative metric for area under curve.
        """
        return average_precision_score(y_true, y_scores, average='micro')

    def _pr_curve(self, estimator, save: str = None, auprc: float = None) -> None:
        """
        Precision-Recall curve. Alternative to the ROC curve. Particularly useful in cases 
        of imbalanced datasets. This is because true positive rate and false positive rate
        (as used in ROC) can be misleading when one of the classes dominate the other.
        """

        baseline = (self.y_test == True).sum() / len(self.y_test)

        PrecisionRecallDisplay.from_estimator(estimator, self.X_test, self.y_test)
        plt.plot([0, 1], [baseline, baseline], linestyle='--', label='Baseline')
        if save is not None:
            plt.savefig(save)
        plt.show()

    def _roc_auc(self, actual_values: list[bool], predicted_values: list[bool]) -> float:
        """
        Comparison of true positive rate and false positive rate.
        """
        return roc_auc_score(actual_values, predicted_values)
    
    def _roc_curve(self, cfm: ConfusionMatrix, save: str = None) -> None:
        _, fp_rate, _, tp_rate = cfm.as_rates()
        plt.plot(fp_rate, tp_rate, 'ro', label='Model Performance')
        plt.plot([0, 1], [0, 1], 'k--', label='Random Guess')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend()
        if save is not None:
            plt.savefig(save)
        plt.show()

    def validate(self, print_metrics=False, X=None, y=None) -> tuple:
        # If X and y is not specified then the default behaviour is to use the test set
        if X is None or y is None:
            # If either X or y is specified, then the other must be specified as well
            assert X is None and y is None
            X = self.X_test
            y = self.y_test

        predictions: list[bool] = self.test(X)
        cf_matrix = ConfusionMatrix(y, predictions)
        accuracy = self._accuracy(cf_matrix)
        precision = self._precision(cf_matrix)
        recall = self._recall(cf_matrix)
        specificity = self._specificity(cf_matrix)
        f1_score = self._f1_score(cf_matrix)
        auc = self._roc_auc(y, predictions)
        auprc = self._auprc(y, predictions)

        if print_metrics:
            print("Actual split ratio:",  self.effective_split_ratio())
            print("Total data points pre-sample:",  self.X_pre_len)
            print("Total data post-sample:",  len(self.X_train) + len(X))
            print(cf_matrix)
            _, fp_rate, fn_rate, _ = cf_matrix.as_rates()
            print(f"False Positive Rate: {fp_rate:.4f}")
            print(f"False Negative Rate: {fn_rate:.4f}")

            print(f"Accuracy: {accuracy:.4f}")
            print(f"Recall or True Positive Rate: {recall:.4f}")
            print(f"Specificity or True Negative Rate: {specificity:.4f}")
            print(f"G-Mean: {math.sqrt(recall * specificity):.4f}")

            print(f"Precision: {precision:.4f}")
            print(f"F1 Score: {f1_score:.4f}")
            print(f"AUC: {auc:.4f}")
            print(f"AUPRC or Average Precision Score: {auprc:.4f}")

            self._roc_curve(cf_matrix)
            cf_matrix.display()

        return cf_matrix, accuracy, precision, recall, specificity, f1_score, auc, auprc


class ModelDriver():
    def __init__(self, model: Union[BaseModel, None], filename: str = ""):
        if model is None:
            if filename == "":
                print("Bad use of the ModelDriver API.")
                print("If model is None, then you must specify a filename where a model can be\
                        loaded from a '.pkl' file.")
                assert False  # fail
            self.model = self.load(filename)
        else:
            assert model is not None  # for the LSP
            self.model = model

    def _ensure_model_is_trained(self):
        if not self.model.has_trained:
            self.model.train()

    def retrain(self):
        self.model.has_trained = False
        self._ensure_model_is_trained()
        return self.model.validate(print_metrics=True)

    def load(self, filename) -> BaseModel:
        return pickle.load(open(filename, 'rb'))

    def pred(self, X):
        self._ensure_model_is_trained()
        return self.model.test(X)

    def training_error(self, print_metrics=True):
        """
            Wrapper for BaseModel's validate() using the training set
        """
        self._ensure_model_is_trained()
        X = self.model.X_train
        y = self.model.y_train
        return self.model.validate(print_metrics=print_metrics, X=X, y=y)

    def test_error(self, print_metrics=True):
        """
            Wrapper for BaseModel's validate(), automatically using the test set
        """
        self._ensure_model_is_trained()
        return self.model.validate(print_metrics=print_metrics)

    def std_benchmark(self, samples=10_000, runs=10, print_metrics=False):
        self._ensure_model_is_trained()

        total_samples = samples * runs
        compute, disk, ram = self.model.benchmark(samples, runs)
        compute_per_analysis = compute / total_samples
        if print_metrics:
            print(f"Compute time: {compute} s. Compute time per analysis: {compute_per_analysis} s")
            print(f"Disk footprint: {disk / (1024 ** 2)} MB")
            print(f"RAM footprint: {ram / (1024 ** 2)} MB")

        return total_samples, compute_per_analysis, disk, ram

    def best_snapshot(self, dataset_dir_name):
        model_name = type(self.model).__name__
        best_estimator, best_params = self.model.grid_search()
        if best_params is not None:
            print("Best Parameters:", best_params)
        self.model.model = best_estimator
        self.take_snapshot(model_name, dataset_dir_name)

    def take_snapshot(self, model_name, dataset_dir_name):
        # We always want to retrain the model before taking a snapshot of it so we can get the
        # time it takes to train.
        train_time = self.model.train(take_time=True)

        snapshot_dir = os.path.join("..", "model-snapshots") # Create directory if it doesn't exist
        os.makedirs(snapshot_dir, exist_ok=True)
        dataset_dir = os.path.join(snapshot_dir, dataset_dir_name)
        os.makedirs(dataset_dir, exist_ok=True)

        # Generate file name on the format: DAY-MONTH-model_name
        timestamp = datetime.now().strftime("%d-%B")
        file_name = f"{timestamp}-{model_name}"
        results_file_path = os.path.join(dataset_dir, file_name + ".csv")
        model_file_path = os.path.join(dataset_dir, file_name + ".pkl")
        self.model.save(str(model_file_path))

        cf_matrix, accuracy, precision, recall, specificity, f1_score, auc, auprc = self.model.validate()
        tn_rate, fp_rate, fn_rate, tp_rate = cf_matrix.as_rates()
        total_samples, compute_per_analysis, disk, ram = self.std_benchmark()

        with open(results_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Model name', model_name])
            writer.writerow(['Dataset name', dataset_dir_name])
            writer.writerow(['Accuracy', accuracy])
            writer.writerow(['Precision', precision])
            writer.writerow(['Recall', recall])
            writer.writerow(['Specificity', specificity])
            writer.writerow(['F1 Score', f1_score])
            writer.writerow(['AUC', auc])
            writer.writerow(['True Negative Rate', tn_rate])
            writer.writerow(['False Positive Rate', fp_rate])
            writer.writerow(['False Negative Rate', fn_rate])
            writer.writerow(['True Positive Rate', tp_rate])
            writer.writerow(['Area under the Precision - Recall', auprc])
            writer.writerow(['Total Samples', total_samples])
            writer.writerow(['Compute per Analysis', compute_per_analysis])
            writer.writerow(['Disk', disk])
            writer.writerow(['RAM', ram])
            writer.writerow(['Train Time', train_time])
