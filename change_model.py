import json
import os
import re


def ast_meta_file_iterator():
    folder_path = "0_data_collection/datasets/commit_data_removed_empty_and_only_comments"

    for root, dirs, files in os.walk(folder_path):
        if root != folder_path:
            subfolder_name = os.path.basename(root)
            subfolder_files = [file for file in files]
            ast_meta_files = [file for file in subfolder_files if file.endswith("_meta_ast.json")]

            json_dict = {}
            processed_files = []

            for ast_meta_file in ast_meta_files:
                file_name = re.match(r'[^_]+', ast_meta_file).group(0)
                if file_name in processed_files:
                    continue
                # Check if the corresponding _before_meta_ast.json or _after_meta_ast.json exists
                before_file = f"{file_name}_before_meta_ast.json"
                after_file = f"{file_name}_after_meta_ast.json"

                json_tuple = ()
                if before_file in ast_meta_files and after_file in ast_meta_files:
                    # Both before and after files exist, load their JSON data into a tuple
                    with open(os.path.join(folder_path, subfolder_name, before_file), 'r') as before_file_obj:
                        before_json = json.load(before_file_obj)
                    with open(os.path.join(folder_path, subfolder_name, after_file), 'r') as after_file_obj:
                        after_json = json.load(after_file_obj)
                    json_tuple = (before_json, after_json)
                else:
                    # Only one of before or after files exist, load the available JSON data
                    if before_file in ast_meta_files:
                        with open(os.path.join(folder_path, subfolder_name, before_file), 'r') as before_file_obj:
                            json_tuple = (json.load(before_file_obj),None)
                    elif after_file in ast_meta_files:
                        with open(os.path.join(folder_path, subfolder_name, after_file), 'r') as after_file_obj:
                            json_tuple = (None,json.load(after_file_obj))
                processed_files.append(file_name)
                key = len(json_dict)
                json_dict[key] = json_tuple
            # TODO add
            # ast_meta_change_object = create_ast_meta_change_object(json_dict)


def create_change_object(json_dict):
    pass

def create_change_text():
    #Write change object text for each folder i.e. change_text.json
    pass

if __name__ == "__main__":
    #ast_meta_file_iterator()
    create_change_object({0: (None, {
    "type": "compilation-unit",
    "identifier": "Example",
    "children": [
        {
            "type": "package",
            "identifier": "com.iluwatar.presentationmodel",
            "children": [
                {
                    "type": "class",
                    "identifier": "PresentationTest",
                    "UID": "PresentationTest",
                    "children": [
                        {
                            "type": "method",
                            "identifier": "testCreateAlbumList",
                            "UID": "PresentationTest/testCreateAlbumList",
                            "fingerprint": "f4e1ea8a22f2b2094c4e6b0e9bbb80e7ceb9fea4af330b7a1f49c31592f30243"
                        },
                        {
                            "type": "method",
                            "identifier": "testSetSelectedAlbumNumber_1",
                            "UID": "PresentationTest/testSetSelectedAlbumNumber_1",
                            "fingerprint": "59588d13af4ed7bef5c40e494905b9073527064ec3305b8d554d59eb0c93d513"
                        },
                        {
                            "type": "method",
                            "identifier": "testSetSelectedAlbumNumber_2",
                            "UID": "PresentationTest/testSetSelectedAlbumNumber_2",
                            "fingerprint": "df8e75348dc678706b4df3b1c1f02b95f49a88f5c41d09f57584e1e7dc89da64"
                        },
                        {
                            "type": "method",
                            "identifier": "testSetTitle_1",
                            "UID": "PresentationTest/testSetTitle_1",
                            "fingerprint": "a840b593b936e0e9c065dd4b34048e0db6bb14634f89290622cb58270c5d209c"
                        },
                        {
                            "type": "method",
                            "identifier": "testSetTitle_2",
                            "UID": "PresentationTest/testSetTitle_2",
                            "fingerprint": "5248377eff557ba6a06f46575572ceaeab5fc57d62bb89bfe42531dd63ddf675"
                        },
                        {
                            "type": "method",
                            "identifier": "testSetArtist_1",
                            "UID": "PresentationTest/testSetArtist_1",
                            "fingerprint": "a98f20ce643328c81bbd161c115cb49c2ab6dc997a003eae83a109d7408f78e6"
                        },
                        {
                            "type": "method",
                            "identifier": "testSetArtist_2",
                            "UID": "PresentationTest/testSetArtist_2",
                            "fingerprint": "055185f8de5d3dffb3f702c251fad1ca51153737d072df72f461d27dad0a644a"
                        },
                        {
                            "type": "method",
                            "identifier": "testSetIsClassical",
                            "UID": "PresentationTest/testSetIsClassical",
                            "fingerprint": "f3c260091811524660a54e0f4b81009d6a19f85cf4fabbb92422bda58c52287d"
                        },
                        {
                            "type": "method",
                            "identifier": "testSetComposer_false",
                            "UID": "PresentationTest/testSetComposer_false",
                            "fingerprint": "41d5a4082b3bcb606e551a2b2abf17cc5e1c9d9c84dc8be014ba2918bdd51d77"
                        },
                        {
                            "type": "method",
                            "identifier": "testSetComposer_true",
                            "UID": "PresentationTest/testSetComposer_true",
                            "fingerprint": "10c7fdc07682cff5dba207429ab8a854a4e5010adb017603ac6f225162b52c35"
                        }
                    ]
                }
            ]
        }
    ]
})})
