import os
import pickle

directory_path = 'merged-clstr-data/2023-09-11/17-15-19'  # Replace with the path to your directory

# Check if the specified directory exists
if os.path.exists(directory_path) and os.path.isdir(directory_path):
    # List all files in the directory
    files = os.listdir(directory_path)
    print(files)
    # Iterate through the files
    for filename in files:

       # if filename.endswith('.pickle'):  # Check if the file is a pickle file
        pickle_file_path = os.path.join(directory_path, filename)
        print(pickle_file_path) 
        try:
            # Open the pickle file for reading in binary mode
            with open(pickle_file_path, 'rb') as file:
                # Load the data from the pickle file
                loaded_data = pickle.load(file)
                    
                    # Now, 'loaded_data' contains the Python object from the pickle file
                print(f'Reading {filename}:')
                print(loaded_data)
        except Exception as e:
           print(f"Error reading '{filename}': {e}")
else:
    print(f"The directory '{directory_path}' does not exist or is not a directory.")

