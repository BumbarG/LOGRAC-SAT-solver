import numpy as np
import sys
from collections import defaultdict
import random
from copy import deepcopy
import time

########################################### CLASS CLAUSE ###########################################


class Clause:
    '''
    self.literals is a set of literals (class Literal)
    '''

    def __init__(self, dm_list):
        self.literals = set(dm_list)

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

    def __repr__(self):
        return str(self.literals)

    def __str__(self):
        return str(self.literals)

########################################### CLASS SENTENCE ########################################


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

########################################### SIMPLIFY FUNCTION (used in sat) ########################################

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

        ####
        # Drop clauses with observed literal
        ####

        for clause_idx in self.literal_to_clause_dict[literal]:

            # If we have multiple occurances of {literal} unit_clause
            if(self.clause_dict[clause_idx].length()) == 1:
                try:  # this try and catch will be usefull if we have multiple unit clauses with the same literal
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

                    if (self.literal_occurence_count_dict[-l] == 0):
                        self.literal_occurence_count_dict.pop(-l)
                    # For all other literals in clause update literal_to_clause_dict (remove clause index)

                    self.literal_to_clause_dict[l].remove(clause_idx)

                    # If literal does not exist in any clause, clean literal_to_clause
                    if len(self.literal_to_clause_dict[l]) == 0:
                        self.literal_to_clause_dict.pop(l)
                        self.literal_occurence_count_dict.pop(l)
                        try:
                            self.pure_literals.remove(l)
                        except:
                            pass

            self.clause_dict.pop(clause_idx)

        self.literal_to_clause_dict.pop(literal)
        self.literal_occurence_count_dict.pop(literal)

        ####
        # remove literal from clause literal_to_clause_dict
        ####

        for clause_idx in self.literal_to_clause_dict[-literal]:
            self.clause_dict[clause_idx].remove_literal(-literal)
            # 2 WATCHED LITERALS heuristic
            if self.clause_dict[clause_idx].is_unit():
                self.unit_clauses.add(clause_idx)
            if self.clause_dict[clause_idx].is_empty():
                return False
        # This try except is here because the literal occurence dict does not neccisarily have -literal as a key.
        try:
            self.literal_occurence_count_dict.pop(-literal)
        except:
            pass

        self.literal_to_clause_dict.pop(-literal)
        return True

    def add_and_copy(self, literal):
        # changes happen with clause dict, unit_clauses, literal_to_clause_dict and literal_occurence_count_dict

        new_clause_dict = deepcopy(self.clause_dict)
        # 0 is reserved for the adding literal
        new_clause_dict[0] = Clause([literal])
        new_unit_clauses = {0}

        new_literal_to_clause_dict = deepcopy(self.literal_to_clause_dict)
        new_literal_to_clause_dict[literal].append(0)

        new_literal_occurence_count_dict = deepcopy(
            self.literal_occurence_count_dict)
        new_literal_occurence_count_dict[literal] = new_literal_occurence_count_dict[literal] + 1

        return Sentence(clause_dict=new_clause_dict, pure_literals=set(), literal_occurence_count_dict=new_literal_occurence_count_dict,
                        unit_clauses=new_unit_clauses, literal_to_clause_dict=new_literal_to_clause_dict)

    def __repr__(self):
        return "{}\n{}\n{}\n{}\n".format(str(self.clause_dict), str(self.literal_to_clause_dict), str(self.unit_clauses), str(self.pure_literals))


def load_dimacs(filepath):

    # We initialize the empty structures needed to construct the starting Sentence class.
    clause_dict = defaultdict(lambda x: None)
    unit_clauses = set()
    literal_to_clause_dict = defaultdict(list)
    # (number of non negated, number of negated)
    literal_status_count = defaultdict(int)

    # Start index for clause_dict (0 is reserved for the unit clause of candidate literal in sat solver. 1 shall not be used because of reasons.)
    curr_clause_index = 2

    # We read the input dimacs formatted file and fill up the empty structures.
    with open(filepath, 'r') as f:
        for row in f.readlines():
            l = row.strip().split()
            # We skip the leading rows used for comments.
            if l[0] == "c" or l[0] == "p":
                pass
            else:
                # Create new Clause that contains all Literals (no duplicates)
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
    literal_status_count_copy = deepcopy(literal_status_count)  # .deepcopy()
    pure_literals = set([k for k, _ in literal_status_count.items(
    ) if literal_status_count_copy[-k] == 0])  # We count find all pure literals

    # NOTE: the idea is to maintain the constructed structures within the Sentence class during runtime and across the recursive calls.
    return Sentence(clause_dict=clause_dict, pure_literals=pure_literals, literal_occurence_count_dict=literal_status_count, unit_clauses=unit_clauses, literal_to_clause_dict=literal_to_clause_dict)

########################################### WRITE SOLUTION ########################################


def write_solution(solution, name):
    """
    Function writes the solution to ze file
    """
    # output = open("Homework Files-20200320/Our_solutions/"+name+"_our_solution.txt", "w")
    output = open(name, "w")
    out = str(solution)
    out = out.replace(',', '')
    out = out.replace('[', '')
    out = out.replace(']', '')
    output.write(out)
    output.close()

########################################### HEURISTICS ########################################


def jaro_wang_heuristic(sentence):
    # jaro_list = sorted( [(k, 2**(-len(v))) for k, v in sentence.literal_to_clause_dict.items()], key=lambda x: x[1], reverse=True)
    output = []
    for k, v in sentence.literal_to_clause_dict.items():
        if k >= 0:
            val = 0
            for clause in v:
                val = val + 2**(-sentence.clause_dict[clause].length())
            for clause in sentence.literal_to_clause_dict[-k]:
                val = val + 2**(-sentence.clause_dict[clause].length())
            output.append((k, val))

    return sorted(output, key=lambda x: (x[1], random.random()), reverse=True)


