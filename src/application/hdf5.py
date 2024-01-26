import h5py
from scipy.sparse import csr_matrix

def csr2h5py(csr_matrixg,filename):
    ''' A csr matrix stores its values in 3 arrays. It is not an array or array subclass, so h5py cannot save it directly. 
        This function saves the attributes, so that the matrix can be recreated on loading '''
    # print(repr(csr_matrixg))
    # print(csr_matrixg.data)
    # print(csr_matrixg.indices)
    # print(csr_matrixg.indptr)

    f = h5py.File('{}.lock'.format(filename),'w')
    g = f.create_group('csr_matrixg')
    g.create_dataset('data', data = csr_matrixg.data)
    g.create_dataset('indptr', data = csr_matrixg.indptr)
    g.create_dataset('indices', data = csr_matrixg.indices)
    g.attrs['shape'] = csr_matrixg.shape
    f.close()
    
# -------------------------------------------------------------------------------------------------------------------------

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
    
# -------------------------------------------------------------------------------------------------------------------------

def load_csr(file):
    ''' reads in a h5py file and constructs a csr matrix; CSR constructed from (dat, (row, col)) '''
    # Check if the file exists before attempting to open it
   # if not os.path.exists(file):
   #     print(f"File '{file}' does not exist.")
   #     return None
    try:
        f = h5py.File(file,'r')
        g2 = f['csr_matrixg']
        csr_matrixg2 = csr_matrix((g2['data'][:],g2['indices'][:], g2['indptr'][:]), g2.attrs['shape'])

        f.close()
        return csr_matrixg2
    
    except Exception as e:
        print(f"Error reading {file}: {e}")
        return None
# -------------------------------------------------------------------------------------------------------------------------

def load_coo(file):
    ''' reads in a h5py file and constructs a csr matrix; COO constructed from ijv format: (data, (row, col)) '''
    f = h5py.File(file,'r')
    g2 = f['coo_matrixg']
    coo_matrixg2 = sparse.coo_matrix((g2['data'], (g2['row'], g2['col'])), g2.attrs['shape']) 
    f.close()
    return coo_matrixg2
