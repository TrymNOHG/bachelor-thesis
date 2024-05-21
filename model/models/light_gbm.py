from base import BaseModel
from lightgbm import LGBMClassifier
import pickle


class LGBMClassifierModel(BaseModel, LGBMClassifier):
    def __init__(
            self,
            X,
            y,
            n_estimators=100,
            *,
            learning_rate=0.05,
            max_depth=4,
            num_leaves=31,
            min_child_samples=20,
            min_child_weight=0.001,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=10,
            objective='binary',
            n_jobs=-1,
            random_state=None,
            verbosity=-1):
        BaseModel.__init__(self, X, y)
        self.model = LGBMClassifier(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            num_leaves=num_leaves,
            min_child_samples=min_child_samples,
            min_child_weight=min_child_weight,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            reg_alpha=reg_alpha,
            reg_lambda=reg_lambda,
            objective=objective,
            n_jobs=n_jobs,
            random_state=random_state,
            verbosity=verbosity)
    
    def train_impl(self):
        self.model.fit(self.X_train, self.y_train)

    def test(self, X) -> list[bool]:
        return self.model.predict(X).astype(bool)

    def grid_search(self):
        param_grid = {
            'max_depth': [3, 4, 5],
            'num_leaves': [20, 31, 40],
            'learning_rate': [0.01, 0.1, 0.3],
            'n_estimators': [50, 100, 150],
            'subsample': [0.6, 0.8, 1.0],
            'colsample_bytree': [0.6, 0.8, 1.0],
        }

        return self.default_stratified_grid_search(param_grid)

    def save(self, filename):
        pickle.dump(self.model, open(filename, 'wb'))
