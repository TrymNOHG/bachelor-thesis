from base import BaseModel
from catboost import CatBoostClassifier
import pickle


class CatBoostClassifierModel(BaseModel):
    def __init__(
            self,
            X,
            y,
            n_estimators=1500,
            *,
            learning_rate=0.2,
            depth=7,
            l2_leaf_reg=3,
            bootstrap_type='MVS',
            subsample=0.8,
            objective='Logloss',
            random_state=None,
            verbosity=0):
        super().__init__(X, y)
        self.model = CatBoostClassifier(
            iterations=n_estimators,
            learning_rate=learning_rate,
            depth=depth,
            l2_leaf_reg=l2_leaf_reg,
            bootstrap_type=bootstrap_type,
            subsample=subsample,
            objective=objective,
            random_state=random_state,
            verbose=verbosity)

    def train_impl(self):
        self.model.fit(self.X_train, self.y_train)

    def test(self, X) -> list[bool]:
        return self.model.predict(X).astype(bool)

    def grid_search(self):
        param_grid = {
            'depth': [7, 8, 9],
            'learning_rate': [0.2, 0.3],
            'iterations': [1500, 2000, 2500],
            'bootstrap_type': ['Bernoulli', 'MVS'],
        }
        return self.default_stratified_grid_search(param_grid)

    def save(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.model, file)

