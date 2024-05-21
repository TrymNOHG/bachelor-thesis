import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def find_ratios(df):
    counts = df['rsrq'].value_counts()
    ratios = counts / counts.sum()
    return ratios

if __name__ == '__main__':
	df = pd.read_csv('time_filtered/metadata_rsrq_events.csv')

	df.sort_values(['node_id', 'ts'], inplace=True)
	df['previous_rsrq'] = df.groupby('node_id')['rsrq'].shift()
	df = df[df['node_id'] == df['node_id'].shift()]
	df['rsrq_switch'] = df['previous_rsrq'].astype(str) + '->' + df['rsrq'].astype(str)

	print("hello")
	rsrq_switch_df = df['rsrq_switch'].str.split('->', expand=True)
	df['previous_rsrq'] = rsrq_switch_df[0].astype(float).astype(int)
	df['next_rsrq'] = rsrq_switch_df[1].astype(float).astype(int)

	print(find_ratios(df))
	pivot_table = df.pivot_table(index='previous_rsrq', columns='next_rsrq', aggfunc='size', fill_value=0)

	plt.figure(figsize=(10, 8))
	sns.heatmap(pivot_table, cmap='YlGnBu')
	plt.title('Heatmap of RSRQ Switches')
	plt.xlabel('Next RSRQ')
	plt.ylabel('Previous RSRQ')
	plt.show()