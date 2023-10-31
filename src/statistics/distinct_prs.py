import json
import os

import csv

output_file = os.path.join(os.getcwd(), "csv/distinct_prs.csv")


def count_distinct_prs(folder, output_file):
    path = f"../0_data_collection/datasets/{folder}"

    folder_count = 0
    prs = set()

    for subfolder in os.listdir(path):
        subfolder_path = os.path.join(path, subfolder)

        if os.path.isdir(subfolder_path):
            folder_count += 1
            commit_info_path = os.path.join(subfolder_path, "commit_info.json")

            if os.path.isfile(commit_info_path):
                with open(commit_info_path, "r") as commit_info_file:
                    commit_info = json.load(commit_info_file)
                    if "pull request" in commit_info:
                        pr_title = commit_info["pull request"]
                        prs.add(pr_title)

    distinct_pr_count = len(prs)
    folders_to_pr_ratio = round(
        (folder_count / distinct_pr_count if distinct_pr_count > 0 else 0), 2
    )

    with open(output_file, "a", newline="") as csvfile:  # Use "a" to append to the file
        fieldnames = [
            "Dataset",
            "# Folder",
            "# Distinct PRs",
            "Ratio",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Check if the file is empty to write the header only once
        if os.path.getsize(output_file) == 0:
            writer.writeheader()

        writer.writerow(
            {
                "Dataset": folder,
                "# Folder": folder_count,
                "# Distinct PRs": distinct_pr_count,
                "Ratio": folders_to_pr_ratio,
            }
        )


if __name__ == "__main__":
    count_distinct_prs("commit_data", output_file)
    count_distinct_prs("commit_data_removed_empty", output_file)
    count_distinct_prs("commit_data_removed_empty_and_only_comments", output_file)
