import numpy as np
import sys
from collections import defaultdict
import random
from copy import deepcopy

# class Literal:
#     def __init__(self, identifier, negation):
      
#         self.identifier = identifier
#         self.negation = negation
        
#     def __init__(self, dimacs_number):
#         self.identifier = abs(dimacs_number)
#         self.negation = dimacs_number < 0
  
#     def equal(self, other):
#         return self.identifier == other.identifier and self.negation == other.negation
    
#     def equal_identifier(self, other):
#         return self.identifier == other.identifier

#     def __str__(self):
#         return '-'*int(self.negation == True) + str(self.identifier)
    
class Clause:
    '''
    self.literals is a set of literals (class Literal)
    '''
    
    # def __init__(self, dm_list): 
    #     self.literals = {Literal(dimacs_number) for dimacs_number in dm_list}
    def __init__(self, dm_list): 
        self.literals = set(dm_list)

    # def __init__(self, literals):
    #     self.literals = literals

    def length(self):
        return len(self.literals)
    
    def is_unit(self):
        return self.length() == 1

    def is_empty(self):
        return self.length() == 0

    def contains(self, x):
        return x in self.literals

    def remove_literal(self, x):
        self.literals.remove(x)

    # def __repr__(self):
    #     out = '('
    #     for el in self.literals:
    #         out  = out + el.__str__() + ' '
    #     return out[:-1]+ ')'

    def __repr__(self):
        return str(self.literals)

    def __str__(self):
       return str(self.literals)


class Sentence:

    def __init__(self, clause_dict, pure_literals, literal_occurence_count_dict, unit_clauses, literal_to_clause_dict):
        '''
        clause_dict ... dictionary of form clause id: clause (positive integer: Class) (positive integers from 2 --> len(clauses)) 
        [Note: in the above dictionary the key/id 0 is reserved for the temporary unit clause added when entering a new branch.]
        literal_to_clause_dict ... dictionary of form literal(signed integer): list of ids_of_clauses_it_occurs_in
        literal_occurence_count_dict ... dictionary of form literal (signed integer): number of occurences in sentence (int)
        pure_literals ... set of literal identifiers (signed integers)
        unit_clauses ... set of clause indexes 
        '''
        self.clause_dict = clause_dict
        self.pure_literals = pure_literals
        self.unit_clauses = unit_clauses
        self.literal_to_clause_dict = literal_to_clause_dict
        self.literal_occurence_count_dict = literal_occurence_count_dict
        
    def simplify(self, literal):
        """
        Function creates new instance of the Sentence with simplified properties
        literal ... the literal (signed int)
        """
        # if we entered simplify from unit clauses and the same literal occurs in pure_literals
        try:
            self.pure_literals.remove(literal)
        except:
            pass

        # we set the literal occurence (signed int) to 0 due to it being removed from the Sentence 
        self.literal_occurence_count_dict[literal] = 0
        self.literal_occurence_count_dict[-literal] = 0

        ####
        ### Drop clauses with observed literal
        ####
        
        for clause_idx in self.literal_to_clause_dict[literal]:
            
            # If we have multiple occurances of {literal} unit_clause
            if(self.clause_dict[clause_idx].length()) == 1:
                try: # this try and catch will be usefull if we have multiple unit clauses with the same literal
                    self.unit_clauses.remove(clause_idx)
                except:
                    pass

            # Removing indexes of observed clause from literal_to_clause_dict
            literals = self.clause_dict[clause_idx].literals
            for l in literals:
                if l != literal:
                    self.literal_occurence_count_dict[l] = self.literal_occurence_count_dict[l] - 1
                    if self.literal_occurence_count_dict[l] == 0 and self.literal_occurence_count_dict[-l] != 0:
                        self.pure_literals.add(-l)   
                    
                    # For all other literals in clause update literal_to_clause_dict (remove clause index)
                    
                    
                    self.literal_to_clause_dict[l].remove(clause_idx)
                 

                    # If literal does not exist in any clause, clean literal_to_clause
                    if len(self.literal_to_clause_dict[l]) == 0:
                        self.literal_to_clause_dict.pop(l)

            
            self.clause_dict.pop(clause_idx)
            # try:
            #     self.unit_clauses.remove(clause_idx)
            # except(ValueError e):

        self.literal_to_clause_dict.pop(literal)

        ####
        ### remove literal from clauseliteral_to_clause_dict
        ####
        
        for clause_idx in self.literal_to_clause_dict[-literal]:
            self.clause_dict[clause_idx].remove_literal(-literal)
            if self.clause_dict[clause_idx].is_unit():
                self.unit_clauses.add(clause_idx)
            if self.clause_dict[clause_idx].is_empty():
                return False

        self.literal_to_clause_dict.pop(-literal)
        return True
        
        
    def add_and_copy(self, literal):
        # changes happen with clause dict, unit_clauses, literal_to_clause_dict and literal_occurence_count_dict
        
        new_clause_dict = deepcopy(self.clause_dict) # .deepcopy()
        new_clause_dict[0] = Clause([literal])  # Credit for idea goes to Špela (XD) 0 is reserved for the adding literal
        new_unit_clauses = {0}

        new_literal_to_clause_dict = deepcopy(self.literal_to_clause_dict) # .deepcopy()
        new_literal_to_clause_dict[literal].append(0)
        
        new_literal_occurence_count_dict = deepcopy(self.literal_occurence_count_dict) # .deepcopy()
        new_literal_occurence_count_dict[literal] = new_literal_occurence_count_dict[literal] + 1

        return Sentence(new_clause_dict, self.pure_literals , new_literal_occurence_count_dict, new_unit_clauses, new_literal_to_clause_dict)

    def __repr__(self):
        return "{}\n{}\n{}\n{}\n".format(str(self.clause_dict), str(self.literal_to_clause_dict), str(self.unit_clauses), str(self.pure_literals))
    
