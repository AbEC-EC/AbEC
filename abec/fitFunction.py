import random
import globalVar
import aux
import abec
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
    if(parameters["BENCHMARK"] == "H1"):
        globalOP = benchmarks.h1([8.6998, 6.7665])[0]
        fitInd = benchmarks.h1(x)[0]
    elif(parameters["BENCHMARK"] == "BOHACHEVSKY"):
        globalOP = benchmarks.bohachevsky([0 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.bohachevsky(x)[0]
    elif(parameters["BENCHMARK"] == "HIMMELBLAU"):
        globalOP = benchmarks.himmelblau([3.0, 2.0])[0]
        fitInd = benchmarks.himmelblau(x)[0]
    elif(parameters["BENCHMARK"] == "SPHERE"):
        globalOP = benchmarks.sphere([0 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.sphere(x)[0]
    elif(parameters["BENCHMARK"] == "ROSENBROCK"):
        globalOP = benchmarks.rosenbrock([1 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.rosenbrock(x)[0]
    elif(parameters["BENCHMARK"] == "SCHAFFER"):
        globalOP = benchmarks.schaffer([0 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.schaffer(x)[0]
    elif(parameters["BENCHMARK"] == "SCHWEFEL"):
        globalOP = benchmarks.schwefel([420.9687436 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.schwefel(x)[0]
    elif(parameters["BENCHMARK"] == "RASTRIGIN"):
        globalOP = benchmarks.rastrigin([0 for _ in range(parameters["NDIM"])])[0]
        fitInd = benchmarks.rastrigin(x)[0]
    elif(parameters["BENCHMARK"] == "MPB"):
        if not globalVar.mpb:
            globalVar.mpb = mpbAbcd(parameters)
            if(globalVar.peaks <= len(parameters["CHANGES_NEVALS"])): # Save the optima values
                aux.saveOptima(parameters)
                globalVar.peaks += 1
        globalOP = globalVar.mpb.maximums()[0][0]
        fitInd = globalVar.mpb(x)[0]
    elif(parameters["BENCHMARK"] == "NONE"):
        abec.errorWarning("0.0.0", file="function.py", parameter="NONE", text="The fitness function is not defined. The file function.py must be included in this directory.")




    fitness = abs(fitInd - globalOP )
    return fitness
