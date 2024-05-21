# The name of this file is only weird to make sure it doesn't overwrite the import from the original xg_boost module.
from base import BaseModel
from xgboost import XGBClassifier
import pickle


class XGBClassifierModel(BaseModel, XGBClassifier):
    def __init__(
            self,
            X,
            y,
            n_estimators=100,
            *,
            learning_rate=0.05,
            max_depth=4,
            min_child_weight=3,
            gamma=0,
            subsample=0.7,
            colsample_bytree=0.9,
            reg_alpha=0.1,
            reg_lambda=10,
            objective='binary:logistic',
            n_jobs=-1,
            random_state=None,
            verbosity=0):
        BaseModel.__init__(self, X, y)
        self.model = XGBClassifier(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            min_child_weight=min_child_weight,
            gamma=gamma,
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
        return self.model.predict(X)

    def grid_search(self):
        param_grid = {
            'max_depth': [3, 4, 5],
            'learning_rate': [0.01, 0.1, 0.3],
            'n_estimators': [50, 100, 150],
            'gamma': [0, 0.1, 0.2],
            'subsample': [0.6, 0.8, 1.0],
            'colsample_bytree': [0.6, 0.8, 1.0],
        }

        return self.default_stratified_grid_search(param_grid)

    def save(self, filename):
        pickle.dump(self.model, open(filename, 'wb'))

