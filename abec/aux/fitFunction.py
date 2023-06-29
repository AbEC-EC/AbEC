import random
import aux.globalVar
import aux.aux
import abec
import fitnessFunction.function as function
from deap import benchmarks
from deap.benchmarks import movingpeaks

def mpbAbcd(parameters):
    # Setup of MPB
    if (parameters["SCENARIO_MPB"] == 1):
        scenario = movingpeaks.SCENARIO_1
    elif (parameters["SCENARIO_MPB"] == 2):
        scenario = movingpeaks.SCENARIO_2
    elif (parameters["SCENARIO_MPB"] == 3):
        scenario = movingpeaks.SCENARIO_3
    severity = parameters["MOVE_SEVERITY_MPB"]
    scenario["period"] = 0
    scenario["npeaks"] = parameters["NPEAKS_MPB"]
    scenario["uniform_height"] = parameters["UNIFORM_HEIGHT_MPB"]
    scenario["move_severity"] = severity
    scenario["min_height"] = parameters["MIN_HEIGHT_MPB"]
    scenario["max_height"] = parameters["MAX_HEIGHT_MPB"]
    scenario["min_width"] = parameters["MIN_WIDTH_MPB"]
    scenario["max_width"] = parameters["MAX_WIDTH_MPB"]
    scenario["min_coord"] = parameters["MIN_COORD_MPB"]
    scenario["max_coord"] = parameters["MAX_COORD_MPB"]
    scenario["lambda_"] = parameters["LAMBDA_MPB"]
    rngMPB = random.Random()
    rngMPB.seed(parameters["SEED"])
    globalVar.mpb = movingpeaks.MovingPeaks(dim=parameters["NDIM"], random=rngMPB, **scenario)
    return globalVar.mpb


def fitnessFunction(x, parameters):
    globalOP = 0
    fitInd = 0
    global mpb
    if(parameters["BENCHMARK"] == "CIGAR"):
        globalOP = benchmarks.cigar([0 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.cigar(x)[0]
    elif(parameters["BENCHMARK"] == "PLANE"):
        globalOP = benchmarks.plane([0 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.plane(x)[0]
    elif(parameters["BENCHMARK"] == "SPHERE"):
        globalOP = benchmarks.sphere([0 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.sphere(x)[0]
    elif(parameters["BENCHMARK"] == "ACKLEY"):
        globalOP = benchmarks.ackley([0 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.ackley(x)[0]
    elif(parameters["BENCHMARK"] == "BOHACHEVSKY"):
        globalOP = benchmarks.bohachevsky([0 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.bohachevsky(x)[0]
    elif(parameters["BENCHMARK"] == "GRIEWANK"):
        globalOP = benchmarks.griewank([0 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.griewank(x)[0]
    elif(parameters["BENCHMARK"] == "H1"):
        globalOP = benchmarks.h1([8.6998, 6.7665])[0]
        fitInd = benchmarks.h1(x)[0]
    elif(parameters["BENCHMARK"] == "HIMMELBLAU"):
        globalOP = benchmarks.himmelblau([3.0, 2.0])[0]
        fitInd = benchmarks.himmelblau(x)[0]
    elif(parameters["BENCHMARK"] == "RASTRIGIN"):
        globalOP = benchmarks.rastrigin([0 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.rastrigin(x)[0]
    elif(parameters["BENCHMARK"] == "ROSENBROCK"):
        globalOP = benchmarks.rosenbrock([1 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.rosenbrock(x)[0]
    elif(parameters["BENCHMARK"] == "SCHAFFER"):
        globalOP = benchmarks.schaffer([0 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.schaffer(x)[0]
    elif(parameters["BENCHMARK"] == "SCHWEFEL"):
        globalOP = benchmarks.schwefel([420.9687436 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.schwefel(x)[0]
    elif(parameters["BENCHMARK"] == "MPB"):
        if not globalVar.mpb:
            globalVar.mpb = mpbAbcd(parameters)
            if(globalVar.peaks <= len(parameters["CHANGES_NEVALS"])): # Save the optima values
                aux.saveOptima(parameters)
                globalVar.peaks += 1
        globalOP = globalVar.mpb.maximums()[0][0]
        fitInd = globalVar.mpb(x)[0]
    elif(parameters["BENCHMARK"] == "NONE"):
        fitInd = function.function(x, parameters["CHANGES_NEVALS"])
        globalOP = 0


    if parameters["BENCHMARK"] =="NONE":
        fitness = fitInd
    else:
        fitness = abs(fitInd - globalOP )
    return fitness
