import pandas as pd
import matplotlib.pyplot as plt

def find_ratios(df):
    counts = df['rssi'].value_counts()
    ratios = counts / counts.sum()
    return ratios

if __name__ == '__main__':
    df = pd.read_csv('time_filtered/metadata_rssi_1min_bin.csv')

    df['rssi'].plot(kind='hist', bins=20, rwidth=0.9, color='#607c8e')

    print(find_ratios(df))
    plt.xlabel("RSSI (dB)")
    plt.ylabel("Count")
    plt.title("RSSI distribution")
    plt.grid(axis='y', alpha=0.75)
    plt.show()