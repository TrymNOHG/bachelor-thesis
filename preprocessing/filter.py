import os
import pandas as pd
from tqdm import tqdm
from collections import defaultdict

CHUNK_SIZE = 1000000

EXCLUDE_FILE_PATH = 'operator_filtered/'

def get_filenames(folder_path):
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return []

    all_filenames = os.listdir(folder_path)

    exclude_filenames = os.listdir(EXCLUDE_FILE_PATH)

    all_filenames = [
        filename for filename in all_filenames if filename not in exclude_filenames]

    return all_filenames


def find_bad_time_periods(input_file):
    df = pd.read_csv(input_file)

    bad_periods = []
    node_dict = defaultdict(list)

    for _, row in tqdm(df.iterrows(), desc=f"Processing {os.path.basename(input_file)}"):
        event_type = row["mode"]
        node_id = row["node_id"]
        timestamp = row["ts"]

        if event_type == 0 and not node_dict[node_id]:
            node_dict[node_id].append((timestamp, "start"))
        elif event_type == 6 and node_dict[node_id]:
            start_time, _ = node_dict[node_id].pop()
            bad_periods.append({"node_id": node_id, "start_time": start_time, "end_time": timestamp})

    return bad_periods


def filter_csv(input_file, bad_periods):
    for chunk in pd.read_csv(input_file, chunksize=CHUNK_SIZE):
        for period in tqdm(bad_periods, desc=f"Processing {os.path.basename(input_file)}"):
            mask = (
                (chunk["node_id"] == period["node_id"])
                & (chunk["ts"] >= period["start_time"])
                & (chunk["ts"] < period["end_time"])
            )
            chunk = chunk[~mask]

        chunk.to_csv('time_filtered/' + input_file.split('/')
                    [1], index=False,  mode='a')

if __name__ == '__main__':
    files = get_filenames("operator")
    bad_time_periods = find_bad_time_periods('operator/metadata_mode_events.csv')
    for file in files:
        filter_csv('operator/' + file, bad_time_periods)
