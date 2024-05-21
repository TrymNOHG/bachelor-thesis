import pandas as pd
import matplotlib.pyplot as plt

def find_mode_ratios(df):
	mode_counts = df['mode'].value_counts()
	mode_ratios = mode_counts / mode_counts.sum()
	return mode_ratios

if __name__ == '__main__':
	df = pd.read_csv('time_filtered/metadata_mode_1min_bin.csv')

	df['mode'].value_counts().plot(kind='bar')

	print(find_mode_ratios(df))
	plt.xlabel("Mode")
	plt.ylabel("Count")
	plt.title("Mode distribution")
	plt.show()