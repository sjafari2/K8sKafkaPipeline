import networkx as nx
import h5py
from scipy import sparse
from scipy.sparse import vstack
import numpy as np
from os import listdir
from os.path import isfile, join
import pickle
from helper import *


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
#---------------------------------------------------------------------------------------------------------
def check_hdf5_structure(path,files_list):
    '''
    INPUT
        files_list: list of hdf5 files to be checked
    OUTPUT
        list of valid files

    '''
    valid_files = []  # List to store files that are structured correctly
    #file_name = "consumer-2-pod-0-20231101-185246.h5" 
    #file_path = "./consumer-app-data/Pod_0/"+file_name
    #files_list = [file_name]
    for file in files_list:
        is_valid = True  # Flag to check if the current file is valid
         # Check if the file exists before attempting to open it
        print(f" file is {file}") 
        file_path =  path + file
        print(f" file path is {file_path}")

        if not os.path.exists(file_path):

            print(f"File '{file}' does not exist.")
            continue  # Skip to the next file 
        
        with h5py.File(file, 'r') as f:
            # Check if 'csr_matrixg' group exists
            if 'csr_matrixg' not in f:
                print(f"File {file} does not contain the 'csr_matrixg' group.")
                is_valid = False
                continue  # Skip to the next file

            print("first checking passed") 
            g2 = f['csr_matrixg']

            # Check if the group contains the expected datasets
            expected_datasets = ['data', 'indices', 'indptr']
            for dataset_name in expected_datasets:
                if dataset_name not in g2:
                    print(f"Group 'csr_matrixg' in file {file} does not contain the '{dataset_name}' dataset.")
                    is_valid = False
                    break  # Exit the inner loop since we found a missing dataset
                
                # Check if the dataset is not empty
                elif len(g2[dataset_name]) == 0:
                    print(f"Dataset '{dataset_name}' in file {file} is empty.")
                    is_valid = False
                    break  # Exit the inner loop since we found an empty dataset

        # If the file passed all checks, add it to the valid_files list
        if is_valid:
            valid_files.append(file)

    num_valid_files = len(valid_files)
    total_files = len(files_list)

    print(f"Number of valid files: {num_valid_files}")
    print(f"Total number of files: {total_files}")
    print(f"Percentage of valid files: {(num_valid_files / total_files) * 100:.2f}%")
    
    return valid_files 

# -------------------------------------------------------------------------------------------------------------
def save_summed_matrix(filename, filepath, col, row, data):
    # Get current date and time
        now =datetime.now()
        date_time_str = now.strftime("%Y%m%d_%H%M%S")
    
    # Insert date-time string into the filename before the extension
        base_filename, file_extension = os.path.splitext(filename)
        new_filename = f"{base_filename}_{date_time_str}{file_extension}"
        
        row_range = 100000
        col_range = 500000
        #print(f"Row range is {row_range}")
        os.makedirs(filepath, exist_ok=True)
        matrix = csr_matrix((data, (row, col)), shape=(row_range, col_range))
        extension = 'lck'
    
    # Use the new filename with the date-time string
        hdf5.csr2h5py(matrix, os.path.join(filepath, new_filename), extension)
        os.rename(os.path.join(filepath, new_filename + '.' + extension), os.path.join(filepath, new_filename + '.h5'))

#---------------------------------------------------------------------------- 

def count_zero_rows_columns(csr_matrix):
    # Count the number of zero rows and zero columns in the CSR matrix
    zero_rows = np.sum(np.sum(csr_matrix, axis=1) == 0)
    zero_columns = np.sum(np.sum(csr_matrix, axis=0) == 0)
    return zero_rows, zero_columns

#------------------------------------------------------------------------------

def count_nonzero_rows_columns(csr_matrix):
    '''
    Count the number of non-zero rows and non-zero columns in a CSR matrix.

    INPUT:
        csr_matrix: The CSR matrix to count non-zero rows and columns in.

    OUTPUT:
        nonzero_rows: Number of non-zero rows.
        nonzero_columns: Number of non-zero columns.
    '''
    nonzero_rows = np.sum(np.sum(csr_matrix, axis=1) != 0)
    nonzero_columns = np.sum(np.sum(csr_matrix, axis=0) != 0)
    return nonzero_rows, nonzero_columns

#-------------------------------------------------------------------------------

