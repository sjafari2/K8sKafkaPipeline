import glob
import h5py
import csv
import os
# Function to find all .h5 files in a directory and get their dimensions
def find_h5_file_dimensions(directory):
    h5_file_dimensions = []

    # Use glob to find all .h5 files in the directory
    h5_files = glob.glob(os.path.join(directory, '**', '*.h5'), recursive=True)
    print(f" H5 files are {h5_files}")
    for file_path in h5_files:
        try:
            with h5py.File(file_path, 'r') as h5_file:
                for dataset_name in h5_file:
                    dataset = h5_file[dataset_name]
                    if isinstance(dataset, h5py.Dataset):
                        rows, cols = dataset.shape
                        h5_file_dimensions.append((file_path, dataset_name, rows, cols))
        except Exception as e:
            print(f"Error reading '{file_path}': {e}")

    return h5_file_dimensions

# Function to save the results to a CSV file
def save_to_csv(data, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['File', 'Dataset', 'Rows', 'Columns'])
        csv_writer.writerows(data)

if __name__ == "__main__":
    directory = input("Enter the directory path: ")
    output_file = input("Enter the output CSV file name: ")

    h5_file_dimensions = find_h5_file_dimensions(directory)
    print(h5_file_dimensions)
    if h5_file_dimensions:
        save_to_csv(h5_file_dimensions, output_file)
        print(f"Results saved to {output_file}")
    else:
        print("No .h5 files found in the specified directory.")

