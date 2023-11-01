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

class Consumer:
    def __init__(self,serveruri):

        self.consumer_methods = {
            "seizure": self.seizure_consume,
            "ukrain": self.ukrain_consume,
        }
        # Define Variables
        self.serializer = helper.Serializer()
        self.hlpr = helper.Tools()
        self.bootstrap_servers = ["pipeline-kafka.kafkastreamingdata.svc.cluster.local:9092"]
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
                'group_id' : "StreamData",
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

    def subscribe_to_topic(self, topic):
        try:
            self.consumer.subscribe([topic])
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
        while True:
            for topic in topics:
                print(f"Topic is {topic}")
                ## assign customer to topics
                self.assign_to_topic(topic)
                self.consumer.seek_to_end()
                try:
                    msg = self.poll(5000,1000)
                    if not msg.items():
                        print("No New message")
                        time.sleep(5)
                        continue

                    if 'error' in msg:
                        print("Error in getting data by kafka consumer")
                        print(f"msg['error']")
                        continue
                    consume_method = self.consumer_methods.get(topicTitle)
                    if not consume_method:
                        raise ValueError(f"No processing method found for topic: {topicTitle}")
                    
                    consume_method(msg, **kwargs)
               
                except Exception as ex:
                    print(f"Can't poll due to exception : {ex}")
                    pass


    def ukrain_consume(self,msg,col_range,pod_index, cindex, file_path):
        row = []
        col = []
        data = []
        np.set_printoptions(threshold=np.inf)
        catched = dropped = laged = 0
        for tp,ms in msg.items(): ## ms is a list
            for m in ms: ## m is a consumer record and m.value is a dictionary
                msg_value = eval(m.value)
                #print(f" message value is {msg_value}")
                msgkey = list(msg_value.keys())[0]
                msglst = msg_value[msgkey]
                print(f"message list is {msglst}")
                lst = list(itertools.chain.from_iterable(msglst))
                for index, value in enumerate(lst):
                    col.append(value)
                    row.append(msgkey)
                    data.append(1)
                    catched = catched + 1
                    #droped = droped+1
        print(f"Number of catched messages are {catched}")
        filename = "consumer-"+str(cindex)+"-pod-"+str(pod_index)
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

