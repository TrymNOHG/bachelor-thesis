import csv
import os
from dataclasses import dataclass


@dataclass
class Snapshot:
    filename: str
    month: str
    day: int
    model_name: str
    data: dict[str, float]


def parse_snapshot(filename):
    data = {}
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header row
        for row in reader:
            key = row[0]
            try:
                value = float(row[1])
            except ValueError:
                value = row[1]
            data[key] = value
    return data


def parse_all_snapshots(directory) -> list[Snapshot]:
    snapshots: list[Snapshot] = []
    for filename in os.listdir(directory):
        if not filename.endswith(".csv"):
            continue

        file_path = os.path.join(directory, filename)
        data = parse_snapshot(file_path)

        # Parse filename.
        # Should be on format: day-month-model-type.csv
        name, _ = filename.split(".")
        name_data = name.split("-")
        day = int(name_data[0])
        month = name_data[1]
        model_name = "-".join(name_data[2:])

        snapshot: Snapshot = Snapshot(filename, month, day, model_name, data)
        snapshots.append(snapshot)

    return snapshots

