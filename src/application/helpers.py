import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import numpy as np
from collections import Counter

def buildGraph(edge_list_path, network):
    '''
    Create nx graph from edge list
    '''
    with open(edge_list_path + network + '.tsv') as f:
        edges = f.readlines()
        edges = [tuple(line.strip().split(' ')) for line in edges]
        edges = [(int(x[0]), int(x[1])) for x in edges]

    graph = nx.Graph()
    graph.name = network

    graph.add_edges_from(edges)
    print(nx.info(graph))
    print("Network density:", nx.density(graph))  
    print('')
    return graph


def orderAdjMatrix(graph, fmap):
    nodes = list(graph.nodes)
    nodes = [int(node) for node in nodes]

    order = []
    for ci, cnodes in sorted(fmap.items()):
        for cnode in cnodes:
            order.append(nodes.index(cnode))
        
    matrix = nx.to_numpy_array(graph)[order][:,order]
    x, y = np.argwhere(matrix == 1).T
    
    return matrix, x, y

def drawAdjMatrixPlotly(x,y,title,color='black'):
    
    fig = go.Figure(data=go.Scatter(x=x, y=y, mode='markers'))

    fig.update_traces(mode='markers', marker_line_width=0.05, marker_size=2, marker_color=color)
    fig.update_layout(title=title,
                      yaxis_zeroline=False, 
                      xaxis_zeroline=False,
                      autosize=False,
                      width=700,
                      height=700,
                      plot_bgcolor='rgb(250,250,250)')

    fig.show()
    
def drawAdjMatrixMatplotlib(x,y,title,save_path, save=True, color='black'):
    
    network_name = title.split(': ')[1]
    
    plt.rcParams["figure.figsize"] = (10, 10)
    plt.scatter(x, y, s=0.001, c=color)

    # add title and axis names
    plt.title(title, fontsize=25)
    plt.xlabel('Nodes', fontsize=25)
    plt.ylabel('Nodes', fontsize=25)
   
    if save == True:
        plt.savefig(save_path + network_name + '.png')  
        plt.clf()
        plt.show()
    
    else:
        plt.show()
        
        
# -----------------------------------------------------------------
# CLUSTER ANALYSIS
# -----------------------------------------------------------------

def get_datetime(date):
    month = date.split('-')[0]
    if month == 'jan':
        month = '01'
    elif month == 'feb':
        month = '02'
    elif month == 'mar':
        month = '03'
    elif month == 'apr':
        month = '04'
    elif month == 'may':
        month = '05'
        
    date = month + '-' + date.split('-')[1] + '-2020'
    
    return date

def get_df_for_network(network_name, df):
    network_df = df.loc[df['network'] == network_name]
    return network_df


def get_topic_count(topics_in_cluster):
    topics = Counter(topics_in_cluster).keys() # equals to list(set(words))
    topics = list(topics)
    counts = Counter(topics_in_cluster).values() # counts the elements' frequency
    counts = list(counts)
    topic_count_mapping = list(set(zip(topics,counts)))
    topic_count_mapping = [tup for tup in topic_count_mapping if tup[0] != '[]']
    topic_count_mapping = sorted(topic_count_mapping,key=lambda x: x[1], reverse=True)
    return topic_count_mapping

def get_num_topic_per_cluster(topic_count):
    topics = []
    occurrences = []
    for tup in topic_count:
        topics.append(tup[0])
        occurrences.append(tup[1])
    return topics, occurrences

# ---------------------------------------------------------------------------------------------------

