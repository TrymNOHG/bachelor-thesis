import importlib.metadata
import pandas as pd
from typing import Optional

# You should be running pandas 2.0.3
def print_pandas_version():
    """Prints the pandas version
    """
    version = importlib.metadata.version("pandas")
    print(f"Pandas version {version}")


def series_to_list(column_series: pd.Series) -> tuple:
    """There can be multiple events in one second, use this to map stuff

    Args:
        column_series (pd.Series): A column in the pandas dataframe

    Returns:
        Tuple: Wrapped hashable, needed for pandas to work
    """
    return tuple(column_series.to_list())


def load_event_for_key(folder_name: str, metadata_key: str, event_key: str) -> pd.DataFrame:
    """Method to load event data for a specific key

    Args:
        metadata_key (str): e.g rssi
        event_key (str): e.g event_rssi

    Returns:
        pd.DataFrame: events_rdf
    """
    # Load dataframe
    # Prepare your filtered dataframe this is only example
    # Change string pattern to match your files
    event_rdf = pd.read_csv(
        f"./{folder_name}/metadata_{metadata_key}_events.csv")
    # Convert timestamp to datetime object
    event_rdf["ts"] = pd.to_datetime(event_rdf["ts"])
    # FLOOR timestamp to second frequency for matching (DO NOT USE ROUND!)
    event_rdf["ts"] = event_rdf["ts"].dt.floor(freq="s")
    # Rename columns to event_ts and e.g. rssi to "event_rssi"
    event_rdf.rename(
        columns={"ts": "event_ts", metadata_key: event_key}, inplace=True)
    # Return loaded rdf
    return event_rdf


def merge_events_to_dataframe(
    rtt_1sec: pd.DataFrame, event_rdf: pd.DataFrame, event_key: str, event_count_key: str
) -> pd.DataFrame:
    """Merges the dataframes together using event_ts and node_id, network_id
    Fills blanks with previous value
    Removes leading NA values 

    Args:
        rtt_1sec (pd.DataFrame): dataframe with rtt measurement
        event_rdf (pd.DataFrame): dataframe with events
        event_key (str): e.g: "event_rssi"
        event_count_key (str): e.g. "event_count_rssi"

    Returns:
        pd.DataFrame: dataframe with mapped columns
    """
    # Do left merge
    rtt_1sec_merged = rtt_1sec.copy(deep=True).merge(
        right=event_rdf, on=["event_ts", "node_id", "network_id"], how="left"
    )

    # Fill subsequent values with value (if there is multiple changes, it will fill it with last value
    rtt_1sec_merged[event_key] = rtt_1sec_merged[event_key].fillna(
        method="ffill")

    # Reset index
    rtt_1sec_merged.reset_index(drop=True, inplace=True)
    # Drop leading NA values
    rtt_1sec_merged.dropna(inplace=True)

    # Flat listing of recors if there are two identical rows it will match them and create tupe (first_val,second_val,...)
    # It will also tuple all single values, bins does not have this issue
    rtt_1sec_merged = (
        rtt_1sec_merged.groupby(by=rtt_1sec.columns.to_list(), as_index=False)
        .agg(
            values=pd.NamedAgg(column=event_key, aggfunc=series_to_list),
            count=pd.NamedAgg(column=event_key, aggfunc="count"),
        )
        .reset_index(drop=True)
    )

    # Rename columns to unique names, so you can do this in iterative manner
    rtt_1sec_merged.rename(
        columns={"values": event_key, "count": event_count_key}, inplace=True
    )
    # Reset index for next function
    rtt_1sec = rtt_1sec_merged.reset_index(drop=True)
    # Drop event dataframe you do not need it
    del event_rdf
    # Return value
    return rtt_1sec


