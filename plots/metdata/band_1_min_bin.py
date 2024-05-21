import pandas as pd
import matplotlib.pyplot as plt

def find_ratios(df):
	counts = df['band'].value_counts()
	ratios = counts / counts.sum()
	return ratios

if __name__ == '__main__':
	df = pd.read_csv('time_filtered/metadata_band_1min_bin.csv')

	df['band'].value_counts().plot(kind='bar')

	print(find_ratios(df))
	plt.xlabel("Band")
	plt.ylabel("Count")
	plt.title("Mode distribution")
	plt.show()