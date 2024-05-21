import pandas as pd
import matplotlib.pyplot as plt

def find_mode_ratios(df):
	mode_counts = df['celevel'].value_counts()
	mode_ratios = mode_counts / mode_counts.sum()
	return mode_ratios

if __name__ == '__main__':
	df = pd.read_csv('time_filtered/metadata_celevel_events.csv')

	df['celevel'].value_counts().plot(kind='bar')

	print(find_mode_ratios(df))
	plt.xlabel("CE Level")
	plt.ylabel("Count")
	plt.title("CE Level distribution")
	plt.show()