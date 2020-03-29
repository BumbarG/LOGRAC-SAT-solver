import random
import numpy as np

seed = 2
def generate_random_dimacs(nr_of_literals, sample_name = 'Sample2_dela'):
    f = open("Samples/"+sample_name+".txt", 'w+')
    nr_of_clauses = int(4.2*nr_of_literals)
    f.write('p cnf {} {}\n'.format(nr_of_literals, nr_of_clauses))
    
    ## 4.2 is supposed to be a critical value to determine wether the problem has satisfiable solution or not 
    literals = list(range(1, nr_of_literals+1))
    for i in range(nr_of_clauses):
        random.Random().shuffle(literals)
        clause = literals[:3]
        clause = [random.Random().choice([-1, 1])*literal for literal in clause]
        f.write('{} {} {} 0\n'.format(clause[0], clause[1], clause[2]))
    f.close()
    
        #( . true_literals[i] . )
# def generate_valid(nr_of_literals, sample_name = 'Sample1'):
#     while True:
        

generate_random_dimacs(150)