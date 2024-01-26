from os import listdir
from os.path import isfile, join
import pickle

def gatherResults(path):
    '''
    INPUT
        path: path to find clusters output files
    OUTPUT
        consolidated list of fingerprints and fmap fingerprint-node mapping
        '''
   
    # load files from directory into list
    fingerprint_files = sorted([f for f in listdir(path) if isfile(join(path, f)) if 'fps' in f])
    
    # each fingerprint file is a list of numpy.ndarrays
    # we will load each fingerprint list of numpy.ndarrays and put it in a list
    fingerprints = []
    for fp_file in fingerprint_files:
        with open(path + fp_file, 'rb') as fpf:
            fps = pickle.load(fpf)
        fingerprints.append(fps)
        
    # flatten list of lists of numpy.ndarrays
    fps_temp = [fp_array for fps_list in fingerprints for fp_array in fps_list]
    print('there are {} fingerprints'.format(len(fps_temp)))
    
    fingerprint_keys = [i for i,fp in enumerate(fps_temp)]
    print('keys: {}'.format(fingerprint_keys))
    
    fmap_files = sorted([f for f in listdir(path) if isfile(join(path, f)) if 'fmap' in f])
    
    # each fmap_file is a dict where the keys are the fingerprint indexes in fps_temp
    # and the values hold the information about nodes assigned to that fingerprint
    
    all_assignments = []
    for fmap_file in fmap_files:
        with open(path + fmap_file, 'rb') as fmapf:
            fmap = pickle.load(fmapf)

        # get dictionary values (node assignment info, type list of lists)
        # 0: [ [node = 0, prob = 1.0, flag = 1],
        #          [node = 1, prob = 1.0, flag = 1],
        #           ...],
        fmap_vals = list(fmap.values())
        
        all_assignments.append(fmap_vals)

    # flatten list of assignments
    fmap_values = [assignment for list_of_assignments in all_assignments for assignment in list_of_assignments]   
        
    # using dictionary comprehension
    # to create fmap_temp from the two lists
    fmap_temp = {fingerprint_keys[i]: fmap_values[i] for i in range(len(fingerprint_keys))}
        
    return fps_temp, fmap_temp
