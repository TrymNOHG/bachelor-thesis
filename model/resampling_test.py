from base import ModelDriver
from models.random_forest import RFClassifier
import pandas as pd

df = pd.read_csv("./interval_data/4144_interval_1_3_months_aggregated_proc.csv")
df = df.iloc[600:]

X = df.drop(columns=['ts', 'is_fault', 'Unnamed: 0'])
y = df['is_fault']

resampling_methods = ['none', 'random', 'nearmiss', 'smote', 'adasyn', 
                      'borderline_smote', 'random_os']
for method in resampling_methods:
    print(f"Method:{method}")
    model = RFClassifier(X, y, resampling_type=method)
    driver = ModelDriver(model)
    driver.take_snapshot(method, "resampling")
