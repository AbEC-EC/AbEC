import sys
import os
import getopt
import numpy as np

arg_help = "{0} -p <path>".format(sys.argv[0])
path = "."

try:
    opts, args = getopt.getopt(sys.argv[1:], "hp:", ["help", "path="])
except:
    print(arg_help)
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print(arg_help)  # print the help message
        sys.exit(2)
    elif opt in ("-p", "--path"):
        path = arg

print('path:', path)

values = [round(i,2) for i in np.arange(3.0, 50.5, 0.5)]

dirs1 = list()
dirValues = list()
for root, dirs, files in os.walk(path, topdown=False):
    for name in dirs:
        dirValues.append(os.path.join(name))
dirValues.sort()

dirs1 = dirValues[-1:]

print(dirs1)


offlineError = []
stdOe = []
for value in dirs1:
   # print(value)
    pathTmp = f"{path}/{value}"
    dirValues = list()
    for root, dirs, files in os.walk(pathTmp, topdown=False):
        for name in dirs:
            dirValues.append(int(os.path.join(name)))
    dirValues.sort()
    for values2 in dirValues:
        #int(f"{pathTmp}/{values2}")
        print(f"{pathTmp}/{values2}")
        if(os.path.isfile(f"{pathTmp}/{values2}/bebc.txt")):
            print("Ja tem")
        else:
            #print("Nao tem")
            os.system(f"python3 bestBeforeChange.py -p {pathTmp}/{values2}")
