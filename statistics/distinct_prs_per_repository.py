import json
import os

import csv

output_file = os.path.join(os.getcwd(), "csv/distinct_prs_per_repository.csv")


def count_distinct_prs_per_repository(folder, output_file):
    path = f"../0_data_collection/datasets/{folder}"

    repositories = {
        "0": {"folder_count": 0, "prs": set()},
        "1": {"folder_count": 0, "prs": set()},
        "2": {"folder_count": 0, "prs": set()},
        "3": {"folder_count": 0, "prs": set()},
        "4": {"folder_count": 0, "prs": set()},
        "5": {"folder_count": 0, "prs": set()},
        "6": {"folder_count": 0, "prs": set()},
        "7": {"folder_count": 0, "prs": set()},
        "8": {"folder_count": 0, "prs": set()},
        "9": {"folder_count": 0, "prs": set()},
    }

    for subfolder in os.listdir(path):
        subfolder_path = os.path.join(path, subfolder)

        if os.path.isdir(subfolder_path):
            repository = subfolder[7]
            repositories[repository]["folder_count"] += 1
            commit_info_path = os.path.join(subfolder_path, "commit_info.json")

            if os.path.isfile(commit_info_path):
                with open(commit_info_path, "r") as commit_info_file:
                    commit_info = json.load(commit_info_file)
                    if "pull request" in commit_info:
                        pr_title = commit_info["pull request"]
                        repositories[repository]["prs"].add(pr_title)

    for repository in repositories:
        repositories[repository]["distinct_pr_count"] = len(
            repositories[repository]["prs"]
        )
        ratio = (
            repositories[repository]["folder_count"]
            / repositories[repository]["distinct_pr_count"]
            if repositories[repository]["distinct_pr_count"] > 0
            else 0
        )
        repositories[repository]["folders_to_pr_ratio"] = round(ratio, 2)

    with open(output_file, "a", newline="") as csvfile:  # Use "a" to append to the file
        fieldnames = [
            "Dataset",
            "Repository",
            "# Folder",
            "# Distinct PRs",
            "Ratio",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Check if the file is empty to write the header only once
        if os.path.getsize(output_file) == 0:
            writer.writeheader()

        for repository in repositories:
            writer.writerow(
                {
                    "Dataset": folder,
                    "Repository": repository,
                    "# Folder": repositories[repository]["folder_count"],
                    "# Distinct PRs": repositories[repository]["distinct_pr_count"],
                    "Ratio": repositories[repository]["folders_to_pr_ratio"],
                }
            )


if __name__ == "__main__":
    count_distinct_prs_per_repository("commit_data", output_file)
    count_distinct_prs_per_repository("commit_data_removed_empty", output_file)
    count_distinct_prs_per_repository(
        "commit_data_removed_empty_and_only_comments", output_file
    )
