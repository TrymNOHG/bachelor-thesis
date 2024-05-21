import pandas as pd
import preprocess as pp

if __name__ == "__main__":
    sec_df = pd.read_csv("./sep_aggregated/4144_3_months_aggregated.csv")

    pp.remove_outliers_IQR(sec_df, 'rtt')

    RTT_THRESHOLD = sec_df['rtt'].quantile(0.90) * 1000

    print(RTT_THRESHOLD)

    intervals = [2, 3, 4, 5, 10, 15, 30, 60]

    for interval in intervals:
        print(f"Processing interval {interval}")
        df = pd.read_csv(f"./interval_aggregated/4144_interval_{interval}_3_months_aggregated.csv")

        # Only keep entries where both scnt and rcnt are 1.
        df = df.loc[(df['scnt'] == 1) & (df['rcnt'] == 1)]

        df = pp.remove_outliers_IQR(df, 'rtt')

        # Convert the rtt unit from seconds to milliseconds
        df['rtt'] = df['rtt'].apply(lambda x: pp.s_to_ms(x))

        df['is_fault'] = df['rtt'] > RTT_THRESHOLD

        # Ensure 'ts' is a datetime type
        df['ts'] = pd.to_datetime(df['ts'])

        df = pp.filter_radio_conn_data(df)

        df = pp.drop_useless_columns(df)

        df = pp.create_rtt_means(df, interval)

        df = pp.add_day_and_hour(df)

        df.dropna(inplace=True)

        # Finally we can properly convert the categorical data
        df = pp.one_hot_encode(df, ['node_id', 'weekday'], ['hour', 'weekday'])

        # Save the processed dataset for later
        df.to_csv(f"./interval_data/4144_interval_{interval}_3_months_aggregated_proc.csv", index=False)