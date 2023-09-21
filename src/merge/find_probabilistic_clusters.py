import networkx as nx
from collections import defaultdict
from scipy.sparse import csr_matrix, spmatrix
import pickle
import warnings
warnings.filterwarnings('ignore')
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from reader import *

################################################################################################################################################

def buildGraph( edge_list_path , network ):
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

################################################################################################################################################

def updateFingerprintProbabilistic(in_merge, fp, vec, countfp, countvec=1, probability=1):
    ''' updates a fingerprint when a node vector is added to the cluster
        through weighted merge of the node vector with the fingerprint '''
    
    # number of nodes in the cluster + number of nodes being added
    count_total=np.sum(countfp)+np.sum(countvec)
    
    if in_merge:
        propfp=np.sum(countfp)/count_total
        propvec=np.sum(countvec)/count_total
    else:
        propfp=0.999 # meaning -> fp will be preserved 99%
        propvec=0.1  # proportion influence of new node
    
    if isinstance(vec, spmatrix):
        new_fp = fp * propfp + (vec.A.astype(float) * propvec)
    else:
        new_fp = (fp*propfp) + (vec*propvec*probability)

    # if an interval of [0, 1] is specified, values smaller than 0 become 0, and values larger than 1 become 1
    new_fp=np.clip(new_fp, 0, 1.0) 
       
    return(new_fp) 

################################################################################################################################################

