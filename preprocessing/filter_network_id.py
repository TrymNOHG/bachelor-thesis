import os
import pandas as pd
from tqdm import tqdm

CHUNK_SIZE = 1000000

EXCLUDE_FILE_PATH = 'operator/'


def get_filenames(folder_path):
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return []

    all_filenames = os.listdir(folder_path)

    exclude_filenames = os.listdir(EXCLUDE_FILE_PATH)

    all_filenames = [
        filename for filename in all_filenames if filename not in exclude_filenames]

    return all_filenames


def filter_csv(input_file):
    for chunk in (tqdm(pd.read_csv(input_file, chunksize=CHUNK_SIZE), desc=f"Processing {os.path.basename(input_file)}")):
        mask = (chunk["network_id"] == 2)

        chunk = chunk[mask]

        chunk.to_csv('operator/' + input_file.split('/')
                     [1], index=False,  mode='a')


if __name__ == '__main__':
    files = get_filenames("data")
    for file in files:
        filter_csv('data/' + file)
