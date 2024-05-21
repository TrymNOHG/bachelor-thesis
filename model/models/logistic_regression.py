from base import BaseModel
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score
import numpy as np
import pickle


class LogisticRegressorClassifier(BaseModel, LogisticRegression):
    def __init__(self, X, y, threshold=0.07):
        BaseModel.__init__(self, X, y)
        self.model = LogisticRegression(random_state=42,
                                        max_iter=10_000,
                                        multi_class='multinomial',
                                        solver='lbfgs')
        self.cutoff = threshold

    def train_impl(self):
        self.model.fit(self.X_train, self.y_train)

    def test(self, X) -> list[bool]:
        #return self.model.predict(self.X_test)
        pred = self.model.predict_proba(X)
        binary_predictions: list[bool] = []
        for p in pred:
            binary_predictions.append(p[1] > self.cutoff)
        return binary_predictions

    def save(self, filename):
        pickle.dump(self.model, open(filename, 'wb'))

    def grid_search(self):
        param_grid = {
            'C': [0.001, 0.01, 0.1, 1, 10, 100],  # Regularization parameter
            'penalty': ['l1', 'l2']  # Regularization type
        }

        return self.default_stratified_grid_search(param_grid)

    def tune_threshold(self):
        """
        Method to find the optimal threshold (cutoff) value for the dataset.
        NOTE: This can take a looong time for large datasets.
        """
        kf = StratifiedKFold(n_splits=5)
        thresholds = np.linspace(0, 1, 100)
        avg_f1_scores = []
        for threshold in thresholds:
            f1_scores = []
            for train_index, test_index in kf.split(self.X, self.y):
                X_train, X_test = self.X.iloc[train_index], self.X.iloc[test_index]
                y_train, y_test = self.y.iloc[train_index], self.y.iloc[test_index]

                self.model.fit(X_train, y_train)
                probabilities = self.model.predict_proba(X_test)
                predictions = (probabilities[:, 1] >= threshold).astype(int)
                f1 = f1_score(y_test, predictions)
                f1_scores.append(f1)

            # Average F1 score for this threshold
            avg_f1_scores.append(np.mean(f1_scores))

        best_threshold = thresholds[np.argmax(avg_f1_scores)]  # argmax gets the index
        print(f"Best Threshold: {best_threshold}")

