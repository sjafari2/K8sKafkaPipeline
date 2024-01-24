import os
import h5py
import csv

# Function to find all .h5 files in a directory and get their lengths
def find_h5_file_lengths(directory):
    h5_file_lengths = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.h5'):
                file_path = os.path.join(root, file)
                try:
                    with h5py.File(file_path, 'r') as h5_file:
                        length = len(h5_file)
                        h5_file_lengths.append((file, length))
                except Exception as e:
                    print(f"Error reading '{file_path}': {e}")

    return h5_file_lengths

# Function to save the results to a CSV file
def save_to_csv(data, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['File', 'Length'])
        csv_writer.writerows(data)

if __name__ == "__main__":
    directory = input("Enter the directory path: ")
    output_file = input("Enter the output CSV file name: ")

    h5_file_lengths = find_h5_file_lengths(directory)

    if h5_file_lengths:
        save_to_csv(h5_file_lengths, output_file)
        print(f"Results saved to {output_file}")
    else:
        print("No .h5 files found in the specified directory.")

