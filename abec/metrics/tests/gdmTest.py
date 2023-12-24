import numpy as np
import pandas as pd
import sys
import getopt
import matplotlib.pyplot as plt
import matplotlib


#plt.style.use("dark_background")
#plt.rcParams["axes.facecolor"] = "#1c1c1c"
#plt.rcParams["savefig.facecolor"] = "#1c1c1c"

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 15
plt.rc('font', size=BIGGER_SIZE)          # controls default text sizes
#plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
#plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
#plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
#plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
#plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
#plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
plt.rcParams["figure.figsize"] = (10, 6)
colors_array = list(matplotlib.colors.cnames.keys())
markers_array = list(matplotlib.markers.MarkerStyle.markers.keys())
lineStyles_array = list(matplotlib.lines.lineStyles.keys())

#####################################
# get the arguments
#####################################
arg_help = "{0} -p <path> ".format(sys.argv[0])
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


fig, ax = plt.subplots()

df = pd.read_csv(path)

gdms = ["dtd", "dmi", "dtap", "dvac", "dpw"]
#gdms = ["dtd", "dtap", "dpw"]
#gdms = ["dtd", "dtap"]
#gdms = ["dpw", "mex"]
gen = df["gen"]

for i, metric in enumerate(gdms):
    ax.plot(gen, df[metric], label=f"{metric}", marker=markers_array[i])

#ax.set_title(f"GDMs ")
plt.legend()
plt.yscale("log")
ax.set_ylabel("Diversity")
ax.set_xlabel("Generation")
plt.grid(which="major", color="dimgrey", linewidth=0.8)
plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)
plt.savefig("diversity2.png")
plt.show()
    
