import math
import operator
import globalVar

'''
Apply PSO on the particle
'''
def pso(ind, best, parameters):
    W = (parameters["PSO_W"] for _ in range(len(ind["pos"])))
    u1 = (globalVar.rng.uniform(0, parameters["PSO_PHI1"]) for _ in range(len(ind["pos"])))
    u2 = (globalVar.rng.uniform(0, parameters["PSO_PHI2"]) for _ in range(len(ind["pos"])))
    v_u1 = map(operator.mul, u1, map(operator.sub, ind["best_pos"], ind["pos"]))
    v_u2 = map(operator.mul, u2, map(operator.sub, best["pos"], ind["pos"]))
    #part.speed = list(map(operator.add, part.speed, map(operator.add, v_u1, v_u2)))
    ind["vel"] = list(map(operator.mul, map(operator.add, ind["vel"], map(operator.add, v_u1, v_u2)), W))
    for i, speed in enumerate(ind["vel"]):
        if abs(speed) < parameters["PSO_MIN_VEL"]:
            ind["vel"][i] = math.copysign(parameters["PSO_MIN_VEL"], speed)
        elif abs(speed) > parameters["PSO_MAX_VEL"]:
            ind["vel"][i] = math.copysign(parameters["PSO_MAX_VEL"], speed)
    ind["pos"] = list(map(operator.add, ind["pos"], ind["vel"]))

    return ind
