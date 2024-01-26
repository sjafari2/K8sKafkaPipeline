import time
from collections import defaultdict
import dask.array as da
import dask
from dask.distributed import Client
from functions import *

# -----------------------------------------------------

client = Client(n_workers=4)

# reconstruct csr matrix from h5py file
file = 'graph_csr_matrix.h5'
csr_matrix = load_csr(file)
# print(type(csr_matrix))

#csr to dask array
csr_dask_array = da.from_array(csr_matrix, chunks=(3, 12))
print('dask_csr_array.astype')

# algorithm code (buggy)
def findProbabilisticClusters(network, nodes, csr_matrixg, fps_csr, similarity='dotsim', threshold=0.05):

    _MIN_LINKS = 2   # minimum number of links to be added as a fingerprint
    num_nodes = len(nodes)    
    processed_nodes = {}
    outlier_nodes = defaultdict(list) 
    fps_map = {}
    
    for ri,node in enumerate(nodes):

        # get node as row vector of the sparse matrix with node's index       
        row = csr_matrixg[ri]
        
        # the sum of vector elements
        sum_nodes = row.sum()
        
        if sum_nodes == 0: continue

        # initialize fingerprints
        if fps_csr == 'Empty':
            fp_id = 'a'     # string id
            fp_idx = 0      # index in the fps_csr matrix 
            node_assignment = {}
            node_assignment[fp_id] = {'prob': 1.0, 'flag': 1}
            processed_nodes[node] = node_assignment
            
            # the first node is the first fingerprint 
            fps_csr = row.astype(np.float) # making sure that we start the fps_csr matrix with floats
            
            # add 1 first fp count to keep track of number of nodes in the fingerprint
            fps_map[fp_idx] = {'fp_id': fp_id, 'fp_count': 1}     
            
            fps_csr = fps_csr.reshape((-1, fps_csr.shape[0]))
            
            continue
                
        # find candidates: all fingerprints where sim(fp,node) > threshold, saved as (fp_id, score)   
        passing_fps_idx, passing_scores = getScores(similarity, threshold, fps_csr, row, sum_nodes)
        sum_of_passing_scores = passing_scores.sum()
        
        # if there are candidates 
        if len(passing_fps_idx) != 0:
            fingerprint_candidates = np.column_stack((passing_fps_idx,passing_scores))
            
            max_score_row = np.argmax(fingerprint_candidates[:, 1])               # find fp with max score: (fp_index,score)
            max_score_fp_idx = int(fingerprint_candidates[max_score_row][0])      # get index of max scoring fingerprint
            max_score_fp_id = fps_map[max_score_fp_idx]['fp_id']                  # find fingerprint (str) id in mapping dict
            
            for fp_candidate in fingerprint_candidates:
                fp_idx = fp_candidate[0]                                          # index in the fps_csr matrix where the fingerprint is
                fp_id = fps_map[fp_idx]['fp_id']                                  # fp_candidate[0] -> fingerprint string id  
                
                prob = fp_candidate[1]/sum_of_passing_scores                      # fp_candidate[1] is the similarity score
                
                if fp_idx == max_score_fp_idx:
                    flag = 1                                                      # 1 represents that this was the maximum scoring fingerprint
                else:
                    flag = 0
                
                node_assignment = {}
                node_assignment[fp_id] = {'prob': prob, 'flag': flag}
                processed_nodes[node] = node_assignment
                
                # print('fps_csr shape:', fps_csr.shape) 
                # print('fps_csr type:', type(fps_csr)) 
                # print('fp_idx type:', fp_idx)
                
                ###############################################################################################################
                # SANDWICH
                ###############################################################################################################
                                
                # update fingerprint with new node
                updated_fp = updateFingerprintProbabilistic(False, fps_csr[fp_idx], row, fps_map[fp_idx]['fp_count'], 1, prob)
                
                start=time.time()

                if fp_idx == 0:
                    fps_csr = updated_fp
                    
                elif fp_idx == 1:
                    fist_part_fps_csr = fps_csr[0,:]                    
                    fps_csr = da.vstack(fist_part_fps_csr,updated_fp)
                    
                elif fp_idx > 2:
                    # slice n rows, all columns
                    start_idx_1 = 0
                    end_idx_1 = fp_idx - 1 
                    fist_part_fps_csr = fps_csr[start_idx_1:end_idx_1,  :]
                
                    # print('type fist_part_fps_csr: {}'.format(type(fist_part_fps_csr)))
                    # print('shape fist_part_fps_csr: {}'.format(fist_part_fps_csr.shape))
                
                    # slice n rows, all columns
                    start_idx_2 = fp_idx + 1
                    end_idx_2 = fps_csr.shape[0]
                    second_fps_csr = fps_csr[start_idx_2:end_idx_2 ,  :]
                
                    fps_csr_temp = da.vstack(fist_part_fps_csr,updated_fp)
                    fps_csr = da.vstack(fps_csr_tmp,second_fps_csr)
                    
                end=time.time()  
                # print ('time it takes to sandwich new fps_csr {}'.format(end - start))
                
                # update fingerprint with new node
                # updated_fp = updateFingerprintProbabilistic(False, fps_csr[fp_idx], row, fps_map[fp_idx]['fp_count'], 1, prob)
                # fps_csr[fp_idx,:] = updated_fp
                
                ###############################################################################################################
                ###############################################################################################################

                # increment the count in each fingerprint by 1 to keep track of number of members in the fingerprint 
                fps_map[fp_idx]['fp_count'] = fps_map.get(fp_idx)['fp_count'] + 1
                
        # no similar fingerprints, creating a new one
        elif sum_nodes > _MIN_LINKS: 
            
            fp_idx = fps_csr.shape[0]                       # index in the fps_csr matrix
            last_fp_idx = list(fps_map)[-1]                 # last fp_idx assigned
            last_fp_id = fps_map[last_fp_idx]['fp_id']      # last fp_id assigned
            new_fp_id = nextID(last_fp_id)                  # next string ID to assign
            prob = 1.0
            flag = 1
            
            node_assignment = {}
            node_assignment[new_fp_id] = {'prob': prob, 'flag': flag}
            processed_nodes[node] = node_assignment
            
            # the first node is the first fingerprint
            fps_csr = da.vstack([fps_csr, row])
            # fps_csr = da.vstack(fps_csr, row)
            
            # add 1 first fp count to keep track of number of nodes in the fingerprint
            fps_map[fp_idx] = {'fp_id': new_fp_id, 'fp_count': 1}            

        else: # node has very few links to be added as a fingerprint, assign to outliers cluster
            outlier_nodes[0].append(node)
            
    return fps_csr, fps_map, processed_nodes, outlier_nodes


fps_csr = 'Empty'
outliers_action = 'remove'
similarity='dotsim'
t1=0.05

# run code 
#time
fps_csr, fps_map, processed_nodes, outlier_nodes = findProbabilisticClusters(graph, nodes, dask_coo_array, fps_csr, similarity='dotsim', threshold=t1)
