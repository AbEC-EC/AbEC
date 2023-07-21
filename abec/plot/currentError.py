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


def loadPlot(path, fig, ax, parameters, multi, THEME):
    df = pd.read_csv(path)
    ax.plot(df["nevals"], df["ec"], label=f"Algorithm")

    if multi:
        ax.fill_between(df["nevals"], df["ec"] - df["ec_std"], df["ec"]+ df["ec_std"], alpha=0.05)

    # Axes labels and limits
    ax.set_xlabel("Evaluations", fontsize=20)
    ax.set_ylabel("Current error (Ec)", fontsize=20)
    ax.set_xlim(df["nevals"].iloc[0], df["nevals"].iloc[-1])
    ax.set_ylim(df["ec"].iloc[-1], df["ec"].iloc[0])

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


def ecPlot(path, parameters = 0, type = 1, multi = 0, THEME = 1, pathSave = ".", name = "ec"):
    fig, ax = configPlot(THEME)

    fig, ax = loadPlot(f"{path}.csv", fig, ax, parameters, multi, THEME)

    fig, ax = configLegend(fig, ax, THEME)

    plt.savefig(f"{pathSave}/{name}.png", format="png")
    plt.show()
