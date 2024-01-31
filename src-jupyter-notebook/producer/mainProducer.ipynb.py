## This is the Main Function to Call Producer ##
import KafkaProducer
import sys
import pandas as pd
import argparse

if __name__ == '__main__':
    ## Get Input Values ##
    pd.set_option('display.max_colwidth', None)
    parser = argparse.ArgumentParser("Run kafka Producers")
    parser.add_argument('-topicTitle', '--topicTitle', type=str, dest='topicTitle', help='Kafka Topic Title', default='test', metavar='KAFKATOPICTITLE')
    parser.add_argument('-np', '--nprod', type=int, dest='nprod', help='Number of Producers in each Producer Pod', default=1,metavar='NPRODUCERS')
    parser.add_argument('-nt', '--ntopics', type=int, dest='ntopics', help='The Number of Topics', default=10, metavar='NTOPICS')
    parser.add_argument('-pi', '--podindex', type=int, dest='podindex', help='Producer Pod Ordinal Number', default=0, metavar='PODINDEX')
    parser.add_argument('-pri', '--prodindex', type=int, dest='prodindex', help='Producer Index', default=0, metavar='PRODUCERINDEX')
    parser.add_argument('-inputpath', '--inputpath', type=str, dest='inputpath', help='Producer Input Path', default="/data", metavar='PRODUCERINPUTPATH')
    parser.add_argument('-bs', '--bsize', type=int, dest='bsize', help='Batch Size', default=100, metavar='BATCHSIZE')
    parser.add_argument('-wtime', '--wtime', type = int, dest='wtime', help='Wait Time', default='10', metavar='WAITTIME')
    parser.add_argument('-cr', '--colrange', type = int, dest='colrange', help ='The Range of Columns in the CSR Matrix', default=500000, metavar='COLRANGE')
    parser.add_argument('-uris', '--uris', nargs = '+', dest='uris', help='Kafka Producer URIs', default='127.0.0.1:9092', metavar='SERVERURIs')
    args = parser.parse_args(sys.argv[1:])
    podindex = args.podindex
    nprod = args.nprod
    ntopics = args.ntopics
    prodindex = args.prodindex
    batchsize = args.bsize
    inputpath = args.inputpath
    serveruris = args.uris
    wtime = args.wtime
    title = args.topicTitle
    column_range = args.colrange

    ## Create a Producer Object
    producer = KafkaProducer.Producer(serveruris)

    ## Call Producer Process Data Method to Produce Streaming Data  ##
    producer.stream_data(wtime,title, nprod=nprod, num_topics=ntopics,podindex=podindex,prodindex=prodindex,batchsize=batchsize,column_range=column_range, inputpath=inputpath)

