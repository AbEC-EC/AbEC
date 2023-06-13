# AbEC


## Description
The AbEC (<ins>**A**</ins>djusta<ins>**b**</ins>le <ins>**E**</ins>volutionary <ins>**C**</ins>omponents) is a framework developed in Python to test different 
components present in the literature on Evolutionary Algorithms (EA) that are 
used in optimization of Static and Dynamic problems. It allows the components to be turned 
on/off in order to test the effectiveness of each one of them independently in a given 
problem.
Another characteristic is the possibility of configuring the parameters of both the 
optimizers (GA, PSO, DE, ES) and the characteristics of the Benchmarks.

## Usage

To use the framework, the easiest way is just clone the git repository and start to use.
For this, you can use the following command in your terminal:
 
```python
    git clone https://github.com/AbEC-EC/AbEC.git
```

<br>
Now, you basically just need to adjust the algorithm in the way that you want and boom!!

<br>

To know more about the configuration files and usage of the framework [come here](https://abec-ec.github.io).

## Contents

Besides of the algorithm configuration the framework also has some features related to the analysis of experimental data:

In <br> 
> AbEC/abec/metrics

Are the codes responsible for the metrics of the algorithms. The metrics implemented so far are:

* Current Error
* Offline Error

And In <br>
> AbEC/abec/plot

Are the codes responsible for generating the graphs. The options implemented so far are:

* Current Error
* Offline Error
* Search Space

## Configuration files

The configuration of the framework is divided in three configuration files, named:

* algoConfig.ini

Where it is the configuration related to the functioning of the algorithm itself (e.g. Population size, optimizers, ...).

* frameConfig.ini

Where it is the configuration of the framework parameters (e.g. number of runs, path of the files, number of evaluations, ...).

* problemConfig.ini

For the configuration of the problem (e.g. number of dimensions, dynamic or not, ...).
