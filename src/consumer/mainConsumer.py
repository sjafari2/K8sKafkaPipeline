import KafkaConsumer
import sys
import pandas as pd
import argparse

if __name__ == '__main__':
    ## Get Input Values ##
    print("Start getting variables")
    parser = argparse.ArgumentParser("Run kafka Consumer")
    pd.set_option('display.max_colwidth', None)
    parser.add_argument('-topics', '--topics', nargs = '+' , dest = 'topics', help = 'Topics Assigned to the Cosnumer', required = True, metavar='TOPICS')
    parser.add_argument('-topictitle', '--topictitle', type = str , dest = 'topictitle', help = 'Topic Title assigned to this project', required = True, metavar='TOPICTITLE')
    parser.add_argument('-consindex', '--consindex', type = int, dest='consindex', help ='The Index of Consumers in Consumer Pod', default=0, metavar='CONSINDEX')
    parser.add_argument('-hpath', '--h5pypath', type = str, dest='h5pypath', help ='The path of h5 files', default='./consumer-app-data', metavar='H5PYPATH')
    parser.add_argument('-colrange', '--colrange', type = int, dest='colrange', help ='The Range of Columns in the CSR Matrix', default=500000, metavar='COLRANGE')
    parser.add_argument('-pi', '--podindex', type = int, dest='podindex', help ='The Pod Index', default=0, metavar='PODINDEX')
    parser.add_argument('-uris', '--server_uris',  nargs = '+' ,  dest = 'server_uris', help = 'KAFKA CONSUMER SERVER URIs', default= '127.0.0.1:9092', metavar='KAFKA CONSUMER SERVER URIs')
    args = parser.parse_args(sys.argv[1:])
    topics = args.topics
    topicTitle = args.topictitle
    pod_index = args.podindex
    col_range = args.colrange
    file_path = args.h5pypath
    cons_index = args.consindex
    print(f" topics are {topics}")
    ## Create a Consumer Object ##
    consumer = KafkaConsumer.Consumer(args.server_uris, pod_index)

    ## Call Consumer Consume Stream Method ##
    consumer.consume_stream(topicTitle=topicTitle, topics=topics, file_path=file_path, col_range=col_range, pod_index=pod_index, cindex=cons_index)
