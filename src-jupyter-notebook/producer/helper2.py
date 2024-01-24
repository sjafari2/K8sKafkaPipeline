import hashlib
import pickle
import nltk
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import plotly.express as px
import spacy
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from preprocess import *

# added stop words
#gist_file = open("data/gist_stopwords.txt", "r")
#try:
#    content = gist_file.read()

#finally:
#    gist_file.close()
# stop words

nlp = spacy.load("en_core_web_sm")
nltk.download('stopwords')
nlp = spacy.load("en_core_web_sm")

# constants
stop_words = list(set(stopwords.words('english')))+list(set(stopwords.words('spanish')))+list(set(stopwords.words('portuguese')))
stop_words.extend(['rt', 'und','many','let','very','from', 'subject', 're', 'edu', 'whole','really',
                   'use', 'amp', 'get', 'go', 'say', 'people', 'need', 'see', 'know', 'make', 'take',
                   'think', 'would', 'still', 'keep', 'may', 'could', 'come','vaccination', 'vaccine', 'vaccines', 'vaccinated'])


with open('./data/rarelist.pkl', 'rb') as f:
    mynewlist = pickle.load(f)
    stop_words.extend(mynewlist)

stop_words = set(stop_words)

#print("Stopwords length = {}".format(len(stop_words)))

# Global dictionary to keep track of word-to-hash mappings
word_hash_map = {}


def get_word_from_hash(hash_value):
    # Inverse lookup in the word_hash_map
    for word, hash_val in word_hash_map.items():
        if hash_val == hash_value:
            return word
    return "Unknown"  # Return "Unknown" if hash not found


def stripStopWords(string):
    if string not in stop_words:
        return string

def removePunctuation(string):
    punctuation = '''!()-[]{}; :'"\,<>./?@#$%^&*_~'''
    for symbol in string:
        if symbol in punctuation:
            string = string.replace(symbol, '')
#         else:
#             string = 'None'
    return string

def lemmatize(string, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    doc = nlp(string)
    return ' '.join([token.lemma_ for token in doc if token.pos_ in allowed_postags])

def stemming(string):
    if string is not None:
        ps = PorterStemmer()
        return ps.stem(string)

def removeDupChars(string):
    string = re.sub(r'(.+?)\1+', r'\1', string)
    return string

def lowercase(string):
    return string.lower()

def deEmojify(string):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F914"             # thinking face emoji 
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)

    return regrex_pattern.sub(r'', string)

def filterHashtag(hashtag):  ### Clean one hashtag
    hashtag = deEmojify(hashtag)
    hashtag = removePunctuation(hashtag)
    hashtag = lowercase(hashtag)
    hashtag = removeDupChars(hashtag)
    hashtag = stripStopWords(hashtag)
    if hashtag == '':
        hashtag = None
#         print(hashtag)
    return hashtag

def cleanHashtags(hashtag_list):

#     hl = []
#     for hashtag in hashtag_list:
#         hashtag = filterHashtag(hashtag)
#         hl.append(hashtag)
#     return hl

#     Clean a list of hashtags
    return list(sorted(filter(bool,map(filterHashtag,hashtag_list))))


def rangeHash(s,r):  ### takes a hashtag and returns hash value
    hash_value = int(hashlib.md5(s.encode('utf8')).hexdigest(),16) % r
    word_hash_map[s] = hash_value
    return hash_value

def orderAdjMatrix(graph, fmap):
    nodes = list(graph.nodes)
    nodes = [int(node) for node in nodes]

    order = []
    for ci, cnodes in sorted(fmap.items()):
        for cnode in cnodes:
            order.append(nodes.index(cnode))

    matrix = nx.to_numpy_array(graph)[order][:,order]
    x, y = np.argwhere(matrix == 1).T

    return matrix, x, y, order

def drawAdjMatrixPlotly(df,title):

    fig = px.scatter(df, x='x', y='y')

    fig.update_traces(mode='markers', marker_size=10, marker_color='black')
    fig.update_layout(yaxis_zeroline=False,
                      xaxis_zeroline=False,
                      xaxis_title='Nodes',
                      yaxis_title='Nodes',
                      autosize=False,
                      width=700,
                      height=700,
                      plot_bgcolor='rgb(255,255,255)')

#     fig.update_layout(title=title,
#                   yaxis_zeroline=False,
#                   xaxis_zeroline=False,
#                   autosize=False,
#                   width=1000,
#                   height=1000,
#                   plot_bgcolor='rgb(250,250,250)')


    fig.show()

def drawAdjMatrixMatplotlib(x,y,title,color='black'):

    network_name = title.split(': ')[1]
    type_fig = title.split(': ')[0]

    if type_fig == 'Clusters before merging fingerprints':
        type_fig = 'before'
    elif type_fig == 'Graph clusters after merging fingerprints':
        type_fig = 'after'
    elif type_fig == 'Unclustered network':
        type_fig = 'unclustered'

    plt.rcParams["figure.figsize"] = (3, 3)
    plt.scatter(x, y, s=1, c=color)

    # add title and axis names
    plt.title(title, fontsize=25)
    plt.xlabel('Nodes', fontsize=25)
    plt.ylabel('Nodes', fontsize=25)

#     plt.savefig('../../../Projects/stream-graph/plots/adjacency_matrices/' + network_name + '_' + type_fig + '.png')
#     plt.savefig('../../../Projects/covid-19/plots/adjacency_matrices_0.1/' + network_name + '_' + type_fig + '.png')
#     plt.clf()
    plt.show()

# ---------------------------------------------------------------------------
# G2 = nx.convert_node_labels_to_integers(G, first_label=0, ordering='default', label_attribute=None)

# communities = algorithms.louvain(G2, weight='weight', resolution=1.)
# clusters = communities.communities
# print('{} clusters found'.format(len(clusters)))

# sizes = []
# for cluster in clusters:
#     cluster_size = len(cluster)
#     sizes.append(cluster_size)

# # visualize ordered matrix
# fmap = defaultdict(list)
# for cluster, node_in_cluster in enumerate(clusters):
#     fmap[cluster] = node_in_cluster

# m, x, y, order = orderAdjMatrix(G2, fmap)

# x_axis = x.tolist()
# y_axis = y.tolist()

# df = pd.DataFrame(list(zip(x_axis, y_axis)), columns =['x', 'y'])
# drawAdjMatrixPlotly(df,'Adjacency matrix ordered')
