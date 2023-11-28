# Function to read and parse a text file with comma-separated integers
def read_and_parse_txt_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
        integers = [int(x.strip()) for x in content.split(',') if x.strip().isdigit()]
    return set(integers)

# Read and parse the content of the two text files
file2_integers = read_and_parse_txt_file('number-words-consumer.txt')
file1_integers = read_and_parse_txt_file('number-words-producer.txt')

# Count the number of unique integers in each file
num_unique_integers_file1 = len(file1_integers)
num_unique_integers_file2 = len(file2_integers)

# Find numbers in file1 that are not in file2
numbers_only_in_file1 = file1_integers - file2_integers

# Find numbers in file2 that are not in file1

numbers_only_in_file2 = file2_integers - file1_integers
# Find the set of different integers between the two files
different_integers = file1_integers.symmetric_difference(file2_integers)

# Display the results
print(f"Number of unique words produced by producer: {num_unique_integers_file1}")
print(f"Number of unique words consumed by consumer: {num_unique_integers_file2}")
#print(f"Different integers between the two files: {list(different_integers)}")
if numbers_only_in_file1:
    print(f"Numbers in producer log file that are not in consumer log file: {list(numbers_only_in_file1)}")
else:
    print("There are no words in producer log file that are not in consumer log.")

if numbers_only_in_file2:
    print(f"Numbers in consumer log file  that are not in producer log file: {list(numbers_only_in_file2)}")
else:
    print("There are no words in consumer log file that are not in producer log file.")
