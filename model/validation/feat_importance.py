from sklearn.ensemble import RandomForestClassifier
import pandas as pd 
import matplotlib.pyplot as plt
import shap
import numpy as np

def order_features_and_col(feature_importance: list, columns: list, reversed: bool =True) -> list[dict, list]:
    """
    This method takes a list of feature importances and sorts it. It then changes the corresponding array of feature names to match the order of importances.
    """
    feature_importance_dict = {}
    for index, feat in enumerate(feature_importance):
        feature_importance_dict[feat] = index
    
    feature_importance_dict = dict(sorted(feature_importance_dict.items(), reverse=reversed)) # If reversed is True, this will order by highest value first.

    ordered_cols = []

    for new_col_index in feature_importance_dict.values():
        ordered_cols.append(columns[new_col_index])

    return feature_importance_dict, ordered_cols

def bar_graph(indices, cols, dict, title, image_save_path, direction='vertical', save_mode=False, thread_lock=None):
    """
    This method creates a bar graph with focus on feature importance. The option for path to save and direction of the bar graph is available.
    """
    with thread_lock:
        x_label = 'Feature'
        y_label = 'Importance'

        if direction == "horizontal":
            plt.barh(indices, dict.keys())
            plt.gca().invert_yaxis()
            plt.yticks(indices, cols, rotation=direction)
            x_label = 'Importance'
            y_label = 'Feature'
        elif direction == "vertical":
            plt.bar(indices, dict.keys(), orientation='vertical')
            plt.xticks(indices, cols, rotation=direction)
        else:
            raise AttributeError("Invalid direction")
        
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.style.use('tableau-colorblind10')
        plt.tight_layout(pad=2.0, w_pad=1.0, h_pad=1.0)

        if image_save_path is not None:
            plt.savefig(image_save_path)
        if not save_mode:
            plt.show()

        plt.close()


def display_mdi_feat_importance(model: object, columns: list, title: str, image_save_path: str) -> None:
    """
    This method takes in a model, checks for feature importances, orders the list by highest, and display it in a bar graph. The method also has the option
    of saving an image of the bar graph.
    """
    feature_importance = None
    if hasattr(model, 'feature_importances_'):
        feature_importance = model.feature_importances_
    else:
        raise AttributeError("Model does not have feature importances attribute.")
    
    num_x = list(range(len(feature_importance)))
    feature_importance_dict, ordered_cols = order_features_and_col(feature_importance, columns, True)
    bar_graph(num_x, ordered_cols, feature_importance_dict, title, image_save_path, 'vertical')


def display_perm_importance(columns: list, feature_importance: list, title: str, image_save_path: str, save_mode=False) -> None:
    """
    This method takes in a list of feature importance, orders the list by highest, and display it in a bar graph. The method also has the option
    of saving an image of the bar graph. The feature importance should be of type permutation importance.
    """
    sorted_importances_ids = feature_importance.importances_mean.argsort()
    importances = feature_importance.importances[sorted_importances_ids].T

    columns = columns[sorted_importances_ids]
    
    _, ax = plt.subplots()

    ax.boxplot(importances, vert=False, whis=20, labels=columns)
    ax.set_title(title)
    ax.axvline(x=0, color="black", linestyle="--")
    ax.set_xlabel("Variable Importance Score")
    ax.figure.tight_layout()
    if image_save_path is not None:
        ax.figure.savefig(image_save_path)

    if not save_mode:
        plt.show()


def get_SHAP_explainer(model: object) -> shap.Explainer:
    """
    This method generates a SHAP explainer for a given model.
    """
    return shap.TreeExplainer(model) if type(model) == RandomForestClassifier else shap.Explainer(model)
        

def calculate_SHAP(explainer: object, X_test: pd.DataFrame, num_features: int = None, title: str = None, image_save_path: str = None, thread_lock=None) -> None:
    """
    This method calculates the SHAP values for a model using an Explainer object. The feature importances are then displayed in a bar graph.
    """
    if explainer is None:
        raise Exception("Explainer has not been initialized.")
    # expected_value = explainer.expected_value
    shap_vals = explainer(X_test)   
    importances = []
    for i in range(shap_vals.values.shape[1]):
        importances.append(np.mean(np.abs(shap_vals.values[:, i])))
    
    
    columns = X_test.columns.to_list()
    feature_importance_dict, ordered_cols = order_features_and_col(importances, columns, True)
    
    if num_features is not None and 0 < num_features <= len(importances) :
        importances = importances[:num_features]
        feature_importance_dict = {key: feature_importance_dict[key] for key in list(feature_importance_dict)[:num_features]}
        ordered_cols = ordered_cols[:num_features]
    num_x = list(range(len(importances)))

    bar_graph(num_x, ordered_cols, feature_importance_dict, title, image_save_path, 'horizontal', save_mode=True, thread_lock=thread_lock)


def display_dependence_plot(model: object, X_test: pd.DataFrame, feat_1: str, feat_2: str) -> None:
    """
    This method creates a dependence plot based on the SHAP values.
    """
    explainer = shap.Explainer(model)
    shap_vals = explainer.shap_values(X_test)
    shap.dependence_plot(feat_1, shap_vals[0], X_test,feat_2)
