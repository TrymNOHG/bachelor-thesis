import pandas as pd
import os
from models.random_forest import RFClassifier
from base import ModelDriver

data_directory = "interval_data"

file_list = [file for file in os.listdir(data_directory) if file.endswith('.csv')]

for file_name in file_list:
    file_path = os.path.join(data_directory, file_name)
    print(f"Processing file: {file_path}")

    df = pd.read_csv(file_path)

    df = df.dropna()

    X = df.drop(columns=[
        'Unnamed: 0',
        'is_fault',
        'ts',
    ])
    y = df['is_fault']

    model = RFClassifier(X, y)
    
    driver = ModelDriver(model)
    
    driver.take_snapshot(dataset_dir_name="interval_data", model_name=f"{file_name[:-4]}")
