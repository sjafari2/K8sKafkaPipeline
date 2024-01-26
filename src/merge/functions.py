import networkx as nx
import h5py
from scipy import sparse
from scipy.sparse import coo_matrix, csr_matrix, vstack, spmatrix
import numpy as np
from os import listdir
from os.path import isfile, join
import pickle


def buildGraph(edge_list_path, network):
    '''
    takes in edge list and returns nx graph object
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

# -------------------------------------------------------------------------------------------------------------


def divide_files(l, n):
     
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]
        
# ------------------------------------------------------------------------------------------------------------

def assignConsumerOutput2Algorithm(path, n):
    '''
    Read consumer output (h5) files as a list
    Divide it into sublists with csr matrices to stack
    
    INPUT
        path: path where consumer output files are
        n:    how many csr matrices each instance should get
        
    OUTPUT
        assigned files: list of lists where each sublist's files will be stacked into a single matrix
    '''
    
    # load files from directory into list
    files = sorted([f for f in listdir(path) if isfile(join(path, f)) if 'h5' in f])
    
    # create sublists of size n of matrices that will be stacked
    file_assignment = list(divide_files(files, n))
    
    return file_assignment

# -------------------------------------------------------------------------------------------------------------

def stackCSR(path, files_to_stack):
    '''
    INPUT
        path: path where consumer output files are
        files_to_stack: list of h5 files 
    OUTPUT
        stacked_csr_matrix
    '''
    all_matrices = []
    for file in files_to_stack:
        csr_matrix = load_csr(path + file)
        all_matrices.append(csr_matrix)
        
    stacked_csr_matrix = vstack(all_matrices)
    return stacked_csr_matrix

        
# ------------------------------------------------------------------------------------------------------------

def csr2h5py(csr_matrixg,filename):
    ''' A csr matrix stores its values in 3 arrays. It is not an array or array subclass, so h5py cannot save it directly. 
        This function saves the attributes, so that the matrix can be recreated on loading '''
    # print(repr(csr_matrixg))
    # print(csr_matrixg.data)
    # print(csr_matrixg.indices)
    # print(csr_matrixg.indptr)

    f = h5py.File('{}.h5'.format(filename),'w')
    g = f.create_group('csr_matrixg')
    g.create_dataset('data', data = csr_matrixg.data)
    g.create_dataset('indptr', data = csr_matrixg.indptr)
    g.create_dataset('indices', data = csr_matrixg.indices)
    g.attrs['shape'] = csr_matrixg.shape
    f.close()
    
# -------------------------------------------------------------------------------------------------------------

def coo2h5py(coo_matrixg,filename):
    ''' A csr matrix stores its values in 3 arrays. It is not an array or array subclass, so h5py cannot save it directly. 
        This function saves the attributes, so that the matrix can be recreated on loading '''

    f = h5py.File('{}.h5'.format(filename),'w')
    g = f.create_group('coo_matrixg')
    g.create_dataset('data', data=coo_matrixg.data)
    g.create_dataset('row', data=coo_matrixg.row)
    g.create_dataset('col', data=coo_matrixg.col)
    g.attrs['shape'] = coo_matrixg.shape
    f.close()

# -------------------------------------------------------------------------------------------------------------

def load_csr(file):
    ''' reads in a h5py file and constructs a csr matrix; CSR constructed from (dat, (row, col)) '''
    f = h5py.File(file,'r')
    g2 = f['csr_matrixg']
    csr_matrixg2 = sparse.csr_matrix((g2['data'][:],g2['indices'][:], g2['indptr'][:]), g2.attrs['shape'])

    f.close()
    return csr_matrixg2

# -------------------------------------------------------------------------------------------------------------

def load_coo(file):
    ''' reads in a h5py file and constructs a csr matrix; COO constructed from ijv format: (data, (row, col)) '''
    f = h5py.File(file,'r')
    g2 = f['coo_matrixg']
    coo_matrixg2 = sparse.coo_matrix((g2['data'], (g2['row'], g2['col'])), g2.attrs['shape']) 
    f.close()
    return coo_matrixg2

# -------------------------------------------------------------------------------------------------------------

def sparseClip(sparse_fp, min_clip, max_clip):
    ''' clip (limit) the values in the new (sparse) fp '''

    nonzero_mask1 = np.array(sparse_fp[sparse_fp.nonzero()] < min_clip)[0]
    rows = sparse_fp.nonzero()[0][nonzero_mask1]
    cols = sparse_fp.nonzero()[1][nonzero_mask1]
    sparse_fp[rows, cols] = min_clip
    nonzero_mask2 = np.array(sparse_fp[sparse_fp.nonzero()] > max_clip)[0]
    rows = sparse_fp.nonzero()[0][nonzero_mask2]
    cols = sparse_fp.nonzero()[1][nonzero_mask2]
    sparse_fp[rows, cols] = max_clip

    return sparse_fp

# ------------------------------------------------------------------------------------------------------------
def updateFingerprintProbabilistic(in_merge, fp, vec, countfp, countvec=1, probability=1):
    ''' updates a fingerprint when a node vector is added to the cluster
        through weighted merge of the node vector with the fingerprint '''
    
    # number of nodes in the cluster + number of nodes being added
    count_total=np.sum(countfp)+np.sum(countvec)
    
    if in_merge:
        propfp = np.sum(countfp)/count_total
        propvec = np.sum(countvec)/count_total
    else:
        propfp = 0.999 # meaning -> fp will be preserved 99%
        propvec = 0.001  # proportion influence of new node
    
    new_fp = (fp * propfp) + (vec * propvec * probability)

    # [0, 1]: values < 0 -> 0, values > 1 -> 1
    # new_fp = sparseClip(new_fp, 0, 1)
    # new_fp = new_fp.toarray()
    # new_fp = np.clip(new_fp, 0, 1.0) 
    # new_fp = csr_matrix(new_fp)

    return(new_fp) 

# -------------------------------------------------------------------------------------------------------------
# def updateFingerprintProbabilistic(in_merge, fp, vec, countfp, countvec=1, probability=1):
#     ''' updates a fingerprint when a node vector is added to the cluster
#         through weighted merge of the node vector with the fingerprint '''
    
