from base import BaseModel
from pytorch_tabnet.tab_model import TabNetClassifier
import torch
import numpy as np


class TNClassifier(BaseModel, TabNetClassifier):
    def __init__(
            self, 
            X,
            y,
            under_sample_method="random"):
        BaseModel.__init__(self, X, y, undersample_method=under_sample_method)
        self.model = TabNetClassifier(verbose=1, n_d=16, n_a=16, n_steps=5, optimizer_fn=torch.optim.SGD, scheduler_params={"step_size":50, "gamma":0.95}, scheduler_fn=torch.optim.lr_scheduler.StepLR, seed=0)
    
    def train(self):
        X_train_np = self.X_train.values.astype(np.float32)
        X_test_np = self.X_test.values.astype(np.float32)
        y_train_np = self.y_train.values.astype(np.float32)
        y_test_np = self.y_test.values.astype(np.float32)

        self.model.fit(
            X_train_np, y_train_np, 
            eval_set=[(X_train_np, y_train_np), (X_test_np, y_test_np)],
            eval_name=['train', 'test'],
            eval_metric=['auc', 'balanced_accuracy'],
            max_epochs=10, patience=60,
            batch_size=512, virtual_batch_size=128,
            num_workers=8, weights=1, drop_last=False
        )

    def test(self) -> list[bool]:
        X_test_np = self.X_test.values.astype(np.float32)
        return self.model.predict(X_test_np).tolist()