def load_bin_for_key(
    folder_name: str, metadata_key: str, bin_key: str
) -> pd.DataFrame:
    """Loads bin file for metadatakey

    Args:
        metadata_key (str): e.g. "rssi"
        bin_key (_type_): e.g "bin_rssi"

    Returns:
        pd.DataFrame: bin_rdf containing 1 minute normalized bins
    """
    # Load file
    # This is example, you may need to change it for your data
    bin_rdf = pd.read_csv(
        f"./{folder_name}/metadata_{metadata_key}_1min_bin.csv")
    # Convert to timestamp
    bin_rdf["ts"] = pd.to_datetime(bin_rdf["ts"])
    # We do not trust data, normalize them
    bin_rdf["ts"] = bin_rdf["ts"].dt.floor(freq="min")
    # Rename ts:bin_ts and e.g. rssi => bin_rssi
    bin_rdf.rename(
        columns={"ts": "bin_ts", metadata_key: bin_key}, inplace=True)
    # Return source data
    return bin_rdf


def merge_bins_to_dataframe(
    rtt_1sec: pd.DataFrame, bin_rdf: pd.DataFrame, bin_key: str
) -> pd.DataFrame:
    """Added "bin_column to dataframe"

    Args:
        rtt_1sec (pd.DataFrame): RTT data
        bin_rdf (pd.DataFrame): BIN data
        bin_key (str): e.g. "bin_rssi"

    Returns:
        pd.DataFrame: RTT data with new bin_key column
    """
    # Left merge
    rtt_1sec_merged = rtt_1sec.merge(
        right=bin_rdf, on=["bin_ts", "node_id", "network_id"], how="left"
    )
    # Fill subsequent values
    rtt_1sec_merged[bin_key] = rtt_1sec_merged[bin_key].fillna(method="ffill")
    # Reset index before drop
    rtt_1sec_merged.reset_index(drop=True, inplace=True)
    # Drop values without bin
    rtt_1sec_merged.dropna(inplace=True)
    # Reset index after drop
    rtt_1sec = rtt_1sec_merged.reset_index(drop=True)
    # Dispose of bins that are already mapped
    del bin_rdf
    # Return new RTT data
    return rtt_1sec


def filter_and_aggregate(
    df: pd.DataFrame, folder_name: str, drop_columns: Optional[list] = ["network_id", "service_id"]
) -> pd.DataFrame:
    """Filter and aggregate the data

    Args:
        df (pd.DataFrame): The pandas dataframe of 1 second RTT data

    Returns: -> pd.DataFrame
        pd.DataFrame: The aggregated dataframe
    """

    df["ts"] = pd.to_datetime(df["ts"])
    df.sort_values(by=["ts"], inplace=True)

    df["bin_ts"] = df["ts"].dt.floor(freq="min")
    df["event_ts"] = df["ts"].dt.floor(freq="s")

    # Specify keys that you want to import (both bins and events)
    # Make sure that you have proper files in proper folder etc.
    for metadata_key in ["rssi", "rsrq", "rsrp"]:
        # Define all keys that are going to extend dataframe in one go
        event_key = f"event_{metadata_key}"
        event_count_key = event_count_key = f"event_count_{metadata_key}"
        bin_key = f"bin_{metadata_key}"

        # Fetch event data
        event_rdf = load_event_for_key(
            folder_name=folder_name, metadata_key=metadata_key, event_key=event_key)
        # Map event data
        df = merge_events_to_dataframe(
            rtt_1sec=df,
            event_rdf=event_rdf,
            event_key=event_key,
            event_count_key=event_count_key,
        )

        # Fetch bin data
        bin_rdf = load_bin_for_key(folder_name=folder_name, metadata_key=metadata_key, bin_key=bin_key)

        # Map bin data
        df = merge_bins_to_dataframe(
            rtt_1sec=df, bin_rdf=bin_rdf, bin_key=bin_key
        )
        print(metadata_key)

    df = df.drop(columns=["bin_ts", "event_ts"])

    if drop_columns:
        df.drop(columns=drop_columns, inplace=True)

    return df
