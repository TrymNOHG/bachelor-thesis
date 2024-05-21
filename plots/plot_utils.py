import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from matplotlib.ticker import FormatStrFormatter
from typing import Optional, Callable


OutlierMethodType = Callable[[pd.DataFrame, str], pd.DataFrame]


def remove_outliers_IQR(df: pd.DataFrame, column: str) -> pd.DataFrame:
	"""
	Remove outliers from a DataFrame using the IQR method.

	Parameters
	----------
	df : pd.DataFrame
		The DataFrame containing the data.
	column : str
		The name of the column to filter.

	Returns
	-------
	pd.DataFrame
		The filtered DataFrame.
	"""
	Q1 = df[column].quantile(0.25)
	Q3 = df[column].quantile(0.75)
	IQR = Q3 - Q1
	lower_bound = Q1 - 1.5 * IQR
	upper_bound = Q3 + 1.5 * IQR
    
	print(f"Lower Bound: {lower_bound}, Upper Bound: {upper_bound}")
	    
	df_filtered = df[(df[column] > lower_bound) & (df[column] < upper_bound)]
	return df_filtered


def remove_outliers_sigma_3(df: pd.DataFrame, column: str) -> pd.DataFrame:
	"""
	Remove outliers from a DataFrame using the Z-score method (sigma 3).

	Parameters
	----------
	df : pd.DataFrame
		The DataFrame containing the data.
	column : str
		The name of the column to filter.

	Returns
	-------
	pd.DataFrame
		The filtered DataFrame.
	"""
	z_scores = stats.zscore(df[column])
      
	df_filtered = df[(np.abs(z_scores) < 3)]
	
	return df_filtered


def plot_box(df: pd.DataFrame, column: str, node_id: Optional[int] = None, 
             outlier_method: OutlierMethodType = None, 
             title: Optional[str] = None, unit: str = "units") -> None:
	"""
	Display a box plot for a specified column in the DataFrame
	for a specified node or for all nodes, with optional outlier removal.

	Parameters
	----------
	df : pd.DataFrame
		The DataFrame containing the data.
	column : str
		The name of the column to box plot for.
	node_id : Optional[int]
		The node ID to filter the data by. If None, data for all nodes is used.
	outlier_method : Optional[OutlierMethodType]
		A function that removes outliers from the data based on the specified column.
		If None, no outlier removal is performed.
	title : Optional[str]
		The title of the plot. If None, a default title is generated.
	unit : str
		The unit of the data, used in the axis label. Defaults to "units".

	Returns
	-------
	None
	"""
	get_plot_box(df=df, column=column, node_id=node_id, outlier_method=outlier_method, title=title, unit=unit)
	plt.show()

def get_plot_box(df: pd.DataFrame, column: str, node_id: Optional[int] = None, 
             outlier_method: OutlierMethodType = None, 
             title: Optional[str] = None, unit: str = "units") -> None:
	"""
	Display a box plot for a specified column in the DataFrame
	for a specified node or for all nodes, with optional outlier removal.

	Parameters
	----------
	df : pd.DataFrame
		The DataFrame containing the data.
	column : str
		The name of the column to box plot for.
	node_id : Optional[int]
		The node ID to filter the data by. If None, data for all nodes is used.
	outlier_method : Optional[OutlierMethodType]
		A function that removes outliers from the data based on the specified column.
		If None, no outlier removal is performed.
	title : Optional[str]
		The title of the plot. If None, a default title is generated.
	unit : str
		The unit of the data, used in the axis label. Defaults to "units".

	Returns
	-------
	None
	"""
	if node_id is None:
		node_df = df
		node_id = "All nodes"
	else:
		node_df = df[df["node_id"] == node_id]

	if outlier_method is not None:
		df_filtered = outlier_method(node_df, column)
	else:
		df_filtered = node_df
    
	fig = plt.figure(figsize=(10, 6))
	sns.boxplot(y=df_filtered[column])
    
	plt.title(f"Boxplot of {title} for Node {node_id}")
	plt.ylabel(f"{title} ({unit})")
	plt.xlabel("Node ID")
	plt.gca().yaxis.set_major_formatter(FormatStrFormatter(f"%.1f {unit}"))
    
	plt.tight_layout()
	return fig



def plot_cdf(df: pd.DataFrame, column: str, node_id: Optional[int] = None, 
            outlier_method: OutlierMethodType = None, 
			title: Optional[str] = None, unit: str = "units", save: str = None) -> None:
	"""
	Display a Cumulative Distribution Function (CDF) plot for a specified column in the DataFrame
	for a specified node or for all nodes, with optional outlier removal.

	Parameters
	----------
	df : pd.DataFrame
		The DataFrame containing the data.
	column : str
		The name of the column to plot the CDF for.
	node_id : Optional[int]
		The node ID to filter the data by. If None, data for all nodes is used.
	outlier_method : Optional[OutlierMethodType]
		A function that removes outliers from the data based on the specified column.
		If None, no outlier removal is performed.
	title : Optional[str]
		The title of the plot. If None, a default title is generated.
	unit : str
		The unit of the data, used in the axis label. Defaults to "units".

	Returns
	-------
	None
	"""
	if title is None:
		title = f"CDF of {column}"

	if node_id is not None:
		node_df = df[df["node_id"] == node_id]
		node_label = f"Node {node_id}"
	else:
		node_df = df
		node_label = "All nodes"

	if outlier_method is not None:
		df_filtered = outlier_method(node_df, column)
	else:
		df_filtered = node_df

	data_sorted = np.sort(df_filtered[column].dropna())
	cdf = np.arange(1, len(data_sorted)+1) / len(data_sorted)

	plt.figure(figsize=(10, 6))
	plt.plot(data_sorted, cdf, marker=".", linestyle="none")
	plt.title(f"{title} - {node_label}")
	plt.xlabel(f"{column} ({unit})")
	plt.ylabel("CDF")
	plt.gca().xaxis.set_major_formatter(FormatStrFormatter("%.2f " + unit))
	plt.grid(True)
	if save is not None:
		plt.savefig(save)
	plt.show()