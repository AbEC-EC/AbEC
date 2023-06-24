#import optimizers.elitism as elitism
#import optimizers.crossover as crossover
#import components.mutation as mutation
import abec
import copy
import aux.globalVar as globalVar
from aux.aux import errorWarning

'''
    GA optimizer
'''

params = ["ELI_PERC", "CROSS_PERC", "MUT_PERC", "MUT_STD", "ENCODER", "INDSIZE"]

'''
Elitism operator
'''
def cp_elitism(parameters):
    if 0 < parameters["GA_ELI_PERC"] < 1:
        return 1
    else:
        errorWarning(1.2, "algoConfig.ini", "GA_ELI_PERC", "The percentage parameter of the Elitism component Elitism should be in the interval ]0, 1[")
        sys.exit()

def elitism(pop, newPop, parameters):
    for i in range(int(parameters["GA_ELI_PERC"]*parameters["GA_POP_PERC"]*parameters["POPSIZE"])):
        newPop.addInd(parameters)
        #print(f"newPop.ind[{i}]: {newPop.ind[i]}")
        #print(f"pop[{i}]: {pop[i]}")
        #e()
        newPop.ind[i] = copy.deepcopy(pop[i])
        newPop.ind[i]["ae"] = 1

    return newPop


'''
Crossover operator
'''
def cp_crossover(parameters):
    if 0.1 < parameters["GA_CROSS_PERC"] <= 1:
        return 1
    else:
        errorWarning(2.2, "algoConfig.ini", "GA_CROSS_PERC", "The percentage parameter of the Elitism component Elitism should be in the interval ]0.1, 1[")
        sys.exit()

def condition(individual):
    return individual["fit"]
def tournament(pop, parameters):
    l = int(len(pop)/2)
    c = []
    for _ in range(3):
        c.append(globalVar.rng.choice(pop[:int(parameters["GA_CROSS_PERC"]*parameters["GA_POP_PERC"]*parameters["POPSIZE"])]))

    choosed = min(c, key=condition)
    return choosed

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

        for i in range(len(child1["pos"])):
            if child1["pos"][i] > parameters["MAX_POS"]:
                child1["pos"][i] = parameters["MAX_POS"]
            elif child1["pos"][i] < parameters["MIN_POS"]:
                child1["pos"][i] = parameters["MIN_POS"]

            if child2["pos"][i] > parameters["MAX_POS"]:
                child2["pos"][i] = parameters["MAX_POS"]
            elif child2["pos"][i] < parameters["MIN_POS"]:
                child2["pos"][i] = parameters["MIN_POS"]

        newPop.addInd(parameters, i)
        newPop.ind[-1]["pos"] = child1["pos"].copy()
        newPop.ind[-1]["type"] = "GA"
        newPop.addInd(parameters, i+1)
        newPop.ind[-1]["pos"] = child2["pos"].copy()
        newPop.ind[-1]["type"] = "GA"

    return newPop


def decoder(ind, parameters):
    '''
    Decoder function for continous problems
    From binary to decimal
    '''
    sum = 0
    j = 0
    l = int(parameters["INDSIZE"]/parameters["NDIM"])
    result = []
    precision = (parameters["MAX_POS"]-parameters["MIN_POS"])/(2**(l)-1)
    for d in range(1, parameters["NDIM"]+1):
        for i, bin in enumerate(ind["pos"][j:d*l], 0):
            sum += bin*(2**(l-i-1))
        decode = sum*precision + parameters["MIN_POS"]
        result.append(decode)
        j = d*l

        sum = 0

    ind["pos"] = result
    return ind

def encoder(ind, parameters):
    '''
    Encoder function for continous problems
    From decimal to binary
    '''
    l = int(parameters["INDSIZE"]/parameters["NDIM"])
    result = ""
    for d in ind["pos"]:
        encode = ((2**(l)-1)*(d - parameters["MIN_POS"]))/(parameters["MAX_POS"]-parameters["MIN_POS"])
        result += "{0:016b}".format(int(encode))
    result = list(result)

    print (result)

    for i, b in enumerate(result):
        result[i] = int(b)

    ind["pos"] = result
    return ind

'''
Mutation operator
'''

def cp_mutation(parameters):
    elitism_factor = parameters["GA_ELI_PERC"]
    mutation_factor = parameters["GA_MUT_PERC"]
    mutation_std = parameters["GA_MUT_STD"]

    if 0 < mutation_factor < 1:
        if parameters["MIN_POS"] < mutation_std < parameters["MAX_POS"]:
            return 1
        else:
            errorWarning("3.3", "algoConfig.ini", "GA_MUT_STD", "The percentage parameter of the Elitism component Elitism should be in the interval ]0, 1[")
            sys.exit()
    else:
        errorWarning("3.2", "algoConfig.ini", "GA_MUT_PERC", "The percentage parameter of the Elitism component Elitism should be in the interval ]0, 1[")
        sys.exit()


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
                    dp = globalVar.rng.normal(loc = 0.0, scale = mutation_std)
                    if (pop.ind[i]["pos"][d] + dp ) > parameters["MAX_POS"]:
                        pop.ind[i]["pos"][d] = parameters["MAX_POS"]
                    elif (pop.ind[i]["pos"][d] + dp ) < parameters["MIN_POS"]:
                        pop.ind[i]["pos"][d] = parameters["MIN_POS"]
                    else:
                        pop.ind[i]["pos"][d] += dp
    return pop


def cp(parameters):
    cp_elitism(parameters)
    cp_mutation(parameters)
    cp_crossover(parameters)

def ga(pop, parameters):
    newPop = abec.population(parameters, id = 0, fill = 0)
    newPop.id = pop.id
    tempPop = copy.deepcopy(pop)
    #tempPop.ind = sorted(tempPop.ind, key = lambda x:x["id"])

    gaPop = [d for d in tempPop.ind if d["type"]=="GA"] # Select only the DE individuals
    #gaPop = sorted(gaPop, key=lambda x:x["fit"])

    if cp_mutation(parameters):
        newPop = elitism(gaPop, newPop, parameters)
        newPop = crossover(gaPop, newPop, parameters)
        newPop = mutation(newPop, parameters)


    # Substitute the individuals of GA population
    for ind in newPop.ind:
        for i in range(len(pop.ind)):
            if ind["id"] == pop.ind[i]["id"]:
                    pop.ind[i] = ind.copy()
    '''
    for i, ind in enumerate(newPop.ind):
        if ind["id"] == pop.ind[i]["id"]:
        #if ind["id"] <= int(parameters["GA_POP_PERC"]*parameters["POPSIZE"]):
            pop.ind[i] = ind.copy()
    '''

    return pop
