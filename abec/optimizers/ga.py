import optimizers.elitism as elitism
import optimizers.crossover as crossover
import components.mutation as mutation
import abec
import copy
import globalVar

'''
    GA optimizer
'''
def ga(pop, parameters):
    newPop = abec.population(parameters, id = 0, fill = 0)
    newPop.id = pop.id
    tempPop = copy.deepcopy(pop)
    #tempPop.ind = sorted(tempPop.ind, key = lambda x:x["id"])

    gaPop = [d for d in tempPop.ind if d["type"]=="GA"] # Select only the DE individuals
    #gaPop = sorted(gaPop, key=lambda x:x["fit"])

    if mutation.cp_mutation(parameters):
        newPop = elitism.elitism(gaPop, newPop, parameters)
        newPop = crossover.crossover(gaPop, newPop, parameters)
        newPop = mutation.mutation(newPop, parameters)


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
