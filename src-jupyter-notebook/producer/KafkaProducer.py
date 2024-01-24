import itertools
import logging
import pandas as pd
from kafka import KafkaProducer
import helper
import helper2
from functools import partial
import os
import time
import glob
import json

class Producer:

    def __init__(self,serveruri) -> None:
        self.topic_methods = {
            "seizure": self.seizure_process,
            "ukrain": self.ukrain_process,
        }

        self.hlpr = helper.Tools()
        self.serializer = helper.Serializer()
        self.producer_bootstrap_servers = json.loads(serveruri[0])
        config = self.hlpr.read_config('producer.properties')
        producer_config_args = {
                'security_protocol': config.get('security.protocol', 'PLAINTEXT'),
                'sasl_mechanism': config.get('sasl.mechanism', 'PLAIN'),
                'sasl_plain_username': config.get('sasl.jaas.config').split('username=')[1].split(' ')[0].replace("\"", "").strip(),
                'sasl_plain_password': config.get('sasl.jaas.config').split('password=')[1].replace("\"", "").replace(";", "").strip(),
        }
        
        additional_args = {'value_serializer': self.serializer.str_serializer, 'acks': 1, 'linger_ms': 100,'compression_type': 'lz4','batch_size': 16384, **producer_config_args}
        # ,'max_request_size':320 * 1024,
        #        }
        # api_version=(2,7,1),
        try:
            self.producer = KafkaProducer(bootstrap_servers=self.producer_bootstrap_servers, **additional_args)
            print("Kafka Producer is running")
        except Exception as ex:
            logging.error('Exception while creating Kafka Producer: ' + str(ex))
            print('Exception while creating Kafka Producer')
            print(str(ex))
    
    def send_message(self, topic, message):
        try:
            self.producer.send(topic, value=message)
            self.producer.flush()
            print(f"Message successfully sent to topic '{topic}'")
        except Exception as e:
            # Log any exceptions that occur during send
            print(f"Error sending message to topic '{topic}': {e}")
 

    def close(self):

        self.producer.close()

    def fetch_files(self,pri,pi,input_path):
        file_names = []
        pattern = f"{input_path}/*-pod-{pi}-prod-{pri}.csv"
        matched_files = glob.glob(pattern)
        file_names.extend(matched_files)
        return file_names



    def stream_data(self,wait_time,topicTitle,**kwargs):
        while True:
            filenames = self.fetch_files(kwargs.get('prodindex'),kwargs.get('podindex'),kwargs.get('inputpath'))
            if filenames:
                process_method = self.topic_methods.get(topicTitle)
                if not process_method:
                    raise ValueError(f"No processing method found for topic: {topicTitle}")
                process_method(filenames, topicTitle, **kwargs)
            else:
                time.sleep(wait_time)  # Sleep for a while before checking again



    def ukrain_process(self, filenames, topicTitle, nprod , num_topics, podindex, prodindex, batchsize, column_range, inputpath):

        sindex = podindex * batchsize * nprod + prodindex * batchsize
        unique_words = set()
        for filename in filenames:
            print("################################################################")
            print(f" File name is {filename}")
            with open(filename, 'r', encoding='utf-8') as f:
                header = f.readline().split(',')
            itr = 0
            key = 0
           # while (True):
            print(f'iteration={itr}')
            itr = itr + 1
            df = pd.read_csv(filename, lineterminator='\n', names=header, header=0, nrows=batchsize, skiprows=sindex, usecols = header, encoding='utf-8')
           # print("df is read")
            if df.shape[0] == 0:
                print('EOF')
                break
                #        start_timestamp = df['timestamp'][0]
                #        producer.send("timestamp" , start_timestamp)
            df['text'] = df['text\n'].apply(lambda x: x.split(' '))
            df['text'] = df['text'].map(lambda x: helper2.cleanHashtags(x))
                # df['text'] = df['text'].map(lambda x: list(filter(lambda y: y != 'vacc' and y != 'vaccination', x)))
            df = df[df['text'].apply(lambda x: len(x) > 1)]
            if df.empty:
                print('Empty DF?')
            else:

                    ## Finding the range of colums for developing CSR matrix
                    #col_range = self.hlpr.findColRange(df)
                
                rangehash = partial(helper2.rangeHash, r = column_range)

                print("start finding word pairs")
                for i in range(len(df)):
                    df['word-pairs_ls'] = list(map(lambda x: list(itertools.permutations(x, r=2)), df['text']))
                df_series = df['word-pairs_ls'].explode().apply(pd.Series)
                df_series.columns = ['word1', 'word2']
                df_series['word1'] = df_series['word1'].map(lambda x: rangehash(x))
                df_series['word2'] = df_series['word2'].map(lambda x: rangehash(x))
                dfResult = df_series.groupby('word1').agg(list).apply(lambda x: list(zip(*x)), axis=1)
                for i in range(dfResult.shape[0]):

                        #producerTimestamp = self.hlpr.TimestampEvent()
                     print('----------------------------------------------------------------')
                     print("Producer is Sending Data")
                     hashTopic = dfResult.index[i]
                     word = helper2.get_word_from_hash(hashTopic)  # Lookup the word from the hash
                     key = hashTopic % num_topics
                     topic = f"{topicTitle}_{key}"#, {word}"
                     print (f" Topic is {topic}, {word}")
                     flat_list = [item for sublist in dfResult.iloc[i] for item in sublist]
                     #dictkey= f"{key}, {word}"                                    #dict_keyi = str(key) + ", " + word
                    # print(f" type word is {type(word)}")
                    # print(f" type dictkey is {type(dictkey)}")
                     #valuedict = {dictkey: flat_list}
                    # valuedict = str({hashTopic: dfResult.iloc[i]})
                     valuedict = str({hashTopic: flat_list})
                     print(f"ValueDict ={valuedict}")

                     # Find the number of unique words in the dictionary including the key
                     # Initialize a set with the key
                     unique_words.add(hashTopic)
                     for value in flat_list:
                         unique_words.add(value)
                     #words_count = len(words_values)  # the word count in each message
                     print(f"Unique words count until now is {len(unique_words)}")
                     #headers = [('words_count', bytes(str(words_count), encoding ='utf-8'))] ## send the word count as header through producer
                     self.send_message(topic, valuedict)
                     print('****************************************************************')
        words_len = len(unique_words)
        print(f" Number of unique words producer sent through Kafka is : {words_len}")
        print(f" Unique words producer sent through Kafka are : {unique_words}")
        os.remove(filename)

    def seizure_process(self, filenames, topicTitle, _range):

        ## Call method for producing fake data and sending it to kafka by producer

        for _ in range(_range):
            message = self.hlpr.produceFakeData()
            self.send_message(topicTitle, message)
        print(f"Done with sending data by producer to topic {topicTitle}")
        self.close()


