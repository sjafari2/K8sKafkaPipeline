from  find_probabilistic_clusters import *
import functions
import argparse
import sys
import pickle
from os import listdir
from os.path import isfile, join

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Run Find Cluster algorithm")
    parser.add_argument('-pypath','--pypath', required=True)                # h5py path file
    parser.add_argument('-t1', '--t1',required=True, type=float)            # first threshold
    parser.add_argument('-t2', '--t2',required=True, type=float)            # second threshold
    parser.add_argument('-sim1', '--sim1',required=True)                    # first threshold metric
    parser.add_argument('-sim2', '--sim2',required=True)                    # second threshold metric
    parser.add_argument('-fps', '--fps',required=True)                      # fps
    parser.add_argument('-podindex','--podindex', type =int, required=True) # pod index number
    parser.add_argument('-logpath',  '--logpath',default="")                # Path of logs
    parser.add_argument('-localclstrpath', '--localclstrpath',default="")   # Path of local clusters


    args = parser.parse_args(sys.argv[1:])

#    network = args.n
    t1 = args.t1
    t2 = args.t2
    sim1 = args.sim1
    sim2 = args.sim2
    podindex = args.podindex
#   fps = []
    log_path = args.logpath
    h5pypath = str(args.pypath)
    clrpath = args.localclstrpath
    #print(f"fps type is {type(fps)}")
    #print(f"H5 files are in format of {h5pypath}")
    outliers_action='remove'


    #print("load files from directory into list")
    h5_files = sorted([f for f in listdir(h5pypath) if isfile(join(h5pypath, f)) if 'h5' in f and f'pod-{podindex}' in f])
   # print(f"hdf files are {h5_files}")
    for f in h5_files:
        csr_matrixg = functions.load_csr(h5pypath +'/'+ f)
        print(f"shape of csr matrix is {csr_matrixg.shape}")
        fps = [] 
        fps_temp, fmap_temp, fmap_oultiers = findProbabilisticClusters(csr_matrixg, fps, log_path, similarity=sim1,  threshold=t1)
        fpsname  = str(clrpath)+'/'+str(f)+'_fps_temp.pickle'
        fmapname = str(clrpath)+'/'+str(f)+'_fmap_temp.pickle'
        try:
            os.makedirs(os.path.dirname(clrpath), exist_ok=True)
#            os.makedirs(os.path.dirname(fmappath), exist_ok=True)
        except Exception as ex:
            print(str(ex))
        try:
            with open(fpsname,'wb') as fp:
                pickle.dump(fps_temp, fp)
                print(f" recored fps temp file: {fps_temp}") 
        except Exception as ex:
            print(str(ex))
        try:
            with open(fmapname,'wb') as fp:
                pickle.dump(fmap_temp, fp)
                print(f" recored fmap temp file: {fmap_temp}") 
        except Exception as ex:
            print(str(ex))

        os.remove(h5pypath+'/'+f)
       # print(f'Clusters found:{len(pruned_fmap)}')
       # print(f'Clusters merged: {len(fmap_temp)-len(pruned_fmap)}')
       # print(f'Remaining clusters: {len(pruned_fmap)}')
