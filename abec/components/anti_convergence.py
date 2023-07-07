'''
Anti-convergence operator
'''

import numpy as np
import copy
from aux.aux import *


params = ["RCONV"]
scope = ["GDV"]

def cp(parameters):
    if parameters["COMP_ANTI_CONVERGENCE"] == 1:
        if parameters["COMP_MULTIPOPULATION"] == 1:
            if 0 < parameters["COMP_ANTI_CONVERGENCE_RCONV"] < parameters["MAX_POS"]:
                return 1
            else:
                errorWarning("3.3.1", "algoConfig.ini", "COMP_ANTI_CONVERGENCE_RCONV", "The Anti convergence radio should be 0 between ]0, POS_MAX[")
                sys.exit()
        elif (parameters["COMP_MULTIPOPULATION_N"] < 1):
            errorWarning("3.2.2", "algoConfig.ini", "COMP_MULTIPOPULATION_N", "The Anti-convergence component require the multipopulation N should be greater than 1")
            sys.exit()
    elif(parameters["COMP_ANTI_CONVERGENCE"] != 0):
        errorWarning("3.3.2", "algoConfig.ini", "COMP_ANTI_CONVERGENCE", "The Anti convergence component should be 0 or 1")
        sys.exit()
    else:
        return 0

def component(pop, parameters, randomInit):
    rconv = parameters["COMP_ANTI_CONVERGENCE_RCONV"]
    wsubpopId = None
    wsubpop = None
    nconv = 0
    for subpopId, subpop in enumerate(pop):
        # Compute the diameter of the swarm
        for ind1Id, ind1 in enumerate(subpop.ind, 1):
            for ind2Id, ind2 in enumerate(subpop.ind, 1):
                if (ind1 == ind2):
                    break
                for x1, x2 in zip(ind1["pos"], ind2["pos"]):
                    d = np.sqrt( (x1 - x2)**2 ) # Euclidean distance between the components
                    if d >= rconv:  # If any is greater or equal rconv, not converged
                        nconv += 1
                        break
        # Search for the worst swarm according to its global best
        if not wsubpop or subpop.best["fit"] < wsubpop.best["fit"]:
            wsubpopId = subpopId
            wsubpop = copy.deepcopy(subpop)

    # If all swarms have converged, remember to randomize the worst
    if nconv == 0:
        randomInit[wsubpopId] = 1

    return randomInit
