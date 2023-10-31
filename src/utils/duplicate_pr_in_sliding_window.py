import json
import os


def check_duplicate_pr_in_sliding_window(folder):
    duplicates_dict = {}

    for root, dirs, files in os.walk(folder):
        for sliding_window_folder in dirs:
            sliding_window_path = os.path.join(root, sliding_window_folder)
            pr_count = {}

            # Iterate through subfolders inside the sliding window folder
            for subroot, subdirs, subfiles in os.walk(sliding_window_path):
                for subfolder in subdirs:
                    subfolder_path = os.path.join(subroot, subfolder)
                    commit_info_path = os.path.join(subfolder_path, "commit_info.json")

                    if os.path.exists(commit_info_path):
                        with open(commit_info_path, "r") as file:
                            commit_info = json.load(file)

                        pull_request = commit_info["pull request"]
                        if pull_request in pr_count:
                            pr_count[pull_request] += 1
                        else:
                            pr_count[pull_request] = 1
            pass
            pr_count = {key: value for key, value in pr_count.items() if value != 1}
            if len(pr_count) > 0:
                duplicates_dict[sliding_window_folder] = pr_count

    return duplicates_dict


if __name__ == "__main__":
    pass
    # folder = "0_data_collection/datasets/commit_data_sliding_window_10"
    # folder = "0_data_collection/datasets/commit_data_sliding_window_20"
    folder = "0_data_collection/datasets/commit_data_sliding_window_test_10"
    duplicates = check_duplicate_pr_in_sliding_window(folder)
    print("Duplicates object: " + str(duplicates))
    print("Number of duplicates object: " + str(len(duplicates)))
    # ------------------------------------------------------------------------------------------------
    # folder = "0_data_collection/datasets/commit_data_sliding_window_10_per_repository"
    # folder = "0_data_collection/datasets/commit_data_sliding_window_20_per_repository"
    # folder = "0_data_collection/datasets/commit_data_sliding_window_30_per_repository"
    # duplicates_per_repository = {}
    # for repository in os.listdir(folder):
    #     duplicates_in_repository = check_duplicate_pr_in_sliding_window(
    #         os.path.join(folder, repository)
    #     )
    #     duplicates_per_repository[repository] = duplicates_in_repository
    # print("Duplicates object for all repositories: " + str(duplicates_per_repository))
    # for repository in os.listdir(folder):
    #     print(
    #         f"Duplicates object in {repository}: "
    #         + str(duplicates_per_repository[repository])
    #     )
    #     print(
    #         f"Number of duplicates objects in {repository}: "
    #         + str(len(duplicates_per_repository[repository]))
    #     )