#     # number of nodes in the cluster + number of nodes being added
#     count_total=np.sum(countfp)+np.sum(countvec)
    
#     if in_merge:
#         propfp=np.sum(countfp)/count_total
#         propvec=np.sum(countvec)/count_total
#     else:
#         propfp=0.999 # meaning -> fp will be preserved 99%
#         propvec=0.1  # proportion influence of new node
    
#     if isinstance(vec, spmatrix):
#         new_fp = fp * propfp + (vec.A.astype(np.float) * propvec)
#     else:
#         new_fp = (fp*propfp) + (vec*propvec*probability)

#     # if an interval of [0, 1] is specified, values smaller than 0 become 0, and values larger than 1 become 1
#     new_fp=np.clip(new_fp, 0, 1.0) 
       
#     return(new_fp) 

# -------------------------------------------------------------------------------------------------------------

def getScores(similarity, threshold, fps_csr, row, sum_nodes):
    '''  calculates similarity or distance scores between node and all fingerprints 
    input
    fps_csr   : (csr_matrix) fingerprints in a sparse matrix, each row is a fingerprint
    row       : (csr_matrix) sparse row vector representing the node's adjacency vector
    sum_nodes : the sum of vector elements
    
    returns fingerprint candidates
    passing_fps_idx: id of fingerprints that have passed the threshold 
    passing_scores : score of passing threshold fingerprints
    '''
    
    if similarity == 'dotsim': # ----------------------------------------------------------------------------
        # print('fps_csr:', fps_csr) 
        # print('fps_csr shape:', fps_csr.shape) 
        # print('fps_csr type', type(fps_csr))
        
        # print('row:', row) 
        # print('row shape:', row.shape) 
        # print('row type', type(row))
        
        result = fps_csr.dot(row.transpose()) / sum_nodes  # here it is using csr_matrix.dot not np.dot
        # print('result:', result) 
        # print('result shape:', result.shape) 
        # print('result type:', type(result)) 
        
        result = result.toarray()
        # print('result:', result) 

#     elif similarity == 'jaccard': # ---------------------------------------------------------------------------------------------------
#         sums=np.sum(array_fps[idxs,:],axis=0)+sum_nodes # array_fps is transposed
#         result=np.divide(row_array[idxs].dot(array_fps[idxs,:]),sums)

#     elif similarity == 'euclidean':  # ------------------------------------------------------------------------------------------------
#         result = np.divide(1, 1 + np.sqrt(np.sum(np.square(np.subtract(row_array,array_fps.transpose())), axis=1))) 
        
#     elif similarity == 'cosine':  # ----------------------------------------------------------------------------------------------------
#         result = cosine_similarity(row_array.reshape(1,-1),array_fps.transpose())
    
    fp_id = np.arange(result.shape[0]) 
    fp_id = fp_id.reshape(-1, 1)

    similarity_scores= np.array([fp_id, result])  

    # fingerprints (idx) that have passed the threshold, sorted from highest scoring to lowest scoring
    cols = np.where(similarity_scores[1] >= threshold)
    passing_scores = similarity_scores[1][cols]     # actual values
    
    passing_fps_idx = similarity_scores[0][cols]    # corresponding fingerprint's index
          
    return passing_fps_idx, passing_scores


# -------------------------------------------------------------------------------------------------------------

def nextID(char):
    ## converting char into int
    i = ord(char[0])
    i += 1


    # casting the resultant int to char
    char = chr(i)
    return char   

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
