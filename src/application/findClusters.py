from find_probabilistic_clusters import *
from functions import *
import argparse
import sys
import pickle
from os import listdir
from os.path import isfile, join
import helper
from datetime import datetime

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Run Find Cluster algorithm")
    parser.add_argument('-pypath','--pypath', required=True)                # h5py path file
    parser.add_argument('-t1', '--t1',required=True, type=float)            # first threshold
    parser.add_argument('-t2', '--t2',required=True, type=float)            # second threshold
    parser.add_argument('-sim1', '--sim1',required=True)                    # first threshold metric
    parser.add_argument('-sim2', '--sim2',required=True)                    # second threshold metric
    parser.add_argument('-appindex', '--appindex',required=True)            # application index
    parser.add_argument('-fps', '--fps',required=True)                      # fps
    parser.add_argument('-logpath',  '--logpath',default="")                # Path of logs
    parser.add_argument('-localclstrpath', '--localclstrpath',default="")   # Path of local clusters


    args = parser.parse_args(sys.argv[1:])

#   network = args.n
    t1 = args.t1
    t2 = args.t2
    sim1 = args.sim1
    sim2 = args.sim2
    appindex = args.appindex
#   fps = []
    log_path = args.logpath
    h5pypath = str(args.pypath)
    clrpath = args.localclstrpath
    #print(f"fps type is {type(fps)}")
    #print(f"H5 files are in format of {h5pypath}")
    outliers_action='remove'


    #load files from directory into list
#    app_pattern = f"consumer-{appindex}-"
    h5_files = sorted([f for f in listdir(h5pypath) 
                   if isfile(join(h5pypath, f)) 
                   if 'pickle' in f]) 
#                   if app_pattern in f])
  
    #print(f"hdf files are {h5_files}")
    #print(f" type of hf_files is {type(h5_files)}")
    print(f"There are {len(h5_files)} pickle files")

    try:
        csr_matrixg = sumPickle(h5pypath, h5_files)
        print(f"shape of csr matrix is {csr_matrixg.shape}")
    except Exception as ex:
        print("Could not create SummedCSR matrix")
        print(str(ex))
    fps = [] 
    fps_temp, fmap_temp, fmap_oultiers = findProbabilisticClusters(csr_matrixg, fps, log_path, similarity=sim1, threshold=t1)
    
    # Get current date and time
    print("start to write the result of local clustering")
    now =datetime.now()
    date_time_str = now.strftime("%Y%m%d_%H%M%S")

    fpsname  = str(clrpath)+'/'+date_time_str+'_fps_temp.pickle'
    fmapname = str(clrpath)+'/'+date_time_str+'_fmap_temp.pickle'
    try:
        os.makedirs(os.path.dirname(clrpath), exist_ok=True)
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

    try:
        hlpr = helper.Tools()
        hlpr.move_to_processed(h5_files,h5pypath) 
        print ("Done with moving files to processed directory")
    except Exception as ex:
        print(str(ex))

        #os.remove(h5pypath+'/'+f)
        #print(f'Clusters found:{len(pruned_fmap)}')
        #print(f'Clusters merged: {len(fmap_temp)-len(pruned_fmap)}')
        #print(f'Remaining clusters: {len(pruned_fmap)}')

