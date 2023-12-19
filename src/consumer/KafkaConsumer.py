'''
@author: Soheila
'''
from kafka import KafkaConsumer
from kafka.structs import TopicPartition
import helper
import logging
import numpy as np
import time
import itertools
import json
import pickle

class Consumer:
    def __init__(self,serveruri,pod_index):

        #self.row_sums = []  # Initialize an empty list to store row sums
        #self.total_sum = 0  # Initialize the total sum
        self.consumer_methods = {
            "seizure": self.seizure_consume,
            "ukrain": self.ukrain_consume,
        }
        # Define Variables
        self.serializer = helper.Serializer()
        self.hlpr = helper.Tools()
        self.bootstrap_servers = ["pipe-kafka.kafkastreamingdata.svc.cluster.local:9092"]
       # self.bootstrap_servers = serveruri[0].strip('["]')
        #print(f"type uri is {type(self.bootstrap_servers)}")
        #print(f" Consumer URIs are {self.bootstrap_servers}")
        config = self.hlpr.read_config('consumer.properties')
        consumer_config_args = {
            'security_protocol': config.get('security.protocol', 'PLAINTEXT'),
            'sasl_mechanism': config.get('sasl.mechanism', 'PLAIN'),
            'sasl_plain_username': config.get('sasl.jaas.config').split('username=')[1].split(' ')[0].replace("\"", "").strip(),
            'sasl_plain_password': config.get('sasl.jaas.config').split('password=')[1].replace("\"", "").replace(";", "").strip(),
        }

        additional_args = {'value_deserializer':self.serializer.str_deserializer,
                #'max_partition_fetch_bytes':320 * 1024,  # Set the maximum partition fetch bytes to 320 KB
                #'fetch_max_bytes':320 * 1024,  # Set the maximum fetch bytes to 320 KB
                'enable_auto_commit': True,
                'auto_offset_reset' : "latest",
                'api_version':(0,10),
                'group_id' : "pip-validate",
                #max_in_flight_requests_per_connection =  flight_req,
                'auto_commit_interval_ms' : 5000,
                **consumer_config_args
                  }
        try:
            self.consumer = KafkaConsumer(bootstrap_servers = self.bootstrap_servers,**additional_args)
        except Exception as ex:
            logging.error('Exception while creating Kafka Consumer: ' + str(ex))
            print('Exception while creating Kafka Consumer')
            print(str(ex))

    def subscribe_to_topics(self, topics):
        try:
            self.consumer.subscribe(topics)
            #print(f" Subscribed to Topic {topic} Successfully")
        except Exception as ex:
            print(str(ex))
            return

    def poll(self,timeout_ms,max_records):
        try:
            message = self.consumer.poll(timeout_ms,max_records)
            #print("Message Polled Successfully")
            return message
        except Exception as ex:
            print(str(ex))
            return


    def assign_to_topic(self, topic):
        try:
            partitions = self.consumer.partitions_for_topic(topic)
            if not partitions:
                print(f"No partition for Topic {topic}!")
                return
            else:
                #print(f"partitions are {partitions}")
                self.consumer.assign([TopicPartition(topic,p) for p in partitions])

        except Exception as ex:
            print(str(ex))
            return
   
    def close(self):
        self.consumer.close()


    def consume_stream(self,topicTitle, topics, **kwargs):
        try:
            self.subscribe_to_topics(topics)
            #print(f"Topic is {topic}")
            # assign customer to toipics
           # self.assign_to_topic(topics)
            #self.consumer.seek_to_end()
            unique_rows = set()
            unique_columns = set()
            row_sums_array = []  # Initialize a local variable as an empty list
            total_sum = 0  # Initialize a local variable for total sum
            row_sums_dict = {}
            itr = 1
            while True:
                 msg = self.poll(5000,1000)
                 if not msg.items():
                    if itr == 1:
                                          
                        print("No New message")
                        print("Let's see the results until now")
                        # Convert row_sums_dict into an array
                        unique_row_indices = sorted(unique_rows)
        
                        row_sums_array = np.array([row_sums_dict[r] for r in unique_row_indices])

                        # Calculate the sum of all row sums
                        total_sum = np.sum(row_sums_array)


                        print(f"Sum of values in each row: {row_sums_array}")
                        print(f"Total Sum of all Rows: {total_sum}")

                        if (len(unique_rows)==len(unique_columns)):
                            print(f" List of unique words are {unique_rows}")
                            print(f" Final number of unique words is {len(unique_rows)}")
                        else:
                            print(f" Number of unique words in rows  {len(unique_rows)}")
                            print(f" Number of unique words in columns is {len(unique_columns)}")
                            if (len(unique_rows)>len(unique_columns)):                          
                                print(f" unique rows - unique columns are {unique_rows-unique_columns}")
                            elif (len(unique_columns)> len(unique_rows)):
                                print(f" unique columns - unique rows  are {unique_columns-unique_rows}")

                    else:
                        sleep_time = 10 * itr
                        print("Let's wait for new messages")
                        print(f"I am going to sleep for {sleep_time} seconds")
                        time.sleep(sleep_time)
                        itr = itr +1
                        continue

                 elif 'error' in msg:
                     print("Error in getting data by kafka consumer")
                     print(f"msg['error']")
                     continue
                 else:
                     itr = 1
                     consume_method = self.consumer_methods.get(topicTitle)
                     if not consume_method:
                        raise ValueError(f"No processing method found for topic: {topicTitle}")
                    
                     consume_method(msg,unique_rows,unique_columns, row_sums_dict, **kwargs)
               
        except Exception as ex:
            print(f"Can't poll due to exception : {ex}")
            pass


    def ukrain_consume(self,msg,unique_rows,unique_columns, row_sums_dict, col_range,pod_index,cindex,file_path):
        row = []
        col = []
        data = []
        np.set_printoptions(threshold=np.inf)
        catched = dropped = laged = 0
        for tp,ms in msg.items(): ## ms is a list
            for m in ms: ## m is a consumer record and m.value is a dictionary
                msg_value = eval(m.value)
                print(f" message value is {msg_value}")
                msgkey = list(msg_value.keys())[0]
               # print(f" type msgvalue is {type(msg_value)}")
               # print(f" msg key is {msgkey}")
                unique_rows.add(msgkey)
                msglst = msg_value[msgkey]
               # print(f"message list is {msglst}")
               # print(f" type msglist is {type(msglst)}")
               # lst = list(itertools.chain.from_iterable(msglst))
               # print(f" type list is {type(lst)}") 
                if isinstance(msglst, list):
                    for index, value in enumerate(msglst):
                        col.append(value)
                        row.append(msgkey)
                        unique_columns.add(value)
                        data.append(1)
                        catched = catched + 1

                        #droped = droped+1
                    # print(f"Number of catched messages are {catched}")
                else:
                    print(f"Skipping non-iterable element: {msglst}")
        filename = "consumer-"+str(cindex)+"-pod-"+str(pod_index)
        print(f"Number of unique words until this itration is {len(unique_rows)}")
       # print(f"Number of unique words in columns until this itration is {len(unique_columns)}")
        # Calculate the sum of values in each row using the provided code snippet
        for r, d in zip(row, data):
            if r not in row_sums_dict:
                row_sums_dict[r] = 0    
            row_sums_dict[r] += d
                        
        try:
            self.hlpr.save_matrix(filename, file_path, col, row, data, col_range)
            print("Done with writing a CSR matrix")
        except Exception as ex:
            print(str(ex))

      



############ Consuming Methods for Seizure Detection Project    ############

    def process_seizure_message(self,message):
        msgvalue = eval(message.value)
        if isinstance(msgvalue, dict):
            fake_data = msgvalue.get('fake_data')
            timestamp = msgvalue.get('timestamp')
        # Access the fake data and timestamp
            if fake_data is not None and timestamp is not None:
                #print(f"Fake data: {fake_data}")
                #print(f"Timestamp: {timestamp}")
                return fake_data,timestamp
        print("Invalid message format or missing values")
        return None, None

    def seizure_consume(self,topic,message,cal_closedTime):
        closedloopTimes, data = [], []
        for tp,ms in message.items():
            for m in ms:
                fake_data , timestamp = self.process_seizure_message(m)
                #Timestamps.append(timestamp)
                data.append(fake_data)
                if cal_closedTime:
                    # Access the clock object properties or methods
                    clock = helper.Clock(timestamp)
                    elapsed_time = clock.get_elapsed_time() * 1000000
                    print(f"Time passed: {elapsed_time} nano seconds")
                    closedloopTimes.append(elapsed_time)
        return data , closedloopTimes

