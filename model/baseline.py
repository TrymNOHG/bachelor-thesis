from base import ModelDriver
from models.random_forest import RFClassifier
from models.logistic_regression import LogisticRegressorClassifier
from models.cat_boost import CatBoostClassifierModel
from models.rule_based_model import RuleBasedModel
from models.decision_tree import DTClassifier
from models.ada_boost import ABClassifier
from models.svc import SVClassifier
from validation.feat_importance import display_mdi_feat_importance, display_perm_importance, calculate_SHAP
from sklearn.inspection import permutation_importance
import pandas as pd 


df = pd.read_csv("./oslo_3_month_aggregated_proc.csv")
# The first measurements will contain NaN for certain rtt metrics as there are no previous
# measurements to calculate the from
df = df.dropna()

X = df.drop(columns=[
    'Unnamed: 0',
    'is_fault',
    'ts', 
    # 'rssi',
    # 'rsrq', 
    # 'rsrp', 
    # 'rtt', 
    # 'rtt_2s_mean', 
    # 'rtt_3s_mean',
    # 'rtt_4s_mean', 
    # 'rtt_5s_mean', 
    # 'rtt_10s_mean', 
    # 'rtt_30s_mean',
    # 'rtt_1min_mean', 
    # 'rtt_5min_mean', 
    # 'ts_0', 
    # 'ts_1', 
    # 'ts_10', 
    # 'ts_11',
    # 'ts_12',
    # 'ts_13', 
    # 'ts_14', 
    # 'ts_15', 
    # 'ts_16', 
    # 'ts_17', 
    # 'ts_18', 
    # 'ts_19',
    # 'ts_2', 
    # 'ts_20', 
    # 'ts_21', 
    # 'ts_22', 
    # 'ts_23', 
    # 'ts_3', 
    # 'ts_4', 
    # 'ts_5',
    # 'ts_6', 
    # 'ts_7', 
    # 'ts_8', 
    # 'ts_9', 
    # 'node_id_4120', 
    # 'node_id_4125',
    # 'node_id_4126', 
    # 'node_id_4144', 
    # 'node_id_4147', 
    # 'population_HIGH',
    # 'population_LOW', 
    # 'population_MEDIUM', 
    # 'weekday_Friday',
    # 'weekday_Monday', 
    # 'weekday_Saturday', 
    # 'weekday_Sunday',
    # 'weekday_Thursday', 
    # 'weekday_Tuesday', 
    # 'weekday_Wednesday'
    ])
y = df['is_fault']


model = CatBoostClassifierModel(X, y)
#model = RuleBasedModel(X, y)
#model = LogisticRegressorClassifier(X, y)
#model = DTClassifier(X, y)
# model = ABClassifier(X, y)
#model = SVClassifier(X, y)
driver = ModelDriver(model)

driver.best_snapshot(dataset_dir_name="oslo_3_month_aggregated_proc")
#model.grid_search()
# driver.retrain()
#driver.std_benchmark()
#driver.take_snapshot("decision-tree")

# Impurity-based feature importances
# display_mdi_feat_importance(model.model, X.columns, "Impurity-based feature importances of RF baseline", "MDI importances2.png")

# SHAP values
# calculate_SHAP(model.model, model.X_train, 'SHAP Feature Importance')

# perm_importance = permutation_importance(model.model, model.X_test, model.y_test,n_repeats=30, random_state=42)
# display_perm_importance(X.columns, perm_importance, "Permutation feature importances of RF baseline", "perm_importance.png")
