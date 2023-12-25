'''
Title: Code to evaluate the xxx metric

Author: Fulano de tal
Contact: xxx

Date: xxxx/xx
'''
import numpy as np
import pandas as pd

'''Calculate the metric

- var_metric is a list with the metric's values appended in each generation

- NMDF is a list with the normalization factor values in each generation. 
This value is the great diversity found so far, usually it is found in the first
generation, and just copied to the next generations, but if a great value is found
its value is updated.

- population is a list with all the individuals. each individual is also a list
with size of the dimensions of the problem.

- gen is the current generation of the optimization process
'''

def metric(var_metric, NMDF, population, gen):
    popsize = len(population)
 
    aux = 1 # aux should be the value of the metric for the normalization works properly
        
    # Normalization
    if(gen == 1 or aux > NMDF[-1]):
        NMDF.append(aux)
    else:
        NMDF.append(NMDF[-1])
    var_metric.append(aux / NMDF[-1])   
    
    return var_metric, NMDF