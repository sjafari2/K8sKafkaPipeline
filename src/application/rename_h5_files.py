import os

def rename_h5_files(directory):
    # Ensure that the directory exists
    if not os.path.exists(directory):
        print(f"The directory '{directory}' does not exist.")
        return

    # List all files in the directory
    files = os.listdir(directory)

    # Iterate through the files and rename H5 files
    for filename in files:
        if filename.endswith(".h5"):
            # Replace underscores with hyphens in the filename
            new_filename = filename.replace("_", "-")

            # Construct the full paths for the old and new filenames
            old_filepath = os.path.join(directory, filename)
            new_filepath = os.path.join(directory, new_filename)

            # Rename the file
            os.rename(old_filepath, new_filepath)

            print(f"Renamed '{filename}' to '{new_filename}'")

if __name__ == "__main__":
    # Specify the directory where the H5 files are located
    directory_path = "./consumer-app-data/Pod_0"

    # Call the function to rename H5 files in the specified directory
    rename_h5_files(directory_path)

