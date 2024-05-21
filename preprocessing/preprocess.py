import pandas as pd 


def filter_interval(df : pd.DataFrame, column : str, lower_bound : int, upper_bound : int) -> pd.DataFrame:
    """
        This function filters a dataframe column to only contain entries between and inclusive of the lower and upper bounds.
    """
    df[column] = df[column].apply(lambda x: int(x))
    df = df.loc[(lower_bound <= df[column]) & (df[column] <= upper_bound)]
    return df


def get_hour_from_data_obj(data : str) -> int:
    """
        This function retrieves the hour from a data object.
    """
    date_obj = pd.to_datetime(data)
    return date_obj.hour


def categorize_column(mapper : dict, val : int) -> str | None:
    mapper = dict(sorted(mapper.items(), key=lambda x:x[1], reverse=True))
    category = None
    for (category, boundary) in mapper.items():
        if (val >= boundary):
            return category
    return category


def s_to_ms(second_data : float) -> float:
    """
        This function converts a data point in seconds to milliseconds.
    """
    return second_data * 10**3


def change_col_type_to_str(df : pd.DataFrame, columns : list) -> pd.DataFrame:
    """
        This function takes a list of columns and converts the values of each column to be of str datatype.
    """
    for col in columns:
        df[col] = df[col].astype(str)
    return df


def get_min_value(tstr):
    """
        Used to get the min value of an event for RSSI or RSRQ or RSRP
    """
    if isinstance(tstr, int):
        return tstr
    nums = tstr.split(" ")
    nums = [float(n) for n in nums]
    return min(nums)


def find_avg_rtt_in_timespan(df, window):
    """
    df: dataframe containing at least ts and rtt.
        It's important that the df only contains row for a single node.
    window: 
        '3s' or '1min' etc ...
    
    """
    df = df.set_index('ts')
    df[f'rtt_{window}_mean'] = df['rtt'].rolling(window).mean()
    # Reset the index if necessary
    df = df.reset_index()
    return df


def shift_fault(df):
    df["is_fault"] = df["is_fault"].shift(-1)
    return df


if __name__ == "__main__":
    df = pd.read_csv("../data/5_nodes_1_week_fault.csv")
    # Drop unwanted columns
    df.drop(columns=['Unnamed: 0', 'network_id', 'service_id'])

    # Only keep entries where both scnt and rcnt are 1.
    df = df.loc[(df['scnt'] == 1) & (df['rcnt'] == 1)]

    # Convert the rtt unit from seconds to milliseconds
    df['rtt'] = df['rtt'].apply(lambda x: s_to_ms(x))

    # Ensure 'ts' is a datetime type
    df['ts'] = pd.to_datetime(df['ts'])

    # Filter away garbage RSSI, RSRQ and RSRP values.
    df['event_rssi'] = df['event_rssi'].apply(lambda val: "".join(char for char in val if char not in "\"(,)"))
    df['event_rsrq'] =df['event_rsrq'].apply(lambda val: "".join(char for char in val if char not in "\"(,)"))
    df['event_rsrp'] = df['event_rsrp'].apply(lambda val: "".join(char for char in val if char not in "\"(,)"))
    df = filter_interval(df, 'bin_rsrp', -140, -44)
    df = filter_interval(df, 'bin_rssi', -100, -6)
    df = filter_interval(df, 'bin_rsrq', -20, -3)
    # Use the smallest RSSI, RSRQ and RSRQ values for each entry
    df['rssi'] = df['bin_rssi'].apply(lambda x: get_min_value(x))
    df['rsrq'] = df['bin_rsrq'].apply(lambda x: get_min_value(x))
    df['rsrp'] = df['bin_rsrp'].apply(lambda x: get_min_value(x))

    # Categorize population
    population_category_mapper = {
        'LOW'    : 15000,
        'MEDIUM' : 30000,
        'HIGH' : 45000
    }
    df['population'] = df['population'].apply(lambda x: categorize_column(population_category_mapper, x)) # Categorize population based on intervals defined in population mapper

    # We can now remove some extra columns
    df = df.drop(columns=["Unnamed: 0", "network_id", "service_id", "scnt", "rcnt", "bin_ts", "event_ts", "event_rssi", "bin_rssi", "event_rsrq", "bin_rsrq", "event_rsrp", "bin_rsrp"])

    df = df.groupby('node_id').apply(lambda group: shift_fault(group)).reset_index(drop=True)
    # Calculate new rtt features.
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "2s")).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "3s")).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "4s")).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "5s")).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "10s")).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "30s")).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "1min")).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "5min")).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "10min")).reset_index(drop=True)

    # Add day-of-week feature
    df['weekday'] = df['ts'].dt.day_name()

    # Only keep hours from timestamp, and make string for categorization later.
    df['ts'] = df['ts'].apply(lambda x: str(get_hour_from_data_obj(x)))
    # Entries made into strings in order to perform one-hot encoding.          
    df = change_col_type_to_str(df, ['node_id', 'weekday'])

    # Finally we can properly convert the categorical data
    df.dropna(inplace=True)

    df = pd.get_dummies(df, columns=['ts', 'population', 'node_id', 'weekday'])

    # Save the processed dataset for later
    df.to_csv("../data/5_nodes_1_week_fault_processed.csv")
