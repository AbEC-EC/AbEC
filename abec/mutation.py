import numpy as np
import globalVar
import sys
from aux import *
from encoder import *

'''
Mutation operator
'''

def cp_mutation(parameters, comp=0):
    if not comp:
        elitism_factor = parameters["GA_ELI_PERC"]
        mutation_factor = parameters["GA_MUT_PERC"]
        mutation_std = parameters["GA_MUT_STD"]
    else:
        elitism_factor = parameters["COMP_MUT_ELI"]
        mutation_factor = parameters["COMP_MUT_PERC"]
        mutation_std = parameters["COMP_MUT_STD"]

    if parameters["COMP_MUT"] == 1 or comp == 0:
        if 0 < mutation_factor < 1:
            if parameters["MIN_POS"] < mutation_std < parameters["MAX_POS"]:
                return 1
            else:
                errorWarning("3.3", "algoConfig.ini", "GA/COMP_MUT_STD", "The percentage parameter of the Elitism component Elitism should be in the interval ]0, 1[")
                sys.exit()
                return 0
        else:
            errorWarning("3.2", "algoConfig.ini", "GA/COMP_MUT_PERC", "The percentage parameter of the Elitism component Elitism should be in the interval ]0, 1[")
            sys.exit()
            return 0
    elif parameters["COMP_MUT"] != 0:
        errorWarning("3.1", "algoConfig.ini", "COMP_MUT", "Component Elitism should be 0 or 1")
        sys.exit()
        return 0


def mutation(pop, parameters, comp=0):
    if not comp:
        elitism_factor = parameters["GA_ELI_PERC"]
        mutation_factor = parameters["GA_MUT_PERC"]
        mutation_std = parameters["GA_MUT_STD"]
        population_perc = parameters["GA_POP_PERC"]
    else:
        elitism_factor = parameters["COMP_MUT_ELI"]
        mutation_factor = parameters["COMP_MUT_PERC"]
        mutation_std = parameters["COMP_MUT_STD"]
        population_perc = 1

    for i in range(int(elitism_factor*population_perc*parameters["POPSIZE"]), int(population_perc*parameters["POPSIZE"]-2)):
        if parameters["GA_ENCODER"]:
            for j in range(parameters["GA_INDSIZE"]):
                if globarVar.rng.random() < mutation_factor:
                    pop.ind[i] = encoder(pop.ind[i], parameters)
                    pop.ind[i]["pos"][j] = 1 - pop.ind[i]["pos"][j]
                    pop.ind[i] = decoder(pop.ind[i], parameters)
        else:
            for d in range(parameters["NDIM"]):
                if globalVar.rng.random() < mutation_factor:
                    pop.ind[i]["pos"][d] += globalVar.rng.normal(loc = 0.0, scale = mutation_std)

    return pop
