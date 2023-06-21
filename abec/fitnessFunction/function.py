import numpy as np

def function(x, nevals):
    fitness = 5*x[0]*np.exp(-( ((x[0])**2) + ((x[1])**2) )/4)
    return fitness