def load_dimacs(filepath):
    
    # We initialize the empty structures needed to construct the starting Sentence class.
    clause_dict = dict()
    unit_clauses = set()
    literal_to_clause_dict = defaultdict(list)
    literal_status_count = defaultdict(int) # (number of non negated, number of negated)

    # Start index for clause_dict (0 is reserved for the unit clause of candidate literal in sat solver. 1 shall not be used because of reasons.)
    curr_clause_index = 2
    
    # We read the input dimacs formatted file and fill up the empty structures.
    with open(filepath, 'r') as f:
        for row in f.readlines():
            l = row.strip().split(' ')
            # We skip the leading rows used for comments.
            if l[0] == "c" or l[0] == "p":
                pass
            else:
                #Create new Clause that contains all Literals (no duplicates) 
                mapped_row = list(set(map(int, l[:-1])))
                if len(mapped_row) == 1:
                    # We fill up the list of unit clauses during construction.
                    unit_clauses.add(curr_clause_index) 
                for val in mapped_row:
                    # Update literal_to_clause_dict and literal_status_count
                    literal_to_clause_dict[val].append(curr_clause_index)
                    literal_status_count[val] = literal_status_count[val] + 1
                clause_dict[curr_clause_index] = Clause(mapped_row)
                curr_clause_index = curr_clause_index + 1  
    
    # We create a copy of the count to ensure that the defaultdict does not change during the iteration
    literal_status_count_copy = deepcopy(literal_status_count) # .deepcopy()       
    pure_literals = set([k for k, _ in literal_status_count.items() if literal_status_count_copy[-k] == 0]) # We count find all pure literals 
    
    # NOTE: the idea is to maintain the constructed structures within the Sentence class during runtime and across the recursive calls.
    return Sentence(clause_dict=clause_dict, pure_literals=pure_literals, literal_occurence_count_dict=literal_status_count, unit_clauses = unit_clauses, literal_to_clause_dict=literal_to_clause_dict)


def write_solution(solution, name):
    """
    Function writes the solution to ze file
    """
    output = open("Homework Files-20200320/Our_solutions/"+name+"_our_solution.txt", "w")
    out = str(solution)
    out = out.replace(',', '')
    out = out.replace('[', '')
    out = out.replace(']', '')
    output.write(out)
    output.close()
      
def sat(sentence: Sentence):
    """
    Function hopefully solves the SAT problem
    sentence ... Sentence(clause_dict=clause_dict, pure_literals=pure_literals,
                   unit_clauses = unit_clauses, literal_to_clause_dict=literal_to_clause_dict, 
                   literal_occurence_count_dict = literal_occurence_count_dict)
    """
    # Step 1 : Unit clauses and pure literals
    # Step 2 : Stopping criterium check
    solution = [] # We initialize an empty solution.
    tmp_literal = None # initialize the tmp literal we are using during the simplify step.
    
    #print('Smo v whilu', len(sentence.pure_literals), len(sentence.unit_clauses))
    while (len(sentence.pure_literals)!=0) or (len(sentence.unit_clauses) != 0):
        #print('Ostržek in whale (in While)', len(sentence.pure_literals), len(sentence.unit_clauses))
        # Unit clauses
        while len(sentence.unit_clauses) != 0: # We simplify our Sentence by each literal in our list of unit clauses.
            tmp_clause_idx = sentence.unit_clauses.pop() # We choose a random unit clause (its id) from our set of unit clauses (pop removes also removes it from the set) credit goes to Gal XD 
            tmp_literal = next(iter(sentence.clause_dict[tmp_clause_idx].literals)) # We retrieve the literal (signed int) corresponding the above clause.
            success = sentence.simplify(tmp_literal) # Simplify the expression by the literal (signed int). Returns False if this causes an empty clause.
            solution.append(tmp_literal) # We add the literal (signed int) to the solution.
            if not success: # if simplify function was not successful we were not able to find the solution.
                return 0
            if len(sentence.clause_dict) == 0:
                return list(set(solution)) # This should be improved after the code starts working. TODO

        ### At this point and after, we do not have any unit clauses  unit_clauses = set()

        # Check for pure literals
        while (len(sentence.pure_literals) != 0) and (len(sentence.unit_clauses) == 0):
            tmp_literal = sentence.pure_literals.pop() # we chose a random pure literal (signed int) from our set of pure literals (pop removes also removes it from the set)
            success = sentence.simplify(tmp_literal) # Simplify the expression by the literal (signed int). Returns False if this causes an empty clause.
            solution.append(tmp_literal) # We add the literal (signed int) to the solution.
            if not success: # if simplify function was not successful we were not able to find the solution.
                return 0
            if len(sentence.clause_dict) == 0:
                return list(set(solution)) # this should be improved after the code starts working TODO

    # print("Gremo mi po svoje (Rekurzija)")
    # Step 3 - Recursion and backtracing
    for candidate_literal in sentence.literal_to_clause_dict.keys(): # Here we should do further optimization. TODO
        branch_solution = sat(sentence.add_and_copy(candidate_literal))
        # If we have valid sollution than we break out of loop = out of search in further branches
        if branch_solution != 0:
            break

    if branch_solution == 0: # No solution was found.
        return 0

    return list(set(solution + branch_solution)) # TODO

if __name__ == '__main__':
    
    cnf = load_dimacs(sys.argv[1])
    solution = sat(cnf)
    name = sys.argv[1].split('/')[-1].split('.')[0]
    #print("Rešitev: " + str(solution))
    write_solution(solution, name)
