# AbEC


## Description
The AbEC (Adjustable Evolutionary Components) is a framework developed in Python to test different 
components present in the literature on Evolutionary Algorithms (EA) that are 
used in optimization of Static and Dynamic problems. It allows the components to be turned 
on/off in order to test the effectiveness of each one of them independently in a given 
problem.
Another characteristic is the possibility of configuring the parameters of both the 
optimizers (GA, PSO, DE, ES) and the characteristics of the Benchmark, which until now consists 
of the Moving Peak Benchmark (MPB).

## Usage

To use the framework, the easiest way is just clone the git repository and start to use.
For this, you can use the following command in your terminal:

<br> 
> git clone https://github.com/AbEC-EC/AbEC.git

<br>
Now, you basically just need to adjust the algorithm in the way that you want and boom!!

<br>

To know more about the configuration files, >come here<.

## Contents

This repository contains both the framework code in the "abec/" 
folder and codes related to the analysis of experimental data:

In <br> 
> "abec/plot"

Are the codes responsible for generating the performance graphs of 
the algorithms;

In <br>
> "abec/metrics" 

Are the codes responsible for calculating the metrics of the execution of the algorithms.

## Parameters settings

### General
- **Parameters for general purpose**
    - *RUNS: 1 - 1000* (int) -> Number of runs;
    - *NEVALS: 1 - 1000000* (int) -> Number of Evaluations of each run;
    - *POPSIZE: 1 - 1000* (int) -> Population size;
    - *NDIM: 1-1000* (int) -> Number of dimensions of the problem;
    - *BOUNDS: [BOUNDMIN, BOUNDMAX]* (list of int) -> Problem boundaries;

### Optmizers

- **PSO**
    - *phi1: 0 - 10* (real) -> Parameter referring to the weight of the individual's contribution;
    - *phi2: 0 - 10* (real) -> Parameter referring to the contribution weight of the best individual in the flock.

- **ES**
    - *RCLOUD: 0 - BOUNDMAX* (real) -> Radius around the individual to be searched.

## Operators

### Change Detection

- **Reevaluation based method**

    - *CHANGE_DETECTION_OP: 0 or 1* (bool) -> 0 for change detection OFF, 1 for change detection ON.


### Diversity control

- **Anti-Convergence**

    - *ANTI_CONVERGENCE_OP: 0 or 1* (bool) -> 0 for anti-convergency OFF, 1 for anti-convergency ON
    - *AC_TYPE_OP: {1, 2, 3}* (int) -> Type of anti-convergency
        - 1: Spatial size monitoring
            - *RCONV: 0 - BOUNDMAX* (real) -> Radius for a subpopulation be considered converged.
        - 2: Fitness monitoring
            - *RCONV: 0 - BOUNDMAX* (real) -> Radius for a subpopulation be considered converged.

- **Exclusion based on spatial size monitoring**

    - *EXCLUSION_OP: 0 or 1* (bool) -> 0 for exclusion OFF, 1 for exclusion ON
    - *REXCL: 0 - BOUNDMAX* (real) -> Radius for two subpopulation be considered redundant.

### Population division and management

- **Multipopulation**

    - Fixed number of subpopulations
        - *NSPOP: 1 - POPSIZE* (int) -> Number of subpopulations.

## Benchmark (Moving Peak Benchmark) parameters:

- *CHANGE: 0 or 1* (bool) -> If there will be changes in the environment;
- *RANDOM_CHANGES: 0 or 1* (bool) -> Whether the changes will be random or not;
- *RANGE_GEN_CHANGES: [MIN, MAX]* (list of int) -> Range of allowed values for random changes to occur;
- *NCHANGES: 1-1000* (int) -> Number of random changes;
- *CHANGES_GEN: [values]* (list of int) -> If the changes are manual, these are the values of the generations in which they will occur;
- *NPEAKS_MPB: 1 - 1000* (int) -> Number of benchmark peaks;
- *UNIFORM_HEIGHT_MPB: 0 - 1000* (float) -> Initial value of the peaks. If 0 will be random;
- *MAX_HEIGHT_MPB: 0 - 1000* (float) -> Maximum value for peaks;
- *MIN_HEIGHT_MPB: 0 - 1000* (float) -> Minimum value for peaks;
- *MOVE_SEVERITY_MPB: 1 - BOUNDMAX* (float) -> Intensity of the change in the position of the peaks when there is a change of environment;
