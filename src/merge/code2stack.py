from functions import *

path = 'consumer_output/'
n = 2

file_assignment = assignConsumerOutput2Algorithm(path , n)
print('file_assignment {}'.format(file_assignment))

stacked_csr = stackCSR(path, file_assignment[0])
# stacked_csr.shape

num_instances = len(file_assignment)

for files2stack in file_assignment:
    
    stacked_csr_matrixg = stackCSR(path, files2stack)
    print('files {} stacked into 1 csr_matrix'.format(files2stack))
        
    # we can put here code to run the algorithm with stacked_csr_matrixg as an input
