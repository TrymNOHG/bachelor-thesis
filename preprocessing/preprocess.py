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


def categorize_column(mapper : dict, val : int):
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


def find_avg_rtt_in_timespan(df, window, multiplier=1):
    """
    df: dataframe containing at least ts and rtt.
        It's important that the df only contains row for a single node.
    window: 
        '3s' or '1min' etc ...
    
    """
    df = df.set_index('ts')
    if multiplier != 1:
        if 'min' in window:
            new_window = int(window.replace('min', '')) * multiplier
            window = f'{new_window}min'
        if 's' in window:
            new_window = int(window.replace('s', '')) * multiplier
            window = f'{new_window}s'

    df[f'rtt_{window}_mean'] = df['rtt'].rolling(window).mean()
    
    # Reset the index if necessary
    df = df.reset_index()
    return df
    

def shift_fault(df):
    df["is_fault"] = df["is_fault"].shift(-1)
    return df

def remove_outliers_IQR(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
            
    df_filtered = df[(df[column] > lower_bound) & (df[column] < upper_bound)]
    return df_filtered


def filter_radio_conn_data(df):
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
    return df


def categorize_population(df, population_dict):
    df['population'] = df['population'].apply(lambda x: categorize_column(population_dict, x))
    return df


def create_rtt_means(df, multiplier=1):
    df = df.groupby('node_id').apply(lambda group: shift_fault(group)).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "2s", multiplier)).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "3s", multiplier)).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "4s", multiplier)).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "5s", multiplier)).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "10s", multiplier)).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "30s", multiplier)).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "1min", multiplier)).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "5min", multiplier)).reset_index(drop=True)
    df = df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "10min", multiplier)).reset_index(drop=True)
    return df


def add_day_and_hour(df):
    df['weekday'] = df['ts'].dt.day_name()
    df['hour'] = df['ts'].apply(lambda x: str(get_hour_from_data_obj(x)))
    return df


def drop_useless_columns(df):
    df = df.drop(columns=["scnt", "rcnt", "event_rssi", "bin_rssi", "event_rsrq", "bin_rsrq", "event_rsrp", "bin_rsrp", "event_count_rssi", "event_count_rsrq", "event_count_rsrp"])
    return df


def one_hot_encode(df, str_cols, dummy_cols):
    df = change_col_type_to_str(df, str_cols)
    df = pd.get_dummies(df, columns=dummy_cols)
    return df