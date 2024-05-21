import pandas as pd
import pickle
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, StratifiedShuffleSplit
import feat_importance as fi
import time
import threading

df = pd.read_csv("../../interval_data/4144_interval_1_3_months_aggregated_proc.csv")
df = df.dropna()

X = df.drop(columns=['Unnamed: 0', 'is_fault', 'ts'])
y = df['is_fault']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=420)

with open('../../model-snapshots/oslo_3_month_aggregated_proc/15-May-catboost_4144_interval_1_3_months_aggregated_proc.pkl', 'rb') as file:
    model = pickle.load(file)

def create_explainer():
    return fi.get_SHAP_explainer(model)

model_predictions = model.predict(X_test)

true_positive_idx = []
true_negative_idx = []
false_positive_idx = []
false_negative_idx = []

for index, pred in enumerate(model_predictions):
    if y_test.iloc[index] == pred:
        if pred == 1:
            true_positive_idx.append(index)
        else:
            true_negative_idx.append(index)
    else:
        if pred == 1:
            false_positive_idx.append(index)
        else:
            false_negative_idx.append(index)

mispredict_indices = false_negative_idx + false_positive_idx
correct_predict_indices = true_positive_idx + true_negative_idx

def stratified_sample(indices, y, n_samples=100):
    if len(indices) > n_samples:
        sss = StratifiedShuffleSplit(n_splits=1, test_size=n_samples, random_state=42)
        y_subset = y.iloc[indices]
        _, test_idx = next(sss.split(indices, y_subset))
        return pd.Series(indices).iloc[test_idx].tolist()
    else:
        return indices

global_indices = stratified_sample(mispredict_indices + correct_predict_indices, y_test, n_samples=100)
mispredict_indices = stratified_sample(mispredict_indices, y_test, n_samples=100)
correct_predict_indices = stratified_sample(correct_predict_indices, y_test, n_samples=100)
true_positive_idx = stratified_sample(true_positive_idx, y_test, n_samples=100)
true_negative_idx = stratified_sample(true_negative_idx, y_test, n_samples=100)
false_positive_idx = stratified_sample(false_positive_idx, y_test, n_samples=100)
false_negative_idx = stratified_sample(false_negative_idx, y_test, n_samples=100)

def print_class_balance(indices, y, label):
    balance = y.iloc[indices].value_counts(normalize=True) * 100
    print(f"{label} class balance:\n{balance}\n")

print_class_balance(global_indices, y_test, "All")
print_class_balance(mispredict_indices, y_test, "Mispredict")
print_class_balance(correct_predict_indices, y_test, "Correct Predict")
print_class_balance(true_positive_idx, y_test, "True Positive")
print_class_balance(true_negative_idx, y_test, "True Negative")
print_class_balance(false_positive_idx, y_test, "False Positive")
print_class_balance(false_negative_idx, y_test, "False Negative")

plot_lock = threading.Lock()

def calculate_and_save_SHAP(explainer, X, num_features, title, image_save_path):
    print(title)
    start_time = time.time()
    fi.calculate_SHAP(explainer, X, num_features=num_features, title=title, image_save_path=image_save_path, thread_lock=plot_lock)
    end_time = time.time()
    print(f"{title} took {end_time - start_time:.2f} seconds to run")

with ProcessPoolExecutor(max_workers=7) as executor:
    futures = [
        executor.submit(calculate_and_save_SHAP, create_explainer(), X_test.iloc[global_indices].copy(), 15, "Global Feature Importance", "global-feat-import.png"),
        executor.submit(calculate_and_save_SHAP, create_explainer(), X_test.iloc[mispredict_indices].copy(), 15, "Local Mispredictions Feature Importance", "local-mispred-feat-import.png"),
        executor.submit(calculate_and_save_SHAP, create_explainer(), X_test.iloc[correct_predict_indices].copy(), 15, "Local Correct Prediction Feature Importance", "local-correct-pred-feat-import.png"),
        executor.submit(calculate_and_save_SHAP, create_explainer(), X_test.iloc[true_positive_idx].copy(), 15, "Local True Positive Feature Importance", "local-true-pos-feat-import.png"),
        executor.submit(calculate_and_save_SHAP, create_explainer(), X_test.iloc[true_negative_idx].copy(), 15, "Local True Negative Feature Importance", "local-true-negative-pred-feat-import.png"),
        executor.submit(calculate_and_save_SHAP, create_explainer(), X_test.iloc[false_positive_idx].copy(), 15, "Local False Positive Feature Importance", "local-false-pos-feat-import.png"),
        executor.submit(calculate_and_save_SHAP, create_explainer(), X_test.iloc[false_negative_idx].copy(), 15, "Local False Negative Feature Importance", "local-false-negative-feat-import.png"),
    ]
    
    for future in futures:
        future.result() 