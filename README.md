# LOGRAC---SAT-solver
A SAT solver implementation in Python for the course Logika v računalništvu (Faculty of Mathematics and Physics, Slovenia, 2020). This program is using the implementation of DPLL algorithm (with improvements) that is used to solve SAT problems.

## Getting Started

### Prerequisites

The only prerequisite that you need is Python 3.7 or higher and library `numpy`.

If numpy is not installed, install it with pip
```
pip install numpy
```

### Tests and generating new instances

There are also example files in this repository that you can try out. Another possibility is creation of your own SAT instances (3-SAT) that are generated using the `generator.py` file.

Creating new instance: 
```
python generator.py <num_of_variables> <name_of_the_file>
```
Generator has been created that creates random 3-SAT formulas in DIMACS format that are **not necessarily** solvable.  

Consider our submitted sample to be: Sample1_dela.txt (3-SAT with 150 literals and 630 clauses)

The solution to the above sample was on (our machines) computed in between 2 and 40 seconds (as our algorithm includes some randomness for lower average runtimes.).

## Running the program

Entire program is located in `SAT_solver.py` file.
```
python SAT_solver.py <input_path> <output_path>
```

Example usage:
```
python SAT_solver.py "Samples/Sample1_dela.txt" "Samples/Solutions/Sample1_solution.txt"
```


If you would like to see the solution, the length of it and the time it took to compute the problem just uncomment the lines at the end of the file (prints in terminal).

## Improvements to the simple DPLL algorithm

- Efficient data structure (usage of dictionaries to avoid iterations over all the clauses (or variables) and usage of sets)
- Implementation of the Heuristic 2-watched literals (indirectly, through updating the dictionaries - when the length of the clause becomes 1 it is immediately added to unit clauses)
- Implementation of 2 Heuristics for the optimization of the choice of the "best" Free_Candidate_literal before branching.
  - Jeroslow-Wang Heuristic
  - RDLCS Heuristic
- Implementation of the Heuristic for the choice of the unit clauses and the choice of pure literals (using the unit/pure literal that has the highest occurence in the sentence. If there are multiple literals with the same occurence one among them is randomly taken). 'This is our own Heuristic. It decreased completion time on the cases we tested.' 

## Authors

* **Špela Čopi**
* **Gal Bumbar**
* **Blaž Dobravec**

## License
This project is licensed under the MIT License - see the `LICENCE.md` file for details
