import pandas as pd

def filter_time(df, node_ids, start_date, days=7):
	node_df = df[df['node_id'].isin(node_ids)]
	node_df["ts"] = pd.to_datetime(node_df["ts"])
	end_date = pd.to_datetime(start_date) + pd.Timedelta(days=days)
	week_data = node_df[(node_df['ts'] >= start_date) & (node_df['ts'] < end_date)]
	return week_data

if __name__ == "__main__":
	start_date = '2023-11-01'

	node_ids = [4143, 4122, 4127, 4147, 4120, 4144, 4125, 4133, 4138, 4121, 4134]
	df = pd.read_csv("./operator/packetloss_rtt_rawdata_1sec_bins.csv")

	for node in node_ids:

		filtered_df = filter_time(df, node_ids, start_date, time_delta=90)

		filtered_df.to_csv("./operator/node_{node_id}_3_month_packetloss_rtt_rawdata_1sec_bins.csv", index=False)
