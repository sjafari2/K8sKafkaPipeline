import pandas as pd
import csv
from mpi4py import MPI
import os.path
import numpy as np
import h5py
import math
from scipy.sparse import csr_matrix

def to_hdf5(path):
  file_reader = pd.read_csv(path, sep='\t', delimiter=' ', chunksize=5000, header=None)
  dirname = os.path.dirname(path)
  basename = os.path.basename(path)
  with h5py.File(os.path.join(dirname,basename.split('.')[0]+'.h5'), 'w') as hf:
    dataset = hf.create_dataset('edges')
    for df_chunk in file_reader:
      hf.append('edges', df_chunk)

class GraphReader:
  def __init__(self, path, partition_path):
    self.comm = MPI.COMM_WORLD
    self.rank = self.comm.Get_rank()
    self.size = self.comm.Get_size()

    # this is just for testing
    #self.rank = 10
    #self.size = 20

    tsv_file = open(partition_path)
    read_tsv = csv.reader(tsv_file, delimiter=",")
    partitions = list(read_tsv)
    partitions = np.array([[int(a[0]), int(a[1])] for a in partitions])
    partitions = np.array(sorted(partitions, key=lambda x: x[0]))
    tsv_file.close()

    self.num_vertices = np.shape(partitions)[0]
    self.vertices = partitions[:,0]
    counts = partitions[:,1]
    edges_ = np.sum(counts)
    local_edge_count = math.ceil(edges_ / self.size)

    self.local_vertices = self.get_vertices(partitions, local_edge_count)
    self.path = path
    # -----------------------------------------------------------

  def read(self):
    local_edges = []
    with open(self.path) as tsv_file:
      read_tsv = csv.reader(tsv_file, delimiter=" ")
      for row in read_tsv:
        r = list(map(int, row))
        for l in self.local_vertices:
          if l in r:
            local_edges.append(r)
            break

    local_edges = [[a[0], a[1]] if a[0] in self.local_vertices else [a[1], a[0]] for a in local_edges]
    duplicates = []
    for e in local_edges:
      if e[1] in self.local_vertices:
        duplicates.append([e[1],e[0]])
    
    local_edges = local_edges + duplicates
    local_edges = sorted(local_edges, key=lambda x: x[0])

    # up to here we have a list of vertices and a list of edges

    # map global id to indices
    self.global_mapping_id_index = {}
    self.global_mapping_index_id = {}
    for k, i in enumerate(self.vertices):
      self.global_mapping_id_index[i] = k
      self.global_mapping_index_id[k] = i

    self.mapped_local_vertices = [0]*len(self.local_vertices)
    for i, v in enumerate(self.local_vertices):
      self.mapped_local_vertices[i] = self.global_mapping_id_index[v]

    mapped_local_edges = [[self.global_mapping_id_index[e[0]], self.global_mapping_id_index[e[1]]] for e in local_edges]

    # map indices to local indices
    self.local_mapping_id_index = {}
    self.local_mapping_index_id = {}
    for k, i in enumerate(self.mapped_local_vertices):
      self.local_mapping_id_index[i] = k
      self.local_mapping_index_id[k] = i

    for e in mapped_local_edges:
      e[0] = self.local_mapping_id_index[e[0]]

    y = np.zeros(len(local_edges))
    x = np.zeros(len(local_edges))
    data = np.ones(len(local_edges))
   
    mapped_local_edges = np.array(mapped_local_edges) 

    self.sparse_matrix = csr_matrix((data, (mapped_local_edges[:,0], mapped_local_edges[:,1])), shape=(len(self.local_vertices), self.num_vertices))
    return self.sparse_matrix
 
  # this will change
  def get_vertices(self, partitions, local_edges):
    dist = [[] for i in range(self.size)]
    current_rank = 0

    count = 0
    for i, entry in enumerate(partitions): 
      dist[current_rank].append(entry[0])
      count += entry[1]
      if count > local_edges:
        current_rank += 1
        count = 0

    return dist[self.rank]
    
if __name__ == "__main__":
  #to_hdf5('../sample_data/protein.tsv') 
  reader = GraphReader('../sample_data/protein.tsv', '../sample_data/protein_node_edges.txt')
  print(reader.read())
   

