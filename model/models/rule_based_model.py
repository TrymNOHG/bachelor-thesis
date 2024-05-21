from base import BaseModel
import pickle


class RuleBasedModel(BaseModel):
    def __init__(self, X, y):
        BaseModel.__init__(self, X, y)

    def train_impl(self):
        pass

    def test(self, X) -> list[bool]:
        return X.apply(self._predict, axis=1)

    def save(self, filename):
        pickle.dump(self, open(filename, 'wb'))

    def grid_search(self):
        return self, None

    def _predict(self, row):
        prev = row["rtt"]
        if prev > 50:
            return True

        rsrq = row["rsrq"]
        return rsrq <= -10
