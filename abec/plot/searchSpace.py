import pandas as pd
import matplotlib.pyplot as plt

def configPlot(THEME = 1, GRID = 1):
    # Configure colors
    if(THEME == 1):
        plt.style.use("dark_background")
        plt.rcParams["axes.facecolor"] = "#1c1c1c"
        plt.rcParams["savefig.facecolor"] = "#1c1c1c"
        plt.rcParams["figure.figsize"] = (16, 9)
    elif(THEME == 2):
        plt.rcParams["axes.facecolor"] = "white"
        plt.rcParams["figure.figsize"] = (11, 8)

    fig, ax = plt.subplots(1)

    # Color of grids
    if(GRID == 1):
        ax.grid(True)
        plt.grid(which="major", color="dimgrey", linewidth=0.8)
        plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)
    else:
        ax.grid(False)

    return fig, ax


def configLegend(fig, ax, THEME):
    plt.legend()
    for text in plt.legend().get_texts():
        if(THEME == 1):
            text.set_color("white")
            text.set_fontsize(24)
        elif(THEME == 2):
            #text.set_color("white")
            text.set_fontsize(16)
    return fig, ax

def plotOptima(path, fig, ax):
    gop = pd.read_csv(f"{path}/optima.csv")
    for k in range(gop.shape[1]):
        temp = gop[f"opt{k}"].values.tolist()
        for j in range(len(temp)):
            temp[j] = list(temp[j].split(", "))
            for i in range(len(temp[j])):
                temp[j][i] =  temp[j][i].replace("[", "")
                temp[j][i] =  temp[j][i].replace("(", "")
                temp[j][i] =  temp[j][i].replace(")", "")
                temp[j][i] =  temp[j][i].replace("]", "")
                temp[j][i] =  float(temp[j][i])

        x = [[x[1], x[2]] for x in temp]
        x1 = [item[0] for item in x]
        y1 = [item[1] for item in x]
        if(k == 0):
            ax.scatter(x1, y1, label=f"GOP", c = "orange", s=200, marker="*")
        else:
            ax.scatter(x1, y1, label=f"LOP", c="green", s=50)

    return fig, ax

def loadPlot(path, fig, ax, parameters, multi, THEME):
    df = pd.read_csv(path)
    x = []
    y = []
    for row in df["indPos"]:
        pos = row.strip('][').split(', ')
        x.append(float(pos[0]))
        y.append(float(pos[1]))

    ax.scatter(x, y, label=f"Ind", s=30, alpha=0.5)

    if multi:
        ax.fill_between(df["nevals"], df["eo"] - df["eo_std"], df["eo"]+ df["eo_std"], alpha=0.05)

    # Axes labels and limits
    ax.set_xlabel("X", fontsize=20)
    ax.set_ylabel("Y", fontsize=20)
    ax.set_xticks([-100, -75, -50, -25, 0, 25, 50, 75, 100])
    ax.set_yticks([-100, -75, -50, -25, 0, 25, 50, 75, 100])
    ax.set_xlim(parameters["MIN_POS"], parameters["MAX_POS"])
    ax.set_ylim(parameters["MIN_POS"], parameters["MAX_POS"])

    # Title content
    if parameters:
        title = f"{parameters['ALGORITHM']} on {parameters['BENCHMARK']} \n\n \
                            POPSIZE: {parameters['POPSIZE']}\
                            DIM: {parameters['NDIM']}\
                        "
    else:
        title = "ALGORITHM"

    # Title size
    if THEME == 1:
        ax.set_title(title, fontsize=22)
    elif THEME == 2:
        ax.set_title(title, fontsize=18)

    return fig, ax


def spPlot(path, parameters = 0, type = 1, multi = 0, THEME = 1, pathSave = ".", name = "sp"):
    fig, ax = configPlot(THEME)

    fig, ax = loadPlot(f"{path}.csv", fig, ax, parameters, multi, THEME)
    fig, ax = plotOptima(pathSave, fig, ax)
    fig, ax = configLegend(fig, ax, THEME)

    plt.savefig(f"{pathSave}/{name}.png", format="png")
    plt.show()
