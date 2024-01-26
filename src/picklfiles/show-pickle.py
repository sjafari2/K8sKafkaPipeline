import os
import pickle

parent_directory = 'merged-clstr-data'  

# Recursively search for pickle files within the parent directory
for root, _, files in os.walk(parent_directory):
    for filename in files:
        if filename.endswith('.pickle'):  # Check if the file is a pickle file
            pickle_file_path = os.path.join(root, filename)
            file_size = os.path.getsize(pickle_file_path)  # Get the file size in bytes
            print(f'File: {pickle_file_path}, Size: {file_size} bytes') 
            
            try:
                
                with open(pickle_file_path, 'rb') as file:
                    # Load the data from the pickle file
                    loaded_data = pickle.load(file)
                    print(f'Reading {filename}:')
                    print(loaded_data)
            except Exception as e:
                print(f"Error reading '{filename}': {e}")

