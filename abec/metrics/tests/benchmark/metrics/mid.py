'''
Title: Code to evaluate the Minimum Individual Distance Metric

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''
import numpy as np

# calculate the metric
def metric(var_metric, NMDF, population, gen):
    minDist = [-1 for _ in range(len(population))] # Initialize the min dist as inf
    
    for ind1_i, ind1 in enumerate(population):
        for ind2 in population:
            sumD = 0
            if (ind1 == ind2):
                continue
            
            for x1, x2 in zip(ind1, ind2):
                sumD += (x1 - x2)**2    
            d = np.sqrt(sumD) # Euclidean distance
                
            if d < minDist[ind1_i] or minDist[ind1_i] == -1:
                #print(d)
                minDist[ind1_i] = d

    aux = sum(minDist)
    
    # Normalization
    if(gen == 1 or aux > NMDF[-1]):
        NMDF.append(aux)
    else:
        NMDF.append(NMDF[-1])
    var_metric.append(aux / NMDF[-1])   
    
    return var_metric, NMDF