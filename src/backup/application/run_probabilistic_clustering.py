from find_probabilistic_clusters import *
import sys
from timeit import default_timer as timer
import argparse
from reader import *
import cdlib
from cdlib import evaluation


# ------------------------------------------------------------------------------------------------------------
# PARSE ARGUMENTS

parser = argparse.ArgumentParser()
parser.add_argument('-n', required=True)                   # network
parser.add_argument('-t1', required=True, type=float)      # first threshold
parser.add_argument('-t2', required=True, type=float)      # second threshold
parser.add_argument('-sim1', required=True)                # first threshold metric
parser.add_argument('-sim2', required=True)                # second threshold metric

args = parser.parse_args()

network = args.n
t1 = args.t1
t2 = args.t2

sim1=args.sim1
sim2=args.sim2

# ------------------------------------------------------------------------------------------------------------
# INPUT AND OUTPUT PATHS

# edge_list_path = '../../network_data/harvey/edges/'
# node_edges_path = '../../network_data/harvey/node_edges/'   # required when using mpi reader

edge_list_path = '../../network_data/'
node_edges_path = '../../network_data/'   # required when using mpi reader

# clusters_path: where resulting clusters will be saved
clusters_path = 'save_runs/'+sim1+'_'+sim2+'/'+network+'/th_'+str(t1)+'_'+str(t2) + '/'

# log will be in same directory as clustering
log_path = clusters_path 

# directory for clustering scores
scores_path = 'save_scores/'+sim1+'_'+sim2+'/'+ network + '/'

# ------------------------------------------------------------------------------------------------------------
# RUNNING SET UP

fps = []
outliers_action = 'remove'

print('Calculating similarity: using ' + sim1 + ' and ' + sim2)    
print('initial_threshold: ' + str(t1))
print('merging_threshold: ' + str(t2))
print('')

# ------------------------------------------------------------------------------------------------------------
# RUN ALGORITHM

start = timer()

# build graph from edge file 
graph = buildGraph(edge_list_path, network)
nodes = sorted(graph.nodes())

## NOTE: to_adjacency_matrix doesn't return an ordered matrix (use GraphReader)
## csr_matrixg = nx.adjacency_matrix(graph)
## matrixg = nx.to_numpy_matrix(graph, nodelist=sorted(graph.nodes()))

# load csr matrix
gr = GraphReader(edge_list_path + network + '.tsv', node_edges_path + network + '_node_edges.txt')
csr_matrixg = gr.read() # csr sparse matrix from the reader

# try loading the matrix from a pickle in here

# save csr matrix
with open(edge_list_path + network + 'csr_matrix.pickle', 'wb') as f:
    pickle.dump(csr_matrixg, f)

fps_temp, fmap_temp, fmap_oultiers = findProbabilisticClusters(network, nodes, csr_matrixg, fps, log_path, similarity=sim1, threshold=t1)
merged_fps, merged_fmap = mergeProbabilisticFingerprints(fps_temp, fmap_temp, outliers_action, log_path, similarity=sim2, threshold=t2)
pruned_fmap = getNonOverlappingClusters(merged_fmap)

end = timer()

print('Clusters found: ' + str(len(pruned_fmap)))
print('Clusters merged: ' + str(len(fmap_temp)-len(pruned_fmap)))
print('Remaining clusters: ' + str(len(pruned_fmap)))

# ---------------------------------------------------------------------------------------------

partition = dict()
for cluster, nodes in pruned_fmap.items():
    for node in nodes:
        partition[node] = cluster

# ---------------------------------------------------------------------------------------------
# SAVE CLUSTERS (only final "merged" clusters that will be analized)
print('')
print('saving final fmap pickle')
with open(clusters_path + network + '_' + str(t1) + '_' + str(t2) + '_fmap'+ '.pkl', 'wb') as f:
    pickle.dump(pruned_fmap, f)
    
print('saving fps pickle')
with open(clusters_path + network + '_' + str(t1) + '_' + str(t2) + '_fps'+ '.pkl', 'wb') as f:
    pickle.dump(merged_fps, f)
    
# print('saving partition pickle')
# with open(clusters_path + network + '_' + str(t1) + '_' + str(t2) + '_partition'+ '.pkl', 'wb') as f:
#     pickle.dump(partition, f)

# ---------------------------------------------------------------------------------------------
# SCORES AND EVALUATION


try:
    print('calculating metrics')
    method = 'dotsim'
    scores = {}

    clusters = list(pruned_fmap.values())
    c = cdlib.classes.node_clustering.NodeClustering(clusters, graph, method)

    # modularity fitness functions
    newman_modularity = evaluation.newman_girvan_modularity(graph,c).score
    conductance = evaluation.conductance(graph,c).score
    internal_edge_density = evaluation.internal_edge_density(graph,c).score   
    cut_ratio = evaluation.cut_ratio(graph,c).score

    # erdos_renyi_mod = evaluation.erdos_renyi_modularity(graph,c).score
    # link_modularity = evaluation.link_modularity(graph,c).score
    # average_internal_degree = evaluation.average_internal_degree(graph,c).score

    # edges_inside = evaluation.edges_inside(graph,c).score
     

    scores['t1'] = t1
    scores['t2'] = t2
    scores['clusters_found'] = len(fmap_temp)
    scores['clusters_merged'] = len(fmap_temp)-len(pruned_fmap)
    scores['remaining_clusters'] = len(pruned_fmap)

    scores['newman_modularity'] = newman_modularity
    scores['conductance'] = conductance
    scores['internal_edge_density'] = internal_edge_density
    scores['cut_ratio'] = cut_ratio

    # scores['erdos_renyi_mod'] = erdos_renyi_mod
    # scores['link_modularity'] = link_modularity
    # scores['average_internal_degree'] = average_internal_degree
    # scores['edges_inside'] = edges_inside

    with open(scores_path + network + '_' + str(t1) + '_' + str(t2) + '_scores' + '.pkl', 'wb') as f:
        pickle.dump(scores, f)
    print('saved_metrics')

except:
    print("Oops!", sys.exc_info()[0], "occurred.")
    print("Next Threshold Values")
    print()


# --------------------------------------------------------------------------------------------
# HOW TO RUN: 
# python3 run_probabilistic_clustering.py -n zachary_karate_club -t1 0.3 -t2 0.3 -sim1 dotsim -sim2 dotsim

