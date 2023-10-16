import os
import json


def traverse_and_collect_pull_request_titles(root_folder):
    # List to store pull request titles
    pull_request_titles = []

    # Traverse through folders in the root folder
    for folder_name in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder_name)
        if os.path.isdir(folder_path):
            commit_data_json_path = os.path.join(folder_path, 'commit_info.json')
            if os.path.isfile(commit_data_json_path):
                # Read commit info and retrieve pull request title
                with open(commit_data_json_path, 'r') as json_file:
                    data = json.load(json_file)
                    pull_request = data.get('pull request')
                    if pull_request:
                        pull_request_titles.append(pull_request)

    return pull_request_titles


if __name__ == '__main__':
    commit_data_folder = '../commit_data_removed_empty_and_only_comments'

    pull_request_titles = traverse_and_collect_pull_request_titles(commit_data_folder)

    for index, title in enumerate(pull_request_titles, start=1):
        print(title)
