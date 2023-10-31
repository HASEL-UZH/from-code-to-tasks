import json
import os


def check_unique_pr_count_equal_window_size(sliding_windows_dataset, window_size):
    window_folders = [
        folder
        for folder in os.listdir(sliding_windows_dataset)
        if os.path.isdir(os.path.join(sliding_windows_dataset, folder))
    ]

    for window_folder in window_folders:
        pr_count = set()
        window_folder_path = os.path.join(sliding_windows_dataset, window_folder)

        commit_folders = [
            folder
            for folder in os.listdir(window_folder_path)
            if os.path.isdir(os.path.join(window_folder_path, folder))
        ]
        for commit_folder in commit_folders:
            commit_folder_path = os.path.join(window_folder_path, commit_folder)
            commit_info_path = os.path.join(commit_folder_path, "commit_info.json")
            if os.path.exists(commit_info_path):
                with open(commit_info_path, "r") as file:
                    commit_info = json.load(file)

                pull_request = commit_info["pull request"]
                pr_count.add(pull_request)
        if len(pr_count) != window_size:
            pass
            return False
        pr_count.clear()
    return True


if __name__ == "__main__":
    pass
    window_size = 10
    folder = "../0_data_collection/datasets/commit_data_sliding_window_10"
    # folder = "../0_data_collection/datasets/commit_data_sliding_window_20"
    # folder = "../0_data_collection/datasets/commit_data_sliding_window_30"
    # repository = 0
    # folder = f"../0_data_collection/datasets/commit_data_sliding_window_per_repository_10/{repository}"
    # folder = f"../0_data_collection/datasets/commit_data_sliding_window_per_repository_20/{repository}"
    # folder = f"../0_data_collection/datasets/commit_data_sliding_window_per_repository_30/{repository}"
    check = check_unique_pr_count_equal_window_size(folder, window_size)
    # print(f"Unique PR count equals window size {repository}: " + str(check))
    print(f"Unique PR count equals window size: " + str(check))
