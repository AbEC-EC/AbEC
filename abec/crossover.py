import globalVar
import sys
from encoder import *

def cp_crossover(parameters):
    if 0 < parameters["GA_CROSS_PERC"] < 1:
        return 1
    else:
        errorWarning(2.2, "algoConfig.ini", "GA_CROSS_PERC", "The percentage parameter of the Elitism component Elitism should be in the interval ]0, 1[")
        sys.exit()
        return 0


def condition(individual):
    return individual["fit"]
def tournament(pop, parameters):
    l = int(len(pop)/2)
    c = []
    for _ in range(3):
        c.append(globalVar.rng.choice(pop[:int(parameters["GA_CROSS_PERC"]*parameters["GA_POP_PERC"]*parameters["POPSIZE"])]))

    choosed = min(c, key=condition)
    return choosed

'''
Crossover operator
'''
def crossover(pop, newPop, parameters):
    for i in range(1, int((parameters["GA_POP_PERC"]*parameters["POPSIZE"] - parameters["GA_ELI_PERC"]*parameters["GA_POP_PERC"]*parameters["POPSIZE"])+1), 2):
        parent1 = tournament(pop, parameters)
        parent2 = tournament(pop, parameters)
        child1 = parent1.copy()
        child2 = parent2.copy()

        if parameters["GA_ENCODER"]:
            parent1 = encoder(parent1, parameters)
            parent2 = encoder(parent2, parameters)
            cutPoint = globalVar.rng.choice(range(len(parent1["pos"])))
            child1["pos"], child2["pos"]  = parent1["pos"][:cutPoint] + parent2["pos"][cutPoint:], \
                                            parent2["pos"][:cutPoint] + parent1["pos"][cutPoint:]
            child1 = decoder(child1, parameters)
            child2 = decoder(child2, parameters)
        else:
            cutPoint = globalVar.rng.choice(range(1, parameters["NDIM"]))
            child1["pos"], child2["pos"]  = parent1["pos"][:cutPoint] + parent2["pos"][cutPoint:], \
                                            parent2["pos"][:cutPoint] + parent1["pos"][cutPoint:]

        newPop.addInd(parameters, i)
        newPop.ind[-1]["pos"] = child1["pos"].copy()
        newPop.ind[-1]["type"] = "GA"
        newPop.addInd(parameters, i+1)
        newPop.ind[-1]["pos"] = child2["pos"].copy()
        newPop.ind[-1]["type"] = "GA"

    return newPop
