import sys
import copy

'''
Elitism operator
'''
def cp_elitism(parameters):
    if 0 < parameters["GA_ELI_PERC"] < 1:
        return 1
    else:
        errorWarning(1.2, "algoConfig.ini", "GA_ELI_PERC", "The percentage parameter of the Elitism component Elitism should be in the interval ]0, 1[")
        sys.exit()
        return 0



def elitism(pop, newPop, parameters):
    for i in range(int(parameters["GA_ELI_PERC"]*parameters["GA_POP_PERC"]*parameters["POPSIZE"])):
        newPop.addInd(parameters)
        #print(f"newPop.ind[{i}]: {newPop.ind[i]}")
        #print(f"pop[{i}]: {pop[i]}")
        #e()
        newPop.ind[i] = copy.deepcopy(pop[i])
        newPop.ind[i]["ae"] = 1

    return newPop
