import aux.globalVar as globalVar
import abec
import copy
from aux.aux import errorWarning

'''
    DE optimizer
'''

params = ["F", "CR"]

def cp(parameters):
    if parameters["DE_F"] <= 0:
        errorWarning("3.2.1", "algoConfig.ini", "DE_F", "The F should be greater than 0")
        sys.exit()
    if parameters["DE_CR"] <= 0:
        errorWarning("3.2.1", "algoConfig.ini", "DF_CR", "The CR should be greater than 0")
        sys.exit()


def de(pop, parameters):
    tempPop = copy.deepcopy(pop)
    tempPop.ind = sorted(tempPop.ind, key = lambda x:x["id"]) # Order the individuals by the id number

    dePop = [d for d in tempPop.ind if d["type"]=="DE"] # Select only the DE individuals


    for ind in dePop:
        x = []
        candidates = [c for c in dePop if c["id"] != ind["id"]]
        a, b, c = globalVar.rng.choice(candidates, 3, replace=False) # Select the candidate individuals

        for d in range(parameters["NDIM"]):
            x.append(a["pos"][d] + parameters["DE_F"]*(b["pos"][d] - c["pos"][d]))
            if x[d] > parameters["MAX_POS"]:
                x[d] = parameters["MAX_POS"]
            elif x[d] < parameters["MIN_POS"]:
                x[d] = parameters["MIN_POS"]

        for d in range(parameters["NDIM"]):
            if globalVar.rng.random() < parameters["DE_CR"]:
                ind["pos"][d] = x[d]

    for ind in dePop:
        ind = abec.evaluate(ind, parameters)
        for i in range(len(pop.ind)):
            if ind["id"] == pop.ind[i]["id"]:
                    if ind["fit"] < pop.ind[i]["fit"]:
                        pop.ind[i] = ind.copy()
                        ind, globalVar.best = abec.updateBest(pop.ind[i], globalVar.best)
                    else:
                            pop.ind[i]["ae"] = 1    # Assure that this individual will not be evaluated again

    return pop

