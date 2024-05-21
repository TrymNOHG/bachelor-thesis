from base import BaseModel
from sklearn.tree import DecisionTreeClassifier
import pickle


class DTClassifier(BaseModel, DecisionTreeClassifier):
    def __init__(
            self, 
            X, 
            y,
            *,
            criterion="gini",
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            min_weight_fraction_leaf=0.0,
            max_features="sqrt",
            max_leaf_nodes=None,
            min_impurity_decrease=0.0,
            bootstrap=True,
            oob_score=False,
            n_jobs=None,
            random_state=None,
            verbose=0,
            warm_start=False,
            class_weight=None,
            ccp_alpha=0.0,
            max_samples=None):
        BaseModel.__init__(self, X, y)
        self.model = DecisionTreeClassifier(
            criterion=criterion,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            max_features=max_features,
            max_leaf_nodes=max_leaf_nodes,
            min_impurity_decrease=min_impurity_decrease,
            random_state=random_state,
            class_weight=class_weight,
            ccp_alpha=ccp_alpha,
            )

    def train_impl(self):
        self.model.fit(self.X_train, self.y_train)

    def test(self, X) -> list[bool]:
        return self.model.predict(X)

    def save(self, filename):
        pickle.dump(self.model, open(filename, 'wb'))

    def grid_search(self):
        param_grid = {
            'criterion': ['gini', 'entropy'],
            'max_depth': [None, 5, 10, 15],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }

        return self.default_stratified_grid_search(param_grid)