def findProbabilisticClusters(csr_matrixg, fps, save_path, similarity='jaccard', threshold=0.05):
    ''' 
    input
        csr_matrixg: sparse adjacency matrix
        fps: list, empty if clustering is starting but could start with fingerprints
        save_path: path to save logs
        similaity: (str) jaccard, dotsim, euclidean, cosine
        threshold: (float) initial merging threshold

    returns:
        fps:  list of all found fingerprints
        fmap: (dict) fingerprint mapping of nodes to fingerprints to keep track of what nodes belongs to what fp

    {   0: [ [node = 0, prob = 1.0, flag = 1],
             [node = 1, prob = 1.0, flag = 1],
              ...],
        1: [ [node = 3, prob = 1.0, flag = 1], 
             [node = 2, prob = 0.6, flag = 1]
              ...],
        2: [ [node = 2, prob = 0.4, flag = 0] ]
    } 
    '''
    
    _MIN_LINKS = 3   # minimum number of links to be added as a fingerprint
    
    # shape (M,N): (row,col)
    num_nodes = csr_matrixg.shape[0] 
    fmap = defaultdict(list)
    fmap_oultiers = defaultdict(list)

    for ri,node_vector in enumerate(csr_matrixg):

        # get node as row vector of the matrix with node's index       
        row = csr_matrixg[ri]

        # dense vector from csr matrix 
        row_array = row.A[0].astype(float)

        # non-zero elements in the row vector
        idxs = np.nonzero(row_array)[0]

        # the sum of vector components
        sum_nodes = row_array[idxs].sum()
        if sum_nodes == 0 : continue

        # initialize fingerprints
        if len(fps) == 0:
            fp_idx = 0
            prob = 1.0
            flag = 1
            node_info = [ri,prob,flag]
            fmap[fp_idx].append(node_info)
            
            fps.append(row_array)
            array_fps=np.transpose(np.array(fps))
            
            continue

        # FIND CANDIDATES - COMPUTE SIMILARITY ############################################################################################    
        # candidates: all fingerprints where sim(fp,node) > threshold

        # dot Similarity -------------------------------------------------------------------------------------------------------------------
        if similarity == 'dotsim': # ------------------------------------------------------------------------------------------------------

            # calculate similarity between node and all fingerprints
            result = row_array[idxs].dot(array_fps[idxs,:]) / sum_nodes

            fp_idx = np.arange(result.shape[0])

            similarity_scores= np.array([fp_idx, result])  

            # sort array by score i.e. by row at index position 1 
            similarity_scores = similarity_scores[:, similarity_scores[1].argsort()[::-1]]

            # fingerprints (idx) that have passed the threshold, sorted from highest scoring to lowest scoring
            cols = np.where(similarity_scores[1] >= threshold)
            passing_scores = similarity_scores[1][cols]     # actual values
            passing_fps_idx = similarity_scores[0][cols]    # corresponding fingerprint's index

        # jaccard Similarity -----------------------------------------------------------------------------------------------------------------
        elif similarity == 'jaccard': # ------------------------------------------------------------------------------------------------------
            sums=np.sum(array_fps[idxs,:],axis=0)+sum_nodes # array_fps is transposed
            result=np.divide(row_array[idxs].dot(array_fps[idxs,:]),sums)
            
            fp_idx = np.arange(result.shape[0])
            similarity_scores= np.array([fp_idx, result])  

            # sort array by score i.e. by row at index position 1 
            similarity_scores = similarity_scores[:, similarity_scores[1].argsort()[::-1]]

            # fingerprints (idx) that have passed the threshold, sorted from highest scoring to lowest scoring
            cols = np.where(similarity_scores[1] >= threshold)
            passing_scores = similarity_scores[1][cols]     # actual values
            passing_fps_idx = similarity_scores[0][cols]    # corresponding fingerprint's index

        # euclidean Similarity ------------------------------------------------------------------------------------------------------------------
        elif similarity == 'euclidean':  # ------------------------------------------------------------------------------------------------------
            # euclidean distance:  square root of the sum of the squared differences between the two vectors
            # euclidean distance: sqrt(sum for i to N (v1[i] – v2[i])^2)
            # 1/1+d(v1,v2) i.e. inverse of Euclidean distance = similarity score 
            # using all the vector, not only idxs 
            # diffs = np.subtract(row_array,array_fps.transpose())
            # squared_diffs = np.square(diffs)
            # sums = np.sum(squared_diffs, axis=1)
            # result = np.divide(1, 1 + np.sqrt(sums))
                            
            result = np.divide(1, 1 + np.sqrt(np.sum(np.square(np.subtract(row_array,array_fps.transpose())), axis=1))) 

            fp_idx = np.arange(result.shape[0])

            similarity_scores= np.array([fp_idx, result])  

            # sort array by score i.e. by row at index position 1 
            similarity_scores = similarity_scores[:, similarity_scores[1].argsort()[::-1]]

            # fingerprints (idx) that have passed the threshold, sorted from highest scoring to lowest scoring
            cols = np.where(similarity_scores[1] >= threshold)
            passing_scores = similarity_scores[1][cols]     # actual values
            passing_fps_idx = similarity_scores[0][cols]    # corresponding fingerprint's index

        # cosine Similarity ------------------------------------------------------------------------------------------------------------------
        elif similarity == 'cosine':  # ------------------------------------------------------------------------------------------------------
            # need to reshape row array 
            # row_array = row_array.reshape(1,-1)
            # result = cosine_similarity(row_array,array_fps.transpose())
            # print(row_array.reshape(1,-1).shape,array_fps.transpose().shape)

            result = cosine_similarity(row_array.reshape(1,-1),array_fps.transpose())[0]

            fp_idx = np.arange(result.shape[0])

            similarity_scores= np.array([fp_idx, result])  

            # sort array by score i.e. by row at index position 1 
            similarity_scores = similarity_scores[:, similarity_scores[1].argsort()[::-1]]

            # fingerprints (idx) that have passed the threshold, sorted from highest scoring to lowest scoring
            cols = np.where(similarity_scores[1] >= threshold)
            passing_scores = similarity_scores[1][cols]     # actual values
            passing_fps_idx = similarity_scores[0][cols]    # corresponding fingerprint's index


        # # stats of number of fps that become candidates
        # with open(save_path+network+'_candidates_log.txt', 'a+') as f:
        #     f.write("{},{},{},{}\n".format(ri, threshold, len(passing_scores), len(passing_fps_idx)))

        # CLUSTER ASSIGNMENT ##############################################################################################################    

        # sum_all_scores = result.sum()   
        sum_of_passing_scores = passing_scores.sum()

        # if there are candidates (passing scores)
        if len(passing_scores) != 0:

            for i,fp in enumerate(zip(passing_fps_idx, passing_scores)):
                if i == 0:
                    flag = 1    # 1 represents that this was the maximum scoring fingerprint
                else:
                    flag = 0

                fp_idx = int(fp[0])                  # fp[0] -> fingerprint index
                prob = fp[1]/sum_of_passing_scores   # fp[1] -> similarity score
                
                node_info = [ri,prob,flag]
                fmap[fp_idx].append(node_info)

                                            # arguments:    (in_merge, fp, vec, countfp, countvec=1, probability)
                fps[fp_idx] = updateFingerprintProbabilistic(False, fps[fp_idx], row_array, len(fmap[fp_idx]), 1, prob).copy()     

                # with open(save_path+network'_candidates_scores_log.txt', 'a+') as fi:
                #     fi.write("{},{},{},{},{}\n".format(ri, threshold, sum_of_passing_scores, fp_idx, fp[1]))  
    
        # no similar fingerprints, creating a new one
        elif sum_nodes > _MIN_LINKS: 
            # print('no similar fingerprints, creating new one')
            fp_idx = len(fps)
            prob = 1.0
            flag = 1
            node_info = [ri,prob,flag]
            
            fmap[fp_idx].append(node_info)
            fps.append(row_array)      

            array_fps=np.transpose(np.array(fps))                  

        else: # node has very few links to be added as a fingerprint, assign to outliers cluster
            print('outlier node:', ri, 'sum nodes', sum_nodes)
            fmap_oultiers[0].append(ri)

    # return fps, fmap, fmap_oultiers
    return fps, fmap, fmap_oultiers