def sumPickle(path, files_to_sum):
    '''
    INPUT
        path: path where consumer output files are
        files_to_sum: list of pickle files
    OUTPUT
        summed_csr_matrix
    '''
    first_file = files_to_sum[0]
    summed_csr_matrix = None
    unique_rows = set()
    unique_columns = set()

    try:
        with open(os.path.join(path, first_file), 'rb') as fp:
            summed_csr_matrix = pickle.load(fp)
            unique_rows.update(summed_csr_matrix.nonzero()[0])
            unique_columns.update(summed_csr_matrix.nonzero()[1])

        for file in files_to_sum[1:]:
            with open(os.path.join(path, file), 'rb') as fp:
                csr_matrix = None
                try:
                    csr_matrix = pickle.load(fp)
                    unique_rows.update(csr_matrix.nonzero()[0])
                    unique_columns.update(csr_matrix.nonzero()[1])
                    
                except EOFError as e:
                    # Handle the truncated file (skip it)
                    warnings.warn(f"Skipping '{file}' due to a truncated pickle file.")
                except Exception as ex:
                    print(f"Exception {ex} happened while loading '{file}'")

                if csr_matrix is not None:
                    if summed_csr_matrix is None:
                        summed_csr_matrix = csr_matrix
                    else:
                        summed_csr_matrix += csr_matrix

    except Exception as ex:
        print(f"Exception {ex} happened while loading '{first_file}'")

    if summed_csr_matrix is not None:

        #num_rows, num_cols = summed_csr_matrix.shape
        #num_rows = np.count_nonzero(summed_csr_matrix.sum(axis=1))
        #num_cols = np.count_nonzero(summed_csr_matrix.sum(axis=0))
        
        # Get the number of unique rows and columns after the operation
        num_unique_rows = len(unique_rows)
        num_unique_columns = len(unique_columns)

        
        print(f"Number of Unique Rows : {num_unique_rows}")
        print(f"Number of Unique Columns : {num_unique_columns}")
        
        # Save the summed CSR matrix using your provided function
        with open('./complete_csr_matrix.pickle', 'wb') as fp:
            pickle.dump(summed_csr_matrix, fp)

        # Call the function to count non-zero rows and columns for summed csr matrix
        nonzero_rows_after, nonzero_columns_after = count_nonzero_rows_columns(summed_csr_matrix)

        # Print or use the counts after the operation as needed
        print(f"Summed CSR Matrix Non-Zero Rows Count: {nonzero_rows_after}")
        print(f"Summed CSR Matrix Non-Zero Columns Count: {nonzero_columns_after}") 
    
    return summed_csr_matrix
'''
def sumPickle(path, files_to_sum):
    if not files_to_sum:
        raise ValueError("The provided files_to_sum list is empty!")

    #print("Initialize the summed_csr_matrix as an empty CSR matrix")
    try:
        summed_csr_matrix = csr_matrix((500000, 500000))
    except Exception as ex:
        print(f" exception {ex} happend while initializing the metrix")
    #print(f" type file_to_sum is {type(files_to_sum)}")
    for file in files_to_sum:
        print(f" file is {file}")
        try:
            with open(os.path.join(path, file), 'rb') as f:
                loaded_matrix = pickle.load(f)
               # print(f"csr metrix is {loaded_matrix}")
                summed_csr_matrix += loaded_matrix
        except Exception as ex:
            print(f"Exception {ex} happened")
            return None

    return summed_csr_matrix
    '''
# ----------------------------------------------------------------------------

def sumCSR(path, files_to_sum):
    '''
    INPUT
        path: path where consumer output files are
        files_to_sum: list of h5 files 
    OUTPUT
        sumed_csr_matrix
    '''
    
    if not files_to_sum:
        raise ValueError("The provided files_to_sum list is empty!")
   
    # Load the first matrix directly as the starting summed matrix
    valid_files_to_sum = files_to_sum #check_hdf5_structure(path,files_to_sum)
    #print(f"valid files to sum are {valid_files_to_sum}")
    try:
        sumed_csr_matrix = load_csr(path + valid_files_to_sum[0])   
        for file in valid_files_to_sum[1:]:
            csr_matrix = load_csr(path + file)
            sumed_csr_matrix+=csr_matrix
    except Exception as ex:
        print(f" Exception {ex} happend")
        return None
    # Verify the CSR matrix data
    assert len(sumed_csr_matrix.indices) == len(sumed_csr_matrix.indptr) - 1
    assert len(sumed_csr_matrix.indices) == len(sumed_csr_matrix.data) 
    
    # Save the summed CSR matrix using your provided function
    save_summed_matrix(
            filename="Summed_CSR_Matrix",
            filepath="./app-merge-data/",
            col=sumed_csr_matrix.indices,
            row=sumed_csr_matrix.indptr[:-1],  # Assuming you want the indptr values minus the last
            data=sumed_csr_matrix.data,
           # col_from_range=sumed_csr_matrix.shape[1]  # Assuming this is what you meant by col_from_range
        )
    return sumed_csr_matrix
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
    #print("Attempting to open:", file)
    try:
        f = h5py.File(file,'r')
        g2 = f['csr_matrixg']
        csr_matrixg2 = sparse.csr_matrix((g2['data'][:],g2['indices'][:], g2['indptr'][:]), g2.attrs['shape'])

        f.close()
        return csr_matrixg2
    
    except Exception as e:
        print(f"Error reading {file}: {e}")
        return None
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
