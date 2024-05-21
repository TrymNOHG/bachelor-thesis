from base import BaseModel
from sklearn.ensemble import AdaBoostClassifier
import pickle


class ABClassifier(BaseModel, AdaBoostClassifier):
    def __init__(self, 
            X, 
            y,
            estimator = None, 
            n_estimators=50, 
            learning_rate=1, 
            algorithm="SAMME", 
            random_state= None, 
            ):
        BaseModel.__init__(self, X, y)
        self.model = AdaBoostClassifier(
            estimator=estimator, 
            n_estimators=n_estimators, 
            learning_rate=learning_rate, 
            algorithm=algorithm, 
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
           'n_estimators': [10, 20, 50] ,
           'algorithm': ['SAMME' ,  'SAMME.R'],
           'learning_rate': [0.1, 0.05, 0.01]
        }

        return self.default_stratified_grid_search(param_grid)

