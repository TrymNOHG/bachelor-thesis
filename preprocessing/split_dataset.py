# This file is used to create a sub-set of a dataset based on time interval.

import pandas as pd
import os

def split_data_set_by_time(df, days=7):
    """
    This method extracts a subset of a dataframe based on the number of days from the first time.
    """
    df['ts'] = pd.to_datetime(df['ts'])

    earliest_entry = df['ts'].min()
    end_of_time_period = earliest_entry + pd.Timedelta(days=days)
    return df[df['ts'] <= end_of_time_period]


def check_data_is_within_time_interval(df, days=7):
    """
    This method allows a dateframe's range in timestamps to be validated.
    """
    return pd.to_datetime(df['ts'].max()) - pd.to_datetime(df['ts'].min()) <= pd.Timedelta(days=days)


def create_distributed_datasets(dir):
    """
    This method takes all the csv files in a given directory and creates subsets of 2 week intervals for each csv file.
    """
    for filename in os.listdir(dir):
        if filename.endswith('.csv'):
            filepath = os.path.join(dir, filename)
            node_id = filename.split("_")[0]
            df = pd.read_csv(filepath)
            two_week_df = split_data_set_by_time(df, 14)
            two_week_df.to_csv(f"../data/2_week_data/{node_id}_2_week_aggregated_proc.csv", index=False)

def create_centralized_dataset(dir):
    """
    This method takes all the 2 week interval files and created a centralized dataset.
    """
    df = None
    for filename in os.listdir(dir):
        if filename.endswith('.csv'):
            filepath = os.path.join(dir, filename)
            if df is None:
                df = pd.read_csv(filepath)
            else:
                df = pd.concat([df, pd.read_csv(filepath)], ignore_index=True)

    assert df is not None
    node_id_dummies = pd.get_dummies(df['node_id'], prefix="node_id")
    df = pd.concat([df, node_id_dummies], axis=1)
    df = df.drop(columns=['node_id'])
    df.to_csv(dir + "/centralized_2_week_aggregated_proc.csv", index=False)


def check_count_of_entries():
    """
    This method attains the count of the centralized dataset and the sum of the count of the distributed datasets.
    """
    central_count = 0
    dist_count = 0 
    for filename in os.listdir("../data/2_week_data/"):
        if filename.endswith('.csv'):
            filepath = os.path.join("../data/2_week_data/", filename)
            df = pd.read_csv(filepath)
            if filename == "centralized_2_week_aggregated_proc.csv":
                central_count = len(df)
                continue
            else:
                dist_count += len(df)
    return central_count, dist_count

if __name__ == "__main__":
    # create_distributed_datasets("../data/3_month_data/")
    create_centralized_dataset("../data/2_week_data/")
    # print(check_count_of_entries())
    # df = pd.read_csv("../data/2_week_data/centralized_2_week_aggregated_proc.csv")
    # node_id_dummies = pd.get_dummies(df['node_id'], prefix="node_id")
    # df = pd.concat([df, node_id_dummies], axis=1)
    # df = df.drop(columns=['node_id'])
    # df.to_csv("../data/2_week_data/centralized_2_week_aggregated_proc.csv")
    print(check_count_of_entries())
