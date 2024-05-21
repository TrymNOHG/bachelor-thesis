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
	band_switch_counts = df['band_switch'].value_counts()
	band_switch_counts.plot(kind='bar')
	plt.xlabel('Band Switch')
	plt.ylabel('Count')
	plt.title('Distribution of Band Switches')
	plt.show()
