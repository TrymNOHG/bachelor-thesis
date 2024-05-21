import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def find_ratios(df):
    counts = df['band'].value_counts()
    ratios = counts / counts.sum()
    return ratios

if __name__ == '__main__':
	df = pd.read_csv('time_filtered/metadata_band_events.csv')

	df.sort_values(['node_id', 'ts'], inplace=True)
	df['previous_band'] = df.groupby('node_id')['band'].shift()
	df = df[df['node_id'] == df['node_id'].shift()]
	df['band_switch'] = df['previous_band'].astype(str) + '->' + df['band'].astype(str)

	band_switch_df = df['band_switch'].str.split('->', expand=True)
	df['previous_band'] = band_switch_df[0].astype(float).astype(int)
	df['next_band'] = band_switch_df[1].astype(float).astype(int)

	pivot_table = df.pivot_table(index='previous_band', columns='next_band', aggfunc='size', fill_value=0)

	plt.figure(figsize=(10, 8))
	sns.heatmap(pivot_table, cmap='YlGnBu')
	plt.title('Heatmap of Band Switches')
	plt.xlabel('Next Band')
	plt.ylabel('Previous Band')
	plt.show()