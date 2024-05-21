import pandas as pd
import preprocess as pp

if __name__ == "__main__":

    df = pd.read_csv("./sep_aggregated/4120_3_months_aggregated.csv")

    df2 = pd.read_csv("./sep_aggregated/4144_3_months_aggregated.csv")

    df.loc[(df['scnt'] == 1) & (df['rcnt'] == 1)]

    df2.loc[(df2['scnt'] == 1) & (df2['rcnt'] == 1)]

    df2 = pp.remove_outliers_IQR(df2, 'rtt')

    df = pp.remove_outliers_IQR(df, 'rtt')

    print("Removed outliers.")

    df['rtt'] = df['rtt'].apply(lambda x: pp.s_to_ms(x))

    df2['rtt'] = df2['rtt'].apply(lambda x: pp.s_to_ms(x))

    RTT_THRESHOLD = df2["rtt"].quantile(0.90)

    df['is_fault'] = df['rtt'] > RTT_THRESHOLD

    print("Added fault.")

    df['ts'] = pd.to_datetime(df['ts'])

    df = pp.filter_radio_conn_data(df)

    print("Fixed radio values.")

    df = pp.drop_useless_columns(df)

    df = pp.create_rtt_means(df)

    print("Created RTT means.")

    df = pp.add_day_and_hour(df)

    print("Added day and hour.")

    df.dropna(inplace=True)

    df = pp.one_hot_encode(df, ['node_id', 'weekday'], ['node_id', 'hour', 'weekday'])

    print("Created dummies.")

    df.to_csv("./4120_3_months_4144_threshold.csv", index=False)
