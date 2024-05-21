from base import BaseModel
from sklearn.ensemble import RandomForestClassifier
import pickle


class RFClassifier(BaseModel, RandomForestClassifier):
    def __init__(
            self, 
            X, 
            y,
            n_estimators=100,
            *,
            criterion="gini",
            max_depth=None,
            min_samples_split=5,
            min_samples_leaf=2,
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
            ccp_alpha=0.0):
        BaseModel.__init__(self, X, y)
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            criterion=criterion,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            max_features=max_features,
            max_leaf_nodes=max_leaf_nodes,
            min_impurity_decrease=min_impurity_decrease,
            bootstrap=bootstrap,
            oob_score=oob_score,
            n_jobs=n_jobs,
            random_state=random_state,
            verbose=verbose,
            warm_start=warm_start,
            class_weight=class_weight,
            ccp_alpha=ccp_alpha)
    
    def train_impl(self):
        self.model.fit(self.X_train, self.y_train)

    def test(self, X) -> list[bool]:
        return self.model.predict(X)

    def save(self, filename):
        pickle.dump(self.model, open(filename, 'wb'))

    def grid_search(self):
        param_grid = {
            'n_estimators': [50, 100, 150], # Number of trees in the forest
            'max_depth': [None, 10, 20], # Maximum depth of the trees
            'min_samples_split': [2, 5, 10], # Minimum number of samples required to split a node
             # Minimum number of samples required to be at a leaf node.
             # Can prevent overfitting by.
            'min_samples_leaf': [1, 2, 4],
        }

        return self.default_stratified_grid_search(param_grid)

