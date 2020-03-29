# kaj rabimo?

# nardimo set listov _ _ _ 0
# random number 

# 
import random
import numpy as np
seed = 2
def generate_random_dimacs(nr_of_clauses, nr_of_literals, sample_name = 'Sample1'):
    with open("Samples/"+sample_name+".txt", 'w+') as f:
        literals = list(range(1, nr_of_literals+1))
        negations = random.Random().choices([-1, 1], k=nr_of_literals)
        literals = [negations[i]*literals[i] for i in range(nr_of_literals)]
        true_literals = random.Random().choices(literals, k=nr_of_clauses)
        #_3_sat = []
        for i in true_literals:
            candidates = [l for l in literals if l != i and l != -i]
            random.Random().shuffle(candidates)
            additional_literals = [random.Random().choice([-1, 1])*k for k in candidates[:2] ]
            curr_clause = [i, additional_literals[0], additional_literals[1]]
            random.Random().shuffle(curr_clause)
            f.write('{} {} {} 0\n'.format(curr_clause[0], curr_clause[1], curr_clause[2]))
        f.close()
        
        #( . true_literals[i] . )

generate_random_dimacs(1700, 2500)