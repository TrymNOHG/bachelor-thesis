import pandas as pd
import preprocess as pp

def create_pop_category_dict(keys, values):
    population_categories = dict(zip(keys, values))
    return population_categories

if __name__ == "__main__":
    population_minimas = [21411, 28632, 35107, 42328]

    category_names = ['Low', 'Mid-Low', 'Mid-High', 'High']

    population_categories = create_pop_category_dict(category_names, population_minimas)

    print(population_categories)

    df = pd.read_csv("./oslo_3_month_aggregated.csv")

    population_df = pd.read_csv("./node_uptime_with_population.csv")

    df = df.merge(population_df[['node_id', 'population']], on='node_id')

    print("Merged with population.")

    pp.categorize_population(df, population_categories)

    print("Categorized population.")

    df = df.loc[(df['scnt'] == 1) & (df['rcnt'] == 1)]

    df = pp.remove_outliers_IQR(df, 'rtt')

    print("Removed outliers.")

    df['rtt'] = df['rtt'].apply(lambda x: pp.s_to_ms(x))

    RTT_THRESHOLD = df["rtt"].quantile(0.90)

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

    df = pp.one_hot_encode(df, ['node_id', 'weekday', 'population'], ['population', 'node_id', 'hour', 'weekday'])

    print("Created dummies.")

    df.to_csv("./oslo_3_month_aggregated.csv", index=False)
