import os
import re
import shutil

# Define the directory where your files are located
source_directory = './consumer-app-data/Pod_0/processed'

# Define the naming pattern and extract numbers before ".h5"
pattern = "consumer-1-pod-0_(\d+)_\d+\.h5"
matching_files = []

for filename in os.listdir(source_directory):
    if filename.endswith(".h5"):
        match = re.match(pattern, filename)
        if match:
            number = int(match.group(1))
            matching_files.append((filename, number))

# Sort the matching files by the extracted number in descending order
matching_files.sort(key=lambda x: x[1], reverse=True)

# Select the last 144 files
selected_files = matching_files[:33]
# Print matched files for debugging
for filename, _ in matching_files:
    print(f"Matched file: {filename}")

# Define the destination directory where you want to move the files
destination_directory = './consumer-app-data/Pod_0/result2'

# Create the destination directory if it doesn't exist
if not os.path.exists(destination_directory):
    os.makedirs(destination_directory)

# Move the selected files to the destination directory
for filename, _ in selected_files:
    source_path = os.path.join(source_directory, filename)
    destination_path = os.path.join(destination_directory, filename)
    
    # Move the file
    shutil.move(source_path, destination_path)
    print(f"Moved {filename} to {destination_directory}")

# Now you can read the selected files or perform any additional actions