################################################################################################################################################

def mergeProbabilisticFingerprints(fps_temp, fmap_temp, outliers_action, save_path, similarity='dotsim', threshold=0.3):
    ''' merges two clusters if their fingerprints are more similar than threshold
    
    fps_temp:   (list) fingerprints created in findProbabilisticClusters
    fmap_temp:  (dict) fingerprint mapping of nodes to fingerprints 
                to keep track of what nodes belongs to what fp, created in findProbabilisticClusters

                {   0: [ [node = 0, prob = 1.0, flag = 1],
                         [node = 1, prob = 1.0, flag = 1],
                          ...],
                    1: [ [node = 3, prob = 1.0, flag = 1], 
                         [node = 2, prob = 0.6, flag = 1]
                          ...],
                    2: [ [node = 2, prob = 0.4, flag = 0] ]
                } 

    save_path:  path to save logs, outliers, etc
    similarity: (str) dotsim, jaccard, euclidean, cosine        
    threshold_merge: (float) for merging similar clusters
    '''
    _MIN_DENSITY = 2 # minimum number of elements in cluster to not be flushed

    fmap = {}
    fps=[]

    out_fps = []
    out_fmap = {}   

    merged_fps = []
    merged_fmap = {}
    nmore=0

    # sort fingerprints from less to more density
    list_lens=np.sort([ len(fmap_temp[clusterOfNodes]) for clusterOfNodes in fmap_temp])
    idxFP = np.argsort([ len(fmap_temp[clusterOfNodes]) for clusterOfNodes in fmap_temp])

    # sort fingerprints and change index to fmap
    j=0
    for i in idxFP:
        fmap[j+nmore] = fmap_temp[i].copy()
        fps.append(fps_temp[i])
        j+=1

    row_array=np.array(fps)
    idxs_all=row_array.any(axis=0) #0
    array_fps=np.transpose(row_array)
    processed = []


    for ai, afp in enumerate(fps):
        # print('\n')
        # print('idx: ',ai)
        # print('fp: ',afp)

        # skip fingerprints that have already been merged
        if ai in processed: 
            continue

        # dot similarity ----------------------------------------------------------------------------------------------------------
        if similarity == 'dotsim': # ----------------------------------------------------------------------------------------------
            idxs=np.nonzero(row_array[ai,:])[0]
            sum_nonzeros=row_array[ai,idxs].sum()
            result=row_array[ai,idxs].dot(array_fps[idxs,:])  / sum_nonzeros

        # jaccard similarity ------------------------------------------------------------------------------------------------------
        elif similarity == 'jaccard': # -------------------------------------------------------------------------------------------
            sum_sonzeros=row_array[ai,idxs_all].sum()
            sums=np.sum(array_fps[idxs_all,:],axis=0)+sum_sonzeros # array_fps is transposed
            result=np.divide(row_array[ai,idxs_all].dot(array_fps[idxs_all,:]),sums)
        
        # euclidean similarity # --------------------------------------------------------------------------------------------------
        elif similarity == 'euclidean': # -----------------------------------------------------------------------------------------
            # euclidean distance:  square root of the sum of the squared differences between the two vectors
            # euclidean distance: sqrt(sum for i to N (v1[i] – v2[i])^2)
            # 1/1+d(v1,v2) i.e. inverse of Euclidean distance = similarity score 
            # using all the vector, not only idxs 
            # diffs = np.subtract(row_array,array_fps.transpose())
            # squared_diffs = np.square(diffs)
            # sums = np.sum(squared_diffs, axis=1)
            # result = np.divide(1, 1 + np.sqrt(sums))
                            
            result = np.divide(1, 1 + np.sqrt(np.sum(np.square(np.subtract(row_array,array_fps.transpose())), axis=1))) 

        # cosine similarity --------------------------------------------------------------------------------------------------------
        elif similarity == 'cosine': # ---------------------------------------------------------------------------------------------
            # need to reshape row array 
            # print(row_array.shape, array_fps.transpose().shape)
            result = cosine_similarity(row_array,array_fps.transpose())[0]

        # ==========================================================================================================================

        result[ai]=0.0 #make 0 it's own product ###### to avoid score with itself?
        # print('all fp sim scores after making 0 its own product: ', result)

        score=np.amax(result)
        # print('max score: ', score)

        bi=np.where(result == score)[0][0]
        # print('bi (idx in results where max scoring fp): ', bi)

        sum_result=np.sum(result)
        # print('sum result: ', sum_result)

        # print('bi in processed', bi in processed)
        # print('score < threshold', score<threshold)
        # print('sum result > 0', sum_result>0)

        while (bi in processed or score<threshold) and sum_result>0:
            result[bi]=0.0
            sum_result=np.sum(result)
            score=np.amax(result)
            bi=np.where(result == np.amax(result))[0][0]

        if score<threshold or bi in processed:
            continue     
        else:
            # print('ai:', ai, 'bi:', bi, 'threshold:', threshold, 'score:', score)
            # merge fingerprints
            fps[bi] = updateFingerprintProbabilistic(True, afp, fps[bi], len(fmap[ai]), len(fmap[bi])).copy() # merge in proportion of densities

            # merge nodes in both clusters
            ci = np.array(fmap[bi] + fmap[ai])
            # print('\n')
            # print('fmap[bi]', fmap[bi])
            # print('fmap[ai]', fmap[ai])

            # get first column (that contains nodes)
            cluster_nodes = ci[:,0]

            # find out it there are repeated nodes in the merged cluster and which ones
            duplicates = [item for item, count in Counter(cluster_nodes).items() if count > 1]
            # print('duplicates', duplicates)
            
            merged_array = False


            # for each duplicated node 
            for dup_node in duplicates:
                # print('dup node', dup_node)

                # select rows where first column (that contains nodes) is == dup_node, i.e., rows with duplicate nodes
                dup_rows = ci[ci[:,0] == dup_node] 
                # print('dup rows \n', dup_rows)

                # merge rows by adding up probabilities and values of flag (only one node will have flag 1, so it always adds up to 1)
                unified_row = np.array([dup_node, dup_rows[:,1].sum(), dup_rows[:,2].sum() ])
                # print('unified row', unified_row)

                # take array without dup_node
                remaining_array = ci[ci[:,0] != dup_node]
                # print('remaining array \n', remaining_array)

                # add back merged row (removing duplicates of this particular node)
                merged_array = np.vstack([remaining_array, unified_row])
                # print('merged array \n', merged_array)

            # checking whether the temp_flag is false (Numpy array is empty)
            if np.any(merged_array):
                fmap[bi] = merged_array.tolist()
            #fmap[bi] = merged_array.tolist()
            # print('fmap[bi] \n',fmap[bi])

            # mark as processed
            processed += [ai] 
            # print('processed', processed)


    ################################
    print("# Fingerprints merged: {}".format(len(processed))) 

    # add fingerprints that were not merged
    allnodes=0

    for i, fp in enumerate(fps):

        # if flag is remove and cluster has less than N nodes 
        if outliers_action=='remove' and len(fmap[i]) <= _MIN_DENSITY: 
            # tag node as outlier
            print('{} is outlier - number of members {}'.format(i, len(fmap[i])))
            print('fmap i \n', fmap[i])
            is_outlier = True

        # else, if cluster has more than N nodes
        else: 
            # tag node as not outlier
            is_outlier = False

        # if the fingerprint was not merged (processed), but it's also not an outlier
        if i not in processed and not is_outlier:
            # keep it
            merged_fps.append(fp)
            merged_fmap[len(merged_fps) - 1] = fmap[i]
            allnodes+=len(fmap[i])

        # if the fingerprint was not merged but it's an outlier
        elif i not in processed and is_outlier:
            print('fp {} is outlier'.format(fp))
            print('fmap {}'.format(fmap))

            out_fps.append(fp)
            out_fmap[len(out_fps) - 1] = fmap[i]

    # if the flag says remove and there are outliers to remove
    if outliers_action == 'remove' and len(out_fps)>0:
        with open(save_path+'outliers.pkl', 'wb') as f:  
            pickle.dump([out_fps, out_fmap], f, protocol=-1)
            print("# Fingerprints removed: {}".format(len(out_fps)))

    #print("Num nodes {}".format(sum([len(merged_fmap[listNodes]) for listNodes in merged_fmap])))

    print("# Nodes in fmap: {}\n".format(allnodes))
    return merged_fps, merged_fmap


################################################################################################################################################

def getNonOverlappingClusters(merged_fmap):
    ''' goes from overlapping clustering to non-overlapping clustering by all removing nodes 
        that have flag 0, which means their assignment wasn't the one with the highest probability, 
        but its score still passed the threshold      
    '''
    
    fmap = {}
    for cluster,nodes in merged_fmap.items():

        nodes = np.array(nodes)

        # select rows where third column (index 2) is == 0, i.e., has flag 0
        pruned_nodes = nodes[nodes[:,2] != 0.0]
        list_nodes = list(pruned_nodes[:,0].astype(int))
        fmap[cluster] = list_nodes

    return fmap

################################################################################################################################################

def fmapStruct(merged_fmap):
    '''change to original fmap structure
        fmap: (dict) fingerprint mapping of nodes to fingerprints 
              to keep track of what node belongs to what fp
        {
            fp_index: [
                row_index,
                ...
            ],
            ...
        }
    '''
    fmap = {}
    for cluster,nodes in merged_fmap.items():
        nodes = np.array(nodes)
        list_nodes = list(nodes[:,0].astype(int))
        fmap[cluster] = list_nodes
    
    return fmap

