import aux.globalVar as fitFunction
import aux.fitFunction as fitFunction
import aux



params = [""]
scope = ["LD"]

def evaluate(x, parameters):
    '''
    Fitness function. Returns the error between the fitness of the particle
    and the global optimum
    '''
    fitness = fitFunction.fitnessFunction(x['pos'], parameters)
    globalVar.nevals += 1
    return fitness

def cp(parameters):
    if parameters["COMP_REEVALUATION"] == 1 :
        return 1
    elif parameters["COMP_REEVALUATION"] != 0:
        errorWarning("3.1", "algoConfig.ini", "COMP_REEVALUATION", "Component Mutation should be 0 or 1")
        sys.exit()
    else:
        return 0



def detection(pop, parameters):
    '''
    Check if a change occurred in the environment
    '''
    if parameters["COMP_CHANGE_DETECT_MODE"] == 0:
        if (parameters["CHANGES_NEVALS"][globalVar.flagChangeEnv] <=  globalVar.nevals < parameters["CHANGES_NEVALS"][globalVar.flagChangeEnv+1]) \
            and (parameters["CHANGES"]):
            if globalVar.flagChangeEnv < len(parameters["CHANGES_NEVALS"])-2:
                globalVar.flagChangeEnv += 1
            globalVar.mpb.changePeaks()
            if(globalVar.peaks <= len(parameters["CHANGES_NEVALS"])): # Save the optima values
                aux.saveOptima(parameters)
                globalVar.peaks += 1

            return 1
        else:
            return 0

    elif parameters["COMP_CHANGE_DETECT_MODE"] == 1:
        sensor = evaluate(pop.best, parameters)
        if(abs(sensor-pop.best["fit"]) > 0.001):
        #if(pop.best["fit"] != )
            #print(f"[CHANGE OCCURED][NEVAL: {globalVar.nevals}][GEN: {gen}][POP ID: {pop.id}]]")
            print(f"POP BEST: {pop.best}][SENSOR: {sensor}]")
            #print(f"[CHANGE] nevals: {nevals}  sensor: {sensor}  sbest:{swarm.best.fitness.values[0]}")
            pop.best["fit"] = sensor
            return 1
        else:
            return 0
