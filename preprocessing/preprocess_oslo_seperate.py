import pandas as pd
import preprocess as pp

if __name__ == "__main__":
    node_ids = [4143, 4122, 4127, 4147, 4120, 4144, 4125, 4133, 4138, 4121, 4134]

    for node_id in node_ids:
        print(f"Processing node {node_id}")
        df = pd.read_csv(f"./sep_aggregated/{node_id}_3_months_aggregated.csv")

        # Only keep entries where both scnt and rcnt are 1.
        df = df.loc[(df['scnt'] == 1) & (df['rcnt'] == 1)]

        df = pp.remove_outliers_IQR(df, 'rtt')

        # Convert the rtt unit from seconds to milliseconds
        df['rtt'] = df['rtt'].apply(lambda x: pp.s_to_ms(x))

        RTT_THRESHOLD = df["rtt"].quantile(0.90)

        df['is_fault'] = df['rtt'] > RTT_THRESHOLD

        # Ensure 'ts' is a datetime type
        df['ts'] = pd.to_datetime(df['ts'])
		
        df = pp.filter_radio_conn_data(df)

        df = pp.drop_useless_columns(df)

        df = pp.create_rtt_means(df)

        df = pp.add_day_and_hour(df)

        df.dropna(inplace=True)

        # Finally we can properly convert the categorical data
        df = pp.one_hot_encode(df, ['node_id', 'weekday'], ['hour', 'weekday'])

        # Save the processed dataset for later
        df.to_csv(f"./3_month_data/{node_id}_3_months_aggregated_proc.csv", index=False)