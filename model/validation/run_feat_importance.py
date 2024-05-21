from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import feat_importance as fi
import pandas as pd 
import pickle

df = pd.read_csv("../../data/2_week_data/4120_2_week_aggregated_proc.csv") # Use correct dataset
df = df.dropna()

X = df.drop(columns=[
    # 'Unnamed: 0', # Comment back?
    'is_fault',
    'ts', 
    ])
y = df['is_fault']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=420) # Use correct split

with open('random_forest_model.pkl', 'rb') as file: # Use correct pickle.
    model = pickle.load(file)
model_explainer = fi.get_SHAP_explainer(model)

model_predictions = model.predict(X_test)
true_postive_idx = []
true_negative_idx = []
false_postive_idx = []
false_negative_idx = []

for index, pred in enumerate(model_predictions):
    if y_test[index] == pred:
        if pred == 1:
            true_postive_idx.append(index)
        else:
            true_negative_idx.append(index)
    else:
        if pred == 1:
            false_postive_idx.append(index)
        else:
            false_negative_idx.append(index)

mispredict_indices = false_negative_idx + false_postive_idx
correct_predict_indices = true_postive_idx + true_negative_idx

# Showing top 15 features.
fi.calculate_SHAP(model_explainer, X_test, title="Global Feature Importance", num_features=15, image_save_path="global-feat-import.png") # Global importance
fi.calculate_SHAP(model_explainer, X_test.iloc[mispredict_indices], num_features=15, title="Local Mispredictions Feature Importance", image_save_path="local-mispred-feat-import.png") # Local importance
fi.calculate_SHAP(model_explainer, X_test.iloc[correct_predict_indices], num_features=15, title="Local Correct Prediction Feature Importance", image_save_path="local-correct-pred-feat-import.png") # Local importance
fi.calculate_SHAP(model_explainer, X_test.iloc[true_postive_idx], num_features=15, title="Local True Positive Feature Importance", image_save_path="local-true-pos-feat-import.png") # Local importance
fi.calculate_SHAP(model_explainer, X_test.iloc[true_negative_idx], num_features=15, title="Local True Negative Feature Importance", image_save_path="local-true-negative-pred-feat-import.png") # Local importance
fi.calculate_SHAP(model_explainer, X_test.iloc[false_postive_idx], num_features=15, title="Local False Positive Feature Importance", image_save_path="local-false-pos-feat-import.png") # Local importance
fi.calculate_SHAP(model_explainer, X_test.iloc[false_negative_idx], num_features=15, title="Local False Negative Feature Importance", image_save_path="local-false-negative-feat-import.png") # Local importance