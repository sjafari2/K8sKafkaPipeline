from find_probabilistic_clusters import *
from functions import *
import argparse
import sys
from os import listdir
from os.path import isfile, join
import pickle

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Perform Merge Step")
#    parser.add_argument('-n', required=True)                   # network
    parser.add_argument('-datapath','--datapath', required=True)      # path file to clustering results
    parser.add_argument('-t1','--t1', required=True, type=float)      # first threshold
    parser.add_argument('-t2','--t2', required=True, type=float)      # second threshold
    parser.add_argument('-sim1','--sim1', required=True)              # first threshold metric
    parser.add_argument('-sim2', '--sim2', required=True)             # second threshold metric
    parser.add_argument('-logpath','--logpath',  default="")          # path of logs
    parser.add_argument('-mergedpath', '--mergedpath', default="")    # path of merged fps and fmap and pruned fmap

    args = parser.parse_args(sys.argv[1:])

#    network = args.n
    t1 = args.t1
    t2 = args.t2
    sim1 = args.sim1
    sim2 = args.sim2
    fps = []
    log_path = args.logpath
    data_path = args.datapath+'/'
    merged_path = args.mergedpath
    outliers_action='remove'

    files = sorted([f for f in listdir(data_path) if isfile(join(data_path, f))])
    print(files)

    fps_temp, fmap_temp = gatherResults(data_path)
    merged_fps, merged_fmap = mergeProbabilisticFingerprints(fps_temp, fmap_temp, outliers_action, log_path, similarity=sim2, threshold=t2)    
    pruned_fmap = getNonOverlappingClusters(merged_fmap)

    fps  = str(merged_path)+'/merged_fps.pickle'
    fmap = str(merged_path)+'/merged_fmap.pickle'
    prunedfmap = str(merged_path)+'/pruned_fmap.pickle'

    with open(fps,'wb') as fp:
        pickle.dump(merged_fps, fp)

    with open(fmap,'wb') as fp:
        pickle.dump(merged_fmap, fp)
    with open(prunedfmap,'wb') as fp:
        pickle.dump(pruned_fmap, fp)


    print(f'Clusters found:{len(fmap_temp)}')
    print(f'Clusters merged: {len(fmap_temp)-len(pruned_fmap)}')
    print(f'Remaining clusters: {len(pruned_fmap)}')

    ### Cleanig and removing files after processing
    #clean()
    
