# Number of folders (number of commits)
# Total number of commit_info.json files
# Total number of .diff files
# Total number of before.java files
# Total number of after.java files
# Total number of .java files

# Minimum number of before.java files in a subfolder
# Minimum number of after.java files in a subfolder
# Minimum number of .java files in a subfolder
# Minimum number of .java files in a subfolder

# Maximum number of before.java files in a subfolder
# Maximum number of after.java files in a subfolder
# Maximum number of .java files in a subfolder
# Maximum number of .java files in a subfolder

# Mean number of before.java files over all subfolders
# Mean number of after.java files over all subfolders
# Mean number of .java files over all subfolders
# Mean number of .diff files over all subfolders

# Median number of before.java files over all subfolders
# Median number of after.java files over all subfolders
# Median number of .java files over all subfolders
# Median number of .diff files over all subfolders

import os

import csv


def create_repository_statistics(folder):
    path = f"../0_data_collection/datasets/{folder}"
    output_file = os.path.join(os.getcwd(), f"csv/dataset_statistics.csv")

    extensions_count = {
        "commits": 0,
        ".diff": 0,
        "before.java": 0,
        "after.java": 0,
        ".java": 0,
    }

    min_counts = {
        "commit_info.json": float("inf"),
        "before.java": float("inf"),
        "after.java": float("inf"),
        ".java": float("inf"),
        ".diff": float("inf"),
    }

    max_counts = {
        "commit_info.json": 0,
        "before.java": 0,
        "after.java": 0,
        ".java": 0,
        ".diff": 0,
    }

    counts = {
        "commit_info.json": [],
        "before.java": [],
        "after.java": [],
        ".java": [],
        ".diff": [],
    }

    for subfolder in os.listdir(path):
        subfolder_path = os.path.join(path, subfolder)

        if os.path.isdir(subfolder_path):
            files = os.listdir(subfolder_path)
            extension_counts = {ext: 0 for ext in extensions_count}

            for file in files:
                for ext in extensions_count:
                    extension_counts[ext] += 1

            for ext, count in extension_counts.items():
                extensions_count[ext] += count
                counts[ext].append(count)
                if count < min_counts[ext]:
                    min_counts[ext] = count
                if count > max_counts[ext]:
                    max_counts[ext] = count

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = [
            "Repository",
            "#Commits",
            "#Added files",
            "#Removed files",
            "#Modified files",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        def write_row(statistic, value):
            writer.writerow(
                {
                    "Repository": folder,
                    "Statistic": statistic,
                    "Value": round(value, 2),
                }
            )


if __name__ == "__main__":
    create_repository_statistics("commit_data")
    create_repository_statistics("commit_data_removed_empty")
    create_repository_statistics("commit_data_removed_empty_and_only_comments")
