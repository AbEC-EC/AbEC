'''
Exclusion operator
'''
import itertools
import numpy as np
from aux.aux import *


params = ["REXCL"]
scope = ["GDV"]

def cp(parameters):
    if parameters["COMP_EXCLUSION"] == 1:
        if parameters["COMP_MULTIPOPULATION"] == 1:
            if 0 < parameters["COMP_EXCLUSION_REXCL"] < parameters["MAX_POS"]:
                return 1
            else:
                errorWarning("3.2.1", "algoConfig.ini", "COMP_EXCLUSION_REXCL", "The Exclusion radio should be 0 between ]0, POS_MAX[")
                sys.exit()
        elif (parameters["COMP_MULTIPOPULATION_N"] < 1):
            errorWarning("3.2.2", "algoConfig.ini", "COMP_MULTIPOPULATION_N", "The Exclusion component require the multipopulation N should be greater than 1")
            sys.exit()
    elif(parameters["COMP_EXCLUSION"] != 0):
        errorWarning("3.2.2", "algoConfig.ini", "COMP_EXCLUSION", "The Exclusion component should be 0 or 1")
        sys.exit()
    else:
        return 0

def component(pop, parameters, randomInit):
    rexcl = parameters["COMP_EXCLUSION_REXCL"]
    for sp1, sp2 in itertools.combinations(range(len(pop)), 2):
        # Subpop must have a best and not already be set to reinitialize
        if pop[sp1].best and pop[sp2].best and not (randomInit[sp1] or randomInit[sp2]):
            dist = 0
            for x1, x2 in zip(pop[sp1].best["pos"], pop[sp2].best["pos"]):
                dist += (x1 - x2)**2
            dist = np.sqrt(dist)
            if dist <= rexcl:
                if pop[sp1].best["fit"] <= pop[sp2].best["fit"]:
                    randomInit[sp1] = 1
                else:
                    randomInit[sp2] = 1
            #else:
                #print(f"{pop[sp1].id} {pop[sp1].best['pos']} -- {pop[sp2].id} {pop[sp2].best['pos']}")

    return randomInit
