import csv, os, json
import time as timer
import hdf5
import math
from datetime import datetime
from scipy.sparse import csr_matrix


class Clock:
    def __init__(self, startTime):
        self.start_time = startTime

    def get_elapsed_time(self):
        current_time = timer.time()
        elapsed_time = current_time - self.start_time
        return elapsed_time


class Tools:
    def __init__(self):
        pass

    def read_config(self, filepath):
        with open(filepath, 'r') as f:
            lines = f.readlines()

        config = {}
        for line in lines:
            key, value = line.strip().split('=', 1)
            config[key] = value

        return config

    @staticmethod
    def save_csv(file_, filename):
        with open(filename + '.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([filename])
            writer.writerows([[row] for row in file_])

    @staticmethod
    def save_matrix(self, filename, filepath, col, row, data,col_range):
        row_range = max(col+row)+1
        print(f" Row range is {row_range}")
        os.makedirs(filepath,exist_ok=True)
        matrix = csr_matrix((data,(row,col)),shape=(row_range,col_range))
        extension = 'lck'
        hdf5.csr2h5py(matrix , filepath+'/'+filename,extension)
        os.rename(filepath+'/'+filename+'.'+extension,filepath+'/'+filename+'.h5')

    def produceFakeData(self):
        # Create Faker object
        # self.faker = Faker()

        # Create Clock object
        clock = Clock(startTime=0)  # Create an instance of the Clock class

        current_time = clock.get_elapsed_time()  # Get the current time
        # Generate a fake sample of 16 bits (2 bytes)
        random_bytes = os.urandom(2)

        # Convert the random bytes to an integer
        fake_data = int.from_bytes(random_bytes, byteorder='big')

        # Create a message including timestamp and fake data
        message = {'fake_data': fake_data, 'timestamp': current_time}
        # message = f"{fake_data},{clock}"

        return message

    def fakeML(self, data):
        start_time = timer.time()  # Start the timer

        # Perform your machine learning operations on the fake_data
        # Simple Example: # Sleep for 1 millisecond

        timer.sleep(0.001)
        end_time = timer.time()  # Stop the timer
        timestamp = end_time - start_time  # Calculate the duration

        return timestamp, data

    def findColRange(self,df):
        df['word'] = df['text'].apply(lambda x: x.split(' '))
        x=df['word'].tolist()
        pdf_flat=[item for sublist in x for item in sublist]
        len_pdf_flat=(len(list(set(pdf_flat))))
        digits = int(math.log10(len_pdf_flat))+1
        print(len_pdf_flat)
        col_row=1
        print(digits)
        for i in range(digits):
            col_row=col_row * 10
        return col_row

    def TimestampEvent(self):
        return (datetime.timestamp(datetime.now()))

class Serializer:
    def __init__(self):
        pass

    def str_serializer(self,value):
        if value is None:
            return None
        try:
            return str(value).encode('utf-8')
        except Exception as ex:
            print(f"Error is {ex}")
            return None
    def str_deserializer(self,value):
        if value is None:
            return None
        try:
            return value.decode('utf-8')
        except Exception as ex:
            print(f"Error is {ex}")
            return None

    def jsonSerializer(self, value):
        if value is None:
            return None
        try:
            return json.dumps(str(value)).encode('utf-8')
        except Exception as ex:
            print(f"Error is {ex}")
            return None

    def jsonDeserializer(self, value):
        if value is None:
            return None
        try:
            return json.loads(value.decode('utf-8'))
        except Exception as ex:
            print(f"Error is {ex}")
            return None
