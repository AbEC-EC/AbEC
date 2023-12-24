'''
Title: Code of the benchmark presented in 


Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import importlib
import csv

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 15
plt.rc('font', size=BIGGER_SIZE)          # controls default text sizes

colors_array = list(matplotlib.colors.cnames.keys())
markers_array = list(matplotlib.markers.MarkerStyle.markers.keys())
fig, ax = plt.subplots()
plots = [1, 25, 50, 75, 95]
colors_array = ["red", "green", "blue", "orange", "black"]

NRUNS = 1 # Number of runs
NGEN = 100 # Number of generations
NPEAKS = 1 # Number of peaks
NP = 100 # Number of individuals in the population
NOUT = 0 # Number of outliers
GOUT = [2, 7] # Generation where the outliers appears
LD = [0, 100] # Boundaries of the landscape
SEED = 42
NDIM = 2
PLOT = 0
METRICS_TO_TEST = ["mid", "dpw"]
rng = np.random.default_rng(SEED)
rng.random()

def writeLog(mode, filename, header, data=None):
    if(mode==0):
        # Create csv file
        file = open(filename, "w")
        csvwriter = csv.DictWriter(file, fieldnames=header)
        csvwriter.writeheader()
        
    elif(mode==1):
        # Writing in csv file
        file = open(filename, "a")
        csvwriter = csv.DictWriter(file, fieldnames=header)
        csvwriter.writerows(data)
    file.close()

class optimum_point():
    def __init__(self, ndim=2, ld=LD, np=NP, nout=NOUT):
        self.positions = (ld[1]- ld[0])*rng.random(size=ndim) + ld[0]
        self.position_min = [ld[0] for d in range(ndim)]
        self.position_max = [ld[1] for d in range(ndim)]
        self.decrease_rate_min = [(self.positions[d] - ld[0])*0.01 for d in range(ndim)]
        self.decrease_rate_max = [(ld[1] - self.positions[d])*0.01 for d in range(ndim)]
        
        self.pop = [[] for _ in range(np)]
        self.outliers = [[] for _ in range(nout)]
        
    def pos(self):
        return self.positions

for r in range(NRUNS):
    ld = LD
    # create the optima points
    popsize = int(NP/NPEAKS)
    optima = [optimum_point(ndim=NDIM, ld=LD, np=popsize, nout=NOUT) for _ in range(NPEAKS)]
    metrics = []
    names = []
    header = ["gen"]
    generations = []
    
    for name in METRICS_TO_TEST:
        names.append(name)
        names.append(f"{name}_NMDF")
        header.append(name)
        header.append(f"{name}_NMDF")
    writeLog(0, f"run_{r}.csv", header)
        
    gdms = {name: [] for name in names}

    for metric_name in METRICS_TO_TEST:
        metrics.append(importlib.import_module(f"{metric_name.lower()}"))
        

    for g in range(1, NGEN):
        # evaluate the boundaries of the space based on the optima points
        for i, optimum in enumerate(optima):
            for d in range(NDIM):
                optimum.position_min[d] += optimum.decrease_rate_min[d]
                optimum.position_max[d] -= optimum.decrease_rate_max[d]                   

            if(PLOT and g in plots):
                plt.xlim(0, 100)
                plt.ylim(0, 100)
                plt.scatter(x=optimum.pos()[0], y=optimum.pos()[1], s=2, color=colors_array[i], marker="X")
                plt.plot((optimum.position_min[0], optimum.position_min[0]), (optimum.position_min[1], optimum.position_max[1]), c=colors_array[i])
                plt.plot((optimum.position_max[0], optimum.position_max[0]), (optimum.position_min[1], optimum.position_max[1]), c=colors_array[i])
                plt.plot((optimum.position_min[0], optimum.position_max[0]), (optimum.position_min[1], optimum.position_min[1]), c=colors_array[i])
                plt.plot((optimum.position_min[0], optimum.position_max[0]), (optimum.position_max[1], optimum.position_max[1]), c=colors_array[i])
                #print(f"Dimension {d}: pos_min = {optimum.position_min[0]}, pos_max = {optimum.position_max[1]}")

        # Set the number of the population based on the outliers     
        if NOUT and g >= GOUT[0]:
            NIND = popsize - NOUT
        else:
            NIND = popsize
            
        # creation of the individuals
        for optimum in optima:
            for i in range(popsize):
                optimum.pop[i] = [(optimum.position_max[d] - optimum.position_min[d])*rng.random() + optimum.position_min[d] for d in range(NDIM)]
                
            # In specif generations, randomize the outliers
            if NOUT and g in GOUT: 
                for out in range(NOUT):
                    optimum.outliers[out] = [(ld[1]-ld[0])*rng.random() + ld[0] for d in range(NDIM)]
        
        # Evaluate the metrics
        population = []
        for name, metric in zip(METRICS_TO_TEST, metrics):
            for optimum in optima:
                population += optimum.pop + optimum.outliers
            gdms[name], gdms[f"{name}_NMDF"] = metric.metric(gdms[name], gdms[f"{name}_NMDF"], population, g)
            
        # Plot of the population
        if(PLOT and g in plots):            
            for i, optimum in enumerate(optima):
                for j in range(NIND):
                    ind = optimum.pop[j]
                    plt.scatter(x=ind[0], y=ind[1], s=10, c=colors_array[i], marker=markers_array[i])
                if NOUT and g >= GOUT[0]:
                    for ind in optimum.outliers:
                        plt.scatter(x=ind[0], y=ind[1], s=10, c=colors_array[i], marker=markers_array[i])
            plt.show()
            
        generations.append(g)
    
    for g in generations:
        for name in METRICS_TO_TEST:
            log = {"gen": g, name: gdms[name][g-1], f"{name}_NMDF": gdms[f"{name}_NMDF"][g-1]}
            writeLog(1, f"run_{r}.csv", header, data = [log])
            
    for i, name in enumerate(METRICS_TO_TEST):
        plt.plot(generations, gdms[name], label=f"{name}", marker=markers_array[i])
        
    plt.xlabel("Generations")
    plt.ylabel("Metric value")
    plt.grid(1)
    plt.legend(loc='best')
    plt.show()    