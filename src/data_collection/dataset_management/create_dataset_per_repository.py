import os
import shutil


def create_dataset_per_repository(input_dir, output_dir):
    # Iterate through subfolders in the input directory
    for subfolder in os.listdir(input_dir):
        subfolder_path = os.path.join(input_dir, subfolder)

        # Check if the subfolder is a directory
        if os.path.isdir(subfolder_path):
            # Extract the key (a number between 0 and 9) from the folder name
            try:
                key = int(subfolder[7])  # Assuming the key is always at index 7
            except (ValueError, IndexError):
                # Handle cases where the key extraction fails
                key = None

            if key is not None and 0 <= key <= 9:
                # Create the corresponding subfolder in the output directory
                output_subfolder = os.path.join(output_dir, str(key))

                # Ensure the output subfolder exists or create it
                os.makedirs(output_subfolder, exist_ok=True)

                # Copy the subfolder from the input to the output directory
                shutil.copytree(
                    subfolder_path, os.path.join(output_subfolder, subfolder)
                )


if __name__ == "__main__":
    input_directory = "../../datasets/commit_data_removed_empty_and_only_comments"
    output_directory = "../../datasets/commit_data_per_repository"
    create_dataset_per_repository(input_directory, output_directory)
