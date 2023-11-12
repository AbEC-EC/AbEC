'''
Title: Code to perform the Particle Swarm Optimization (PSO) optimizer

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''
import math
import operator
import sys
from aux.aux import errorWarning

params = ["PHI1", "PHI2", "W", "MIN_VEL", "MAX_VEL"]

def cp(parameters):
    if parameters["PSO_W"] <= 0:
        errorWarning("3.2.1", "algoConfig.ini", "PSO_W", "The W should be greater than 0")
        sys.exit()
    if parameters["PSO_PHI1"] <= 0:
        errorWarning("3.2.1", "algoConfig.ini", "PSO_PHI1", "The PHI1 should be greater than 0")
        sys.exit()
    if parameters["PSO_PHI2"] <= 0:
        errorWarning("3.2.1", "algoConfig.ini", "PSO_PHI2", "The PHI2 should be greater than 0")
        sys.exit()


def optimizer(pop, best, runVars, parameters):
    for i in range(len(pop.ind)):
        W = (parameters["PSO_W"] for _ in range(len(pop.ind[i]["pos"])))
        u1 = (runVars.rng.uniform(0, parameters["PSO_PHI1"]) for _ in range(len(pop.ind[i]["pos"])))
        u2 = (runVars.rng.uniform(0, parameters["PSO_PHI2"]) for _ in range(len(pop.ind[i]["pos"])))
        v_u1 = map(operator.mul, u1, map(operator.sub, pop.ind[i]["best_pos"], pop.ind[i]["pos"]))
        v_u2 = map(operator.mul, u2, map(operator.sub, pop.best["pos"], pop.ind[i]["pos"]))
        pop.ind[i]["vel"] = list(map(operator.mul, map(operator.add, pop.ind[i]["vel"], map(operator.add, v_u1, v_u2)), W))
        for j, speed in enumerate(pop.ind[i]["vel"]):
            if abs(speed) < parameters["PSO_MIN_VEL"]:
                pop.ind[i]["vel"][j] = math.copysign(parameters["PSO_MIN_VEL"], speed)
            elif abs(speed) > parameters["PSO_MAX_VEL"]:
                pop.ind[i]["vel"][j] = math.copysign(parameters["PSO_MAX_VEL"], speed)
        pop.ind[i]["pos"] = list(map(operator.add, pop.ind[i]["pos"], pop.ind[i]["vel"]))
        for j in range(len(pop.ind[i]["pos"])):
            if pop.ind[i]["pos"][j] > parameters["MAX_POS"]:
                pop.ind[i]["pos"][j] = parameters["MAX_POS"]
            elif pop.ind[i]["pos"][j] < parameters["MIN_POS"]:
                pop.ind[i]["pos"][j] = parameters["MIN_POS"]

    return pop, runVars
