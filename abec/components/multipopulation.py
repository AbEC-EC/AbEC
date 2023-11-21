'''
Title: Code to perform the Multipopulation component

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''
import numpy as np
import abec
from aux.aux import *


params = ["N"]
scope = ["INI"]

def cp(parameters):
    if parameters["COMP_MULTIPOPULATION"] == 1:
        if parameters["COMP_MULTIPOPULATION_N"] > 1:
            return 1
        else:
            errorWarning("00.1.1", "algoConfig.ini", "COMP_MULTIPOPULATION_N", "The number of populations should be greater than 1")
            return 0
    elif(parameters["COMP_MULTIPOPULATION"] != 0):
        errorWarning("3.2.2", "algoConfig.ini", "COMP_MULTIPOPULATION", "The Multipopulation component should be 0 or 1")
    else:
        return 0

def component(pop, runVars, parameters):
    subpopsize = int(parameters["POPSIZE"]/parameters["COMP_MULTIPOPULATION_N"])
    for _ in range (parameters["COMP_MULTIPOPULATION_N"]):
        pop.append(abec.population(runVars, parameters, subpopsize))

    runVars.randomInit = [0 for _ in range(1, parameters["COMP_MULTIPOPULATION_N"]+2)]

    return pop, runVars
