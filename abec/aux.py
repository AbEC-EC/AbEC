import csv
import os
import datetime
import globalVar

cDate = datetime.datetime.now()
year = cDate.year
month = cDate.month
day = cDate.day
hour = cDate.hour
minute = cDate.minute

'''
Check if the dirs already exist, and if not, create them
Returns the path
'''
def checkDirs(path):
    if(os.path.isdir(path) == False):
        os.mkdir(path)
    path += f"/{year}-{month}-{day}"
    if(os.path.isdir(path) == False):
        os.mkdir(path)
    path += f"/{hour}-{minute}"
    if(os.path.isdir(path) == False):
        os.mkdir(path)
    return path


'''
Write the log of the algorithm over the generations on a csv file
'''
def writeLog(mode, filename, header, data=None):
    if(mode==0):
        # Create csv file
        with open(filename, "w") as file:
            csvwriter = csv.DictWriter(file, fieldnames=header)
            csvwriter.writeheader()
    elif(mode==1):
        # Writing in csv file
        with open(filename, mode="a") as file:
            csvwriter = csv.DictWriter(file, fieldnames=header)
            csvwriter.writerows(data)
           # for i in range(len(data)):
           #     csvwriter.writerows(data[i])


'''
Write the position and fitness of the peaks on
the 'optima.csv' file. The number of the peaks will be
NPEAKS_MPB*NCHANGES
'''
def saveOptima(parameters):
    opt = [0]
    if(parameters["BENCHMARK"] == "MPB"):
        opt = [0 for _ in range(parameters["NPEAKS_MPB"])]
        for i in range(parameters["NPEAKS_MPB"]):
            opt[i] = globalVar.mpb.maximums()[i]
    elif(parameters["BENCHMARK"] == "H1"):
        opt[0] = fitFunction([8.6998, 6.7665])[0]
    with open(f"{globalVar.path}/optima.csv", "a") as f:
        write = csv.writer(f)
        write.writerow(opt)
