import numpy as np
import sys

name = "Homework Files-20200320/"+sys.argv[1]+"_solution.txt"
name_our = "Homework Files-20200320/Our_solutions/"+sys.argv[1]+"_our_solution.txt"

r1 = np.loadtxt(name)
r2 = np.loadtxt(name_our)

print(set(r1) == set(r2))