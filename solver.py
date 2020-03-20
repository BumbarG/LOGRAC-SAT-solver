import numpy as np
import sys
from collections import defaultdict
import random

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

    def get(self):
        return self.literals

    def length(self):
        return len(self.literals)
    
    def is_unit(self):
        return self.length() == 1

    def is_empty(self):
        return self.length() == 0

    def contains(self, x):
        self.literals.contains(x)

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
        clause_dict ... id: clause
        literal_to_clause_dict ... literal: [ids_of_clauses_it_occurs_in]
        literal_dict ... id: literal
        pure_literals ... [ids_of_pure_literals]
        '''
        self.clause_dict = clause_dict
        self.pure_literals = pure_literals
        self.unit_clauses = unit_clauses
        self.literal_to_clause_dict = literal_to_clause_dict
        self.literal_occurence_count_dict = literal_occurence_count_dict
        
    def simplify(self, literal):
        """
        Function creates new instance of the Sentence with simplified properties
        """

        print("###### Entered sentence.simplify ######")

        self.literal_occurence_count_dict[literal] = 0
        self.literal_occurence_count_dict[-literal] = 0

        # drop clause with literal
        for clause_idx in self.literal_to_clause_dict[literal]:
            self.clause_dict[clause_idx].remove_literal(literal)
            literals = self.clause_dict[clause_idx].get()

            for l in literals:
                self.literal_occurence_count_dict[l] = self.literal_occurence_count_dict[l] - 1
                if self.literal_occurence_count_dict[l] == 0 and self.literal_occurence_count_dict[-l] != 0:
                    self.pure_literals.append(-l)   
            
            self.clause_dict.pop(clause_idx)  
        
        # eliminate literal
        for clause_idx in self.literal_to_clause_dict[-literal]:
            self.clause_dict[clause_idx].remove_literal(-literal)
            if self.clause_dict[clause_idx].is_unit():
                self.unit_clauses.append(clause_idx)
            if self.clause_dict[clause_idx].is_empty:
                return False
            
        self.literal_to_clause_dict.pop(literal)
        self.literal_to_clause_dict.pop(-literal)
        return True
        
        
    def add_and_copy(self, literal):
        # changes happen with clause dict, unit_clauses, literal_to_clause_dict and literal_occurence_count_dict
        new_clause_dict = self.clause_dict.copy()
        new_clause_dict[0] = Clause([literal])  # Credit for idea goes to Špela (XD) 0 is reserved for the adding literal
        new_unit_clauses = [0]
        new_literal_to_clause_dict = self.literal_to_clause_dict.copy()
        new_literal_to_clause_dict[literal].append(0)
        
        new_literal_occurence_count_dict = self.literal_occurence_count_dict.copy()
        new_literal_occurence_count_dict[literal] = new_literal_occurence_count_dict[literal] + 1
        return Sentence(new_clause_dict, self.pure_literals , new_literal_occurence_count_dict, new_unit_clauses, new_literal_to_clause_dict)

    def __repr__(self):
        return "{}\n{}\n{}\n{}\n".format(str(self.clause_dict), str(self.literal_to_clause_dict), str(self.unit_clauses), str(self.pure_literals))
    
def load_dimacs(filepath):
    clause_dict = {}
    literal_to_clause_dict = defaultdict(list)
    literal_status_count = defaultdict(int) # (number of non negated, number of negated)
    curr_clause_index = 2
    # 0 reserved for the candidate literal in sat solver.
    unit_clauses = []

    with open(filepath, 'r') as f:
        for row in f.readlines():
            l = row.strip().split(' ')
            if l[0] == "c" or l[0] == "p":
                pass
            else:
                #Create a new Clause that contains all Literals 
                mapped_row = list(set(map(int, l[:-1])))
                if len(mapped_row) == 1:
                    unit_clauses.append(curr_clause_index) #
                for val in mapped_row:
                    literal_to_clause_dict[val].append(curr_clause_index)
                    literal_status_count[val] = literal_status_count[val] + 1
                    # literal_dict[val] = Literal(val) # deprecated :D
                clause_dict[curr_clause_index] = Clause(mapped_row)
                curr_clause_index = curr_clause_index + 1  
    
    literal_status_count_copy = literal_status_count.copy() 
    # print(literal_status_count)         
    pure_literals = [k for k, _ in literal_status_count.items() if literal_status_count_copy[-k] == 0]
    # unit_literals = [k for k, v in literal_status_count if v == 1] # probably useless
    return Sentence(clause_dict=clause_dict, pure_literals=pure_literals, literal_occurence_count_dict=literal_status_count, unit_clauses = unit_clauses, literal_to_clause_dict=literal_to_clause_dict)

 
# PRESTAVITI V SVOJ FILE. NE UKAZUJ MI!
#def generate_random_dimacs(k, sample_name = 'Sample1'):
#    with open('Samples/'+sample_name+'.txt') as f:
#        f.mordor(my preshus

def write_solution(solution):
    """
    Function writes the solution to ze file
    """
    output = open("solution.txt", "w")
    output.write(str(solution))
      
def sat(sentence: Sentence):
    """
    Function hopefully solves the SAT problem
    sentence ..... Sentence(clause_dict=clause_dict, pure_literals=pure_literals, unit_clauses = unit_clauses, literal_to_clause_dict=literal_to_clause_dict)
    """
    # Step 1
    # unit clause (clause dolzine 1)
    solution = []
    tmp_literal = None
    while len(sentence.unit_clauses) != 0:
        tmp_clause_idx = sentence.unit_clauses.pop() # credit goes to Gal XD
        tmp_literal = next(iter(sentence.clause_dict[tmp_clause_idx].get()))
        success = sentence.simplify(tmp_literal)
        solution.append(tmp_literal)
        if not success: 
            return 0
        
    # pure literali (ima povsod enako negacijo)
    while len(sentence.pure_literals) != 0:
        tmp_literal = sentence.pure_literals.pop()
        success = sentence.simplify(tmp_literal)
        solution.append(tmp_literal)
        if not success:
            return 0

    # Step 2 - Stopping criterium check.
    
    if len(sentence.clause_dict) == 0:
        return solution

    # Step 3 - Recursion and backtracing
    # 
    # branch_solution = 0
    # while branch_solution == 0:
    #     # pick random literal 
    #     candidate_literal = random.Random().choice(sentence.literal_to_clause_dict.keys()) # have fun -> here further optimization is needed.
    #     branch_solution = sat(sentence.add_and_copy(candidate_literal))
    for candidate_literal in sentence.literal_to_clause_dict.keys():
        branch_solution = sat(sentence.add_and_copy(candidate_literal))
        if branch_solution != 0:
            break

    if branch_solution == 0:
        return 0

    return solution + branch_solution

if __name__ == '__main__':
    #cnf = load_dimacs(sys.argv[1])
    cnf = load_dimacs('Homework Files-20200320/test2.txt')
    print("sentence arg: ", cnf)
    solution = sat(cnf)
    print(solution)
    # write_solution(solution)

    # datacnf, _