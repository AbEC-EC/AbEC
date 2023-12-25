'''
Title: Code to evaluate the Pairwise Distances metric (Dpw)*

* A.L. Barker and W.N. Martin. Dynamics of a distance-based population diversity measure. In
Proceedings of the 2000 Congress on Evolutionary Computation. CEC00 (Cat. No.00TH8512),
volume 2, pages 1002–1009 vol.2, 2000

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''
import numpy as np
import pandas as pd

# calculate the metric
def metric(var_metric, NMDF, population, gen):
    popsize = len(population)
    aux = 0
    aux2 = 0

    # Caclulate the difference euclidean distance between the individuals
    # and normalize with the population size
    for ind1_i, ind1 in enumerate(population, start=1):
        for ind2 in population[:ind1_i-1]:
            for d1, d2 in zip(ind1, ind2):
                aux += (d1-d2)**2
            aux2 += np.sqrt(aux)
            aux = 0
    
    aux = 2*(aux2)/(popsize-1)
    aux = aux / popsize
        
    # Normalization
    if(gen == 1 or aux > NMDF[-1]):
        NMDF.append(aux)
    else:
        NMDF.append(NMDF[-1])
    var_metric.append(aux / NMDF[-1])   
    
    return var_metric, NMDF