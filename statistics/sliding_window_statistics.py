import json
import os
import statistics

import csv


def calculate_temporal_proximity(commit_dates):
    temporal_distances = []

    if len(commit_dates) > 1:
        temporal_distances.extend(
            abs(
                (date2[2] - date1[2]) * 365
                + (date2[1] - date1[1]) * 30
                + (date2[0] - date1[0])
            )
            for date1, date2 in zip(commit_dates, commit_dates[1:])
        )

    if temporal_distances:
        min_proximity = min(temporal_distances)
        max_proximity = max(temporal_distances)
        mean_proximity = sum(temporal_distances) / len(temporal_distances)
        median_proximity = statistics.median(temporal_distances)
        stdev_proximity = statistics.stdev(temporal_distances)
    else:
        min_proximity = 0
        max_proximity = 0
        mean_proximity = 0
        median_proximity = 0
        stdev_proximity = 0

    return (
        min_proximity,
        max_proximity,
        mean_proximity,
        median_proximity,
        stdev_proximity,
    )


def count_distinct_prs_per_repository(folder, output_file):
    path = f"../0_data_collection/datasets/{folder}"

    sliding_window_count = 0

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = [
            "#Windows",
            "Min Proximity",
            "Max Proximity",
            "Mean Proximity",
            "Median Proximity",
            "Standard Deviation Proximity",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for sliding_window in os.listdir(path):
            sliding_window_count += 1
            subfolder_path = os.path.join(path, sliding_window)
            commit_dates = []

            for item in os.listdir(subfolder_path):
                item_path = os.path.join(subfolder_path, item)

                # Check if the item is a directory before processing
                if os.path.isdir(item_path):
                    commit_info_path = os.path.join(item_path, "commit_info.json")

                    with open(commit_info_path, "r") as json_file:
                        commit_info = json.load(json_file)
                        committer_date = commit_info.get("committer date")

                        if committer_date:
                            # Assuming committer_date is a list [day, month, year]
                            commit_dates.append(committer_date)

            (
                min_proximity,
                max_proximity,
                mean_proximity,
                median_proximity,
                stdev_proximity,
            ) = calculate_temporal_proximity(commit_dates)

            writer.writerow(
                {
                    "#Windows": sliding_window_count,
                    "Min Proximity": min_proximity,
                    "Max Proximity": max_proximity,
                    "Mean Proximity": mean_proximity,
                    "Median Proximity": median_proximity,
                    "Standard Deviation Proximity": stdev_proximity,
                }
            )


if __name__ == "__main__":
    output_file = os.path.join(os.getcwd(), "csv/sliding_window_statistics.csv")
    count_distinct_prs_per_repository("commit_data_sliding_window", output_file)
