import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def find_ratios(df):
    counts = df['rsrp'].value_counts()
    ratios = counts / counts.sum()
    return ratios

if __name__ == '__main__':
	df = pd.read_csv('time_filtered/metadata_rsrp_events.csv')

	df.sort_values(['node_id', 'ts'], inplace=True)
	df['previous_rsrp'] = df.groupby('node_id')['rsrp'].shift()
	df = df[df['node_id'] == df['node_id'].shift()]
	df['rsrp_switch'] = df['previous_rsrp'].astype(str) + '->' + df['rsrp'].astype(str)

	print("hello")
	rsrp_switch_df = df['rsrp_switch'].str.split('->', expand=True)
	df['previous_rsrp'] = rsrp_switch_df[0].astype(float).astype(int)
	df['next_rsrp'] = rsrp_switch_df[1].astype(float).astype(int)

	print(find_ratios(df))
	pivot_table = df.pivot_table(index='previous_rsrp', columns='next_rsrp', aggfunc='size', fill_value=0)

	plt.figure(figsize=(10, 8))
	sns.heatmap(pivot_table, cmap='YlGnBu')
	plt.title('Heatmap of RSRP Switches')
	plt.xlabel('Next RSRP')
	plt.ylabel('Previous RSRP')
	plt.show()