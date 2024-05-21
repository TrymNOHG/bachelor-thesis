from sklearn.svm import SVC
from base import BaseModel
import pickle


class SVClassifier(BaseModel, SVC):
    def __init__(self, 
            X, 
            y,
            C=1.0,
            kernel="rbf",
            degree=3,
            gamma="scale",
            coef0=0.0,
            shrinking=True,
            probability=False,
            tol=1e-3,
            cache_size=200,
            class_weight=None,
            verbose=False,
            max_iter=-1,
            decision_function_shape="ovr",
            break_ties=False,
            random_state=42,
            ):
        BaseModel.__init__(self, X, y)
        self.model = SVC(
            C=C,
            kernel=kernel,
            degree=degree,
            gamma=gamma,
            coef0=coef0,
            shrinking=shrinking,
            probability=probability,
            tol=tol,
            cache_size=cache_size,
            class_weight=class_weight,
            verbose=verbose,
            max_iter=max_iter,
            decision_function_shape=decision_function_shape,
            break_ties=break_ties,
            random_state=random_state,
        )
       
    def train_impl(self):
        self.model.fit(self.X_train, self.y_train)

    def test(self, X) -> list[bool]:
        return self.model.predict(X)

    def save(self, filename):
        pickle.dump(self.model, open(filename, 'wb'))

    def grid_search(self):
        param_grid = {
            'kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
            'C': [0.1, 1, 10], 
            'degree': [1, 2, 3],
            'gamma': [0.01, 0.1, 1],
            'class_weight' : ['balanced']
        }

        return self.default_stratified_grid_search(param_grid)

