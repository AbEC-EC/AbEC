import numpy as np
import globalVar
import sys
from aux import *

params = ["PERC", "STD", "ELI"]

'''
Mutation operator
'''


def cp_mutation(parameters, comp=0):
    if not comp:
        elitism_factor = parameters["GA_ELI_PERC"]
        mutation_factor = parameters["GA_MUT_PERC"]
        mutation_std = parameters["GA_MUT_STD"]
    else:
        elitism_factor = parameters["COMP_MUTATION_ELI"]
        mutation_factor = parameters["COMP_MUTATION_PERC"]
        mutation_std = parameters["COMP_MUTATION_STD"]

    if parameters["COMP_MUTATION"] == 1 or comp == 0:
        if 0 < mutation_factor < 1:
            if parameters["MIN_POS"] < mutation_std < parameters["MAX_POS"]:
                return 1
            else:
                errorWarning("3.3", "algoConfig.ini", "GA/COMP_MUTATION_STD", "The percentage parameter of the Elitism component Elitism should be in the interval ]0, 1[")
                sys.exit()
                return 0
        else:
            errorWarning("3.2", "algoConfig.ini", "GA/COMP_MUTATION_PERC", "The percentage parameter of the Elitism component Elitism should be in the interval ]0, 1[")
            sys.exit()
            return 0
    elif parameters["COMP_MUTATION"] != 0:
        errorWarning("3.1", "algoConfig.ini", "COMP_MUTATION", "Component Mutation should be 0 or 1")
        sys.exit()
        return 0


def mutation(pop, parameters, comp=0):
    if not comp:
        elitism_factor = parameters["GA_ELI_PERC"]
        mutation_factor = parameters["GA_MUT_PERC"]
        mutation_std = parameters["GA_MUT_STD"]
        population_perc = parameters["GA_POP_PERC"]
    else:
        elitism_factor = parameters["COMP_MUTATION_ELI"]
        mutation_factor = parameters["COMP_MUTATION_PERC"]
        mutation_std = parameters["COMP_MUTATION_STD"]
        population_perc = 1

    for i in range(int(elitism_factor*population_perc*parameters["POPSIZE"]), int(population_perc*parameters["POPSIZE"]-2)):
        for d in range(parameters["NDIM"]):
            if globalVar.rng.random() < mutation_factor:
                dp = globalVar.rng.normal(loc = 0.0, scale = mutation_std)
                if (pop.ind[i]["pos"][d] + dp ) > parameters["MAX_POS"]:
                    pop.ind[i]["pos"][d] = parameters["MAX_POS"]
                elif (pop.ind[i]["pos"][d] + dp ) < parameters["MIN_POS"]:
                    pop.ind[i]["pos"][d] = parameters["MIN_POS"]
                else:
                    pop.ind[i]["pos"][d] += dp
    return pop
