import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def find_ratios(df):
    counts = df['rssi'].value_counts()
    ratios = counts / counts.sum()
    return ratios

if __name__ == '__main__':
	df = pd.read_csv('time_filtered/metadata_rssi_events.csv')

	df.sort_values(['node_id', 'ts'], inplace=True)
	df['previous_rssi'] = df.groupby('node_id')['rssi'].shift()
	df = df[df['node_id'] == df['node_id'].shift()]
	df['rssi_switch'] = df['previous_rssi'].astype(str) + '->' + df['rssi'].astype(str)

	print("hello")
	rssi_switch_df = df['rssi_switch'].str.split('->', expand=True)
	df['previous_rssi'] = rssi_switch_df[0].astype(float).astype(int)
	df['next_rssi'] = rssi_switch_df[1].astype(float).astype(int)

	print(find_ratios(df))
	pivot_table = df.pivot_table(index='previous_rssi', columns='next_rssi', aggfunc='size', fill_value=0)

	plt.figure(figsize=(10, 8))
	sns.heatmap(pivot_table, cmap='YlGnBu')
	plt.title('Heatmap of RSSI Switches')
	plt.xlabel('Next RSSI')
	plt.ylabel('Previous RSSI')
	plt.show()