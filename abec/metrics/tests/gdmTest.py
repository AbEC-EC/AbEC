import numpy as np
import pandas as pd
import sys
import getopt
import matplotlib.pyplot as plt


plt.style.use("dark_background")
plt.rcParams["axes.facecolor"] = "#1c1c1c"
plt.rcParams["savefig.facecolor"] = "#1c1c1c"
plt.rcParams["figure.figsize"] = (20, 16)

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

gdms = ["dtd", "dmi", "dtap", "dvac", "dpw", "mex"]
#gdms = ["dtd", "dtap"]
#gdms = ["dpw", "mex"]
gen = df["gen"]

for metric in gdms:
    ax.plot(gen, df[metric], label=f"{metric}")

ax.set_title(f"GDMs")
plt.legend()
plt.grid(which="major", color="dimgrey", linewidth=0.8)
plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)
plt.show()
    