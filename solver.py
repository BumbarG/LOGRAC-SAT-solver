import numpy as np
import sys
from collections import defaultdict

class Literal:
    def __init__(self, identifier, negation):
      
        self.identifier = identifier
        self.negation = negation
        
    def __init__(self, dimacs_number):
        self.identifier = abs(dimacs_number)
        self.negation = dimacs_number < 0
  
    def equal(self, other):
        return self.identifier == other.identifier and self.negation == other.negation
    
    def equal_identifier(self, other):
        return self.identifier == other.identifier

    def __str__(self):
        return '-'*int(self.negation == True) + str(self.identifier)
    
class Clause:
    '''
    self.literals is a set of literals (class Literal)
    '''
    
    def __init__(self, dm_list): 
        self.literals = {Literal(dimacs_number) for dimacs_number in dm_list}

    # def __init__(self, literals):
    #     self.literals = literals

    def length(self):
        return len(self.literals)
    
    def is_unit(self):
        return self.length() == 1

    def contains(self, x):
        self.literals.contains(x)

    def __repr__(self):
        out = '('
        for el in self.literals:
            out  = out + el.__str__() + ' '
        return out[:-1]+ ')'

    def __str__(self):
        out = '('
        for el in self.literals:
            out  = out + el.__str__() + ' '
        return out[:-1]+ ')'


class Sentence:

    def __init__(self, clause_dict, literal_dict, pure_literals, literal_to_clause_dict):
        '''
        clause_dict ... id: clause
        literal_to_clause_dict ... literal: [ids_of_clauses_it_occurs_in]
        literal_dict ... id: literal
        pure_literals ... [ids_of_pure_literals]
        '''
        self.clause_dict = clause_dict
        self.literal_dict = literal_dict 
        self.pure_literals = pure_literals
        self.literal_to_clause_dict = literal_to_clause_dict

    def __repr__(self):
        pass
    
def load_dimacs(filepath):
    clause_dict = {}
    literal_to_clause_dict = {}
    # pure_literals = []
    literal_dict = {}
    literal_status_count = defaultdict(lambda: (0, 0)) # (number of non negated, number of negated)
    curr_clause_index = 0
    curr_literal_index = 0

    with open(filepath, 'r') as f:
        for row in f.readlines():
            l = row.strip().split(' ')
            if l[0] == "c" or l[0] == "p":
                pass
            else:
                #Create a new Clause that contains all Literals 
                mapped_row = list(map(int, l[:-1]))
                # print(mapped_row)
                for val in mapped_row:
                    abs_val = abs(val)
                    (a, b) = literal_status_count[abs_val]
                    # if abs_val == 23:
                    #     print(a, b)
                    if val >= 0:
                        literal_status_count[abs_val] = (a+1, b)
                    else:
                        literal_status_count[abs_val] = (a, b+1)
                    
                output.append(Clause(mapped_row))
                
    is_pure_dict = {k: ((v[1] == 0) or (v[0] == 0)) for k, v in literal_status_count.items()}
    pure_literals = 
    #print(literal_status_count)
    #print(is_pure_dict)
    return output, is_pure_dict

def write_solution(solution):
    """
    Function writes the solution to ze file
    """
    
    pass
    

def sat(cnf):
    """
    Function hopefully solves the SAT problem
    """
    # unit clause (clause dolzine 1)

    # pure literali (ima povsod enako negacijo)
    
    # 



    #
    pass


if __name__ == '__main__':
    # cnf = load_dimacs(sys.argv[1])
    cnf, _ = load_dimacs('Homework Files-20200320/test.txt')
    #print("cnf: ", cnf)
    solution = sat(cnf)
    write_solution(solution)

    