import itertools
import numpy as np
import time
def reduce_nq_sat(n):
    """
    funkcija  sprejme dimenzijo šahovnice in vrne SAT izraz (CNF oblika) v obliki Dimacs le to zapiše na datoteko nQ_to_sat.txt
    | 1 2 3 4 |
    | 5 6 7 8 |
    | 9 10 11 12 |
    | 13 14 15 16 |
    """
    counter = 0
    problem = np.arange(1,n*n + 1).reshape(n,n)
    #ls = []
    niz = ""
    ### Najprej uredimo vse po vrsticah
    for column in problem:
        for el in column:
            niz = niz + str(el) + " "
        niz = niz + "0\n"
        counter += 1
        #ls.append(list(column))
        for comb in itertools.combinations(-column, 2):
            for el in comb:
                niz = niz + str(el) + " "
            counter += 1
            niz = niz + "0\n"
            #ls.append(list(comb))

    # Urejamo po diagonalah
    for i in range(-n+2,n-1):
        diag = np.diagonal(problem,i)
        for comb in itertools.combinations(-diag, 2):
            for el in comb:
                niz = niz + str(el) + " "
            niz = niz + "0\n"
            counter += 1
            #ls.append(list(comb))

        antidiag = np.diagonal(np.fliplr(problem),i)
        for comb in itertools.combinations(-antidiag, 2):
            for el in comb:
                niz = niz + str(el) + " "
            niz = niz + "0\n"
            counter += 1
            #ls.append(list(comb))
    niz = "p cnf " + str(n*n) + " " + str(counter) + "\n" + niz
    return niz, counter  #list_to_cnf(ls)

n = 40
niz, counter = reduce_nq_sat(n)
out = open("Homework Files-20200320/nQ_sat" + str(n) + ".txt" , "w")
out.write(niz)
out.close
#for i in range(2, 200, 2):
#    zac = time.time()
#    niz, counter = reduce_nq_sat(i)
#    print(counter)
#    kon = time.time()
#    print("Za velikost " + str(i) + " potrebujemo: " + str(kon-zac))