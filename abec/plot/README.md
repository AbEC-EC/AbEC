## The scripts is this dir are used to generate figures of error over generations from the data of the experiments.

### The setup of the metrics codes is made by the "config.ini" file.

Also, it is necessary pass some arguments when call the script. The sintax for currentError
and offlineError is:

    $ python3 code.py -p path path1 ... path5

where path is one folder before than where the data are and
pathX[1-5] is the folder where the data are.

It is possible plot up to 5 datasets on the same figure.

Examples:

    $ python3 currentErrorPlot.py -p ../../../examples/pso-abcd pso

    $ python3 currentErrorPlot.py -p ../../../examples/pso-abcd pso abcd

