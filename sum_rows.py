# Initialize a variable to store the sum of row values
total_sum = 0

# Open the text file for reading
with open('consumer-log.txt', 'r') as file:
    # Iterate through each line in the file
    for line in file:
        # Check if the line contains "Sum of rows in this matrix is"
        if "Sum of rows in this matrix is" in line:
            # Split the line into words and extract the last word (which should be the number)
            words = line.split()
            try:
                # Attempt to convert the last word to an integer and add it to the total_sum
                value = int(words[-1])
                total_sum += value
            except ValueError:
                # Handle the case where the last word is not a valid integer
                print(f"Invalid value found in line: {line}")

# Print the total sum of row values

print(f"Total sum of row values: {total_sum}")
total_sum = 0 
with open ('consumer-sum-rows.txt' ,'r') as f:
    for line in f:
        value = line.split()
        try:
            total_sum += sum(map(int,value))
        except:
            print('Error')

print(f"Total sum is {total_sum}")
