'''
Exclusion operator
'''
import itertools
import numpy as np
import globalVar
import abec

params = ["N"]

def cp_multipopulation(parameters):
    if parameters["COMP_MULTIPOPULATION"] == 1:
        if parameters["COMP_MUTLIPOPULATION_N"] > 1:
            return 1
        else:
            errorWarning("00.1.1", "algoConfig.ini", "COMP_MULTIPOPULATION_N", "The number of populations should be greater than 1")
            sys.exit()
            return 0
    elif(parameters["COMP_MULTIPOPULATION"] != 0):
        errorWarning("3.2.2", "algoConfig.ini", "COMP_MULTIPOPULATION", "The Multipopulation component should be 0 or 1")
        sys.exit()
        return 0

def multipopulation(pop, parameters):
    if cp_multipopulation(parameters):
        for _ in range (parameters["COMP_MULTIPOPULATION_N"]):
            pop.append(abec.population(parameters))

        globalVar.randomInit = [0 for _ in range(1, parameters["COMP_MULTIPOP_N"]+2)]
    else:
        pop.append(abec.population(parameters))
        globalVar.randomInit = [0]

    return pop