def rdlcs_heuristic(sentence):
    output = []
    for k, occurence in sentence.literal_occurence_count_dict.items():
        if k >= 0:
            output.append(
                (k, occurence + sentence.literal_occurence_count_dict[-k]))

    return sorted(output, key=lambda x: (x[1], random.random()), reverse=True)


######################################## SAT SOLVER ########################################

def sat(sentence: Sentence, heuristic_cand='Jaro'):
    """
    Function hopefully solves the SAT problem
    sentence ... Sentence(clause_dict=clause_dict, pure_literals=pure_literals,
                   unit_clauses = unit_clauses, literal_to_clause_dict=literal_to_clause_dict, 
                   literal_occurence_count_dict = literal_occurence_count_dict)
    heuristic_cand ... the heuristics used for choosing candidate literal. Possible options: 'Jaro', 'RDLCS', 'First in list'
    """
    # Step 1 : Unit clauses and pure literals
    # Step 2 : Stopping criterium check

    solution = []  # We initialize an empty solution.
    while (len(sentence.pure_literals) != 0) or (len(sentence.unit_clauses) != 0):
        # Unit clauses
        # We simplify our Sentence by each literal in our list of unit clauses.
        while len(sentence.unit_clauses) != 0:
            # IDEA IS THAT WE FIRST TAKE A LOOK AT THE UNIT CLAUSES THAT HAVE HIGH OCCURENCY
            # Unit choice optimization
            _max = 0
            tmp_literal = None
            tmp_clause_to_remove = None
            for tmp_clause_idx in sentence.unit_clauses:
                literal = next(
                    iter(sentence.clause_dict[tmp_clause_idx].literals))
                current_literal_count = sentence.literal_occurence_count_dict[literal]
                if _max < current_literal_count:
                    _max = current_literal_count
                    tmp_literal = literal
                    tmp_clause_to_remove = tmp_clause_idx
                elif _max == current_literal_count and bool(random.getrandbits(1)):
                    _max = current_literal_count
                    tmp_literal = literal
                    tmp_clause_to_remove = tmp_clause_idx

            # Unit choice optimization

            sentence.unit_clauses.remove(tmp_clause_to_remove)
            # tmp_clause_idx = sentence.unit_clauses.pop() # We choose a random unit clause (its id) from our set of unit clauses (pop removes also removes it from the set) credit goes to Gal XD
            # tmp_literal = next(iter(sentence.clause_dict[tmp_clause_idx].literals))
            # Simplify the expression by the literal (signed int). Returns False if this causes an empty clause.
            success = sentence.simplify(tmp_literal)
            # We add the literal (signed int) to the solution.
            solution.append(tmp_literal)
            # if simplify function was not successful we were not able to find the solution.
            if not success:
                return 0
            if len(sentence.clause_dict) == 0:
                return solution  # This should be improved after the code starts working. TODO

        # At this point and after, we do not have any unit clauses  unit_clauses = set()

        # Check for pure literals
        while (len(sentence.pure_literals) != 0) and (len(sentence.unit_clauses) == 0):  # not {}

            # Unit choice optimization
            tmp_literal = None
            _max = 0
            for literal in sentence.pure_literals:
                current_literal_count = sentence.literal_occurence_count_dict[literal]
                if _max < current_literal_count:
                    _max = current_literal_count
                    tmp_literal = literal
                elif _max == current_literal_count and bool(random.getrandbits(1)):
                    _max = current_literal_count
                    tmp_literal = literal

            # Unit choice optimization
            if tmp_literal is None:
                print('Something went wrong.')
            sentence.pure_literals.remove(tmp_literal)
            # Unit choice optimization

            # Simplify the expression by the literal (signed int). Returns False if this causes an empty clause.
            success = sentence.simplify(tmp_literal)
            # We add the literal (signed int) to the solution.
            solution.append(tmp_literal)
            # if simplify function was not successful we were not able to find the solution.
            if not success:
                return 0
            if len(sentence.clause_dict) == 0:
                return solution

    # Step 3 - Recursion, backtracing and heuristics
    # Jaroslaw Wong heuristic, RDLCS heuristics, no heuriscitc (first in dictionary)

    if heuristic_cand == 'Jaro':
        # IN TESTED CASES THE JARO WANG HEURISTIC WORKED BETTER
        improved_tuple_list = jaro_wang_heuristic(sentence)
        candidate_literal, _ = improved_tuple_list[0]

    elif heuristic_cand == 'RDLCS':
        improved_tuple_list = rdlcs_heuristic(sentence)
        candidate_literal, _ = improved_tuple_list[0]

    elif heuristic_cand == 'First in list':
        candidate_literal = random.choice(
            list(sentence.literal_to_clause_dict.keys()))
    else:
        print("you must specify the Heuristic")

    candidate_literal = random.choice([-1, 1])*candidate_literal
    branch_solution_positive = sat(sentence.add_and_copy(candidate_literal))

    if branch_solution_positive != 0:
        return (solution + branch_solution_positive)

    branch_solution_negative = sat(sentence.add_and_copy(-candidate_literal))

    if branch_solution_negative != 0:
        return (solution + branch_solution_negative)
    else:
        return 0


#######################################################################################
########                                PROGRAM                                ########
#######################################################################################


if __name__ == '__main__':
    cnf = load_dimacs(sys.argv[1])
    # zac = time.time()
    # the second Heuristic implementation is "RDLCS"
    solution = sat(cnf, 'Jaro')
    # kon = time.time()
    write_solution(solution, sys.argv[2])
    # print("Rešitev: " + str(solution) + "\n" + "v času: " + str(kon - zac))
    # print(len(solution))
