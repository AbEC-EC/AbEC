import pandas as pd
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import seaborn as sns
import ast

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
    df = pd.read_csv(path).indPos.to_frame()
    x = []
    y = []
    print(df.head())

    #Convert the column with the pos to a dataframe where each dimension
    # is a column
    x = df["indPos"].to_list()
    for i in range(len(x)):
        x[i] = ast.literal_eval(x[i])
    df2 = pd.DataFrame(x, columns=['d1','d2', "d3", "d4", "d5"])
    print(df2.head())

    scalar = StandardScaler()
    scaled_data = pd.DataFrame(scalar.fit_transform(df2)) #scaling the data
    #print(scaled_data)
    #sns.heatmap(scaled_data.corr())
    #plt.show()

    pca = PCA()
    #pca = PCA(n_components = 2)
    pca.fit(scaled_data)

    autovalores = pca.explained_variance_
    autovetores = pca.components_

    #data_pca = pca.transform(scaled_data)
    #data_pca = pd.DataFrame(data_pca,columns=['PC1','PC2'])
    #print(data_pca.head())
    #sns.heatmap(data_pca.corr())
    #plt.show()

    fatores_x = ['F1','F2','F3', 'F4','F5']
    fig.set_figheight(10)
    fig.set_figwidth(10)
    ax.bar(x=fatores_x, height= autovalores)
    plt.show()

    #x = pca.inverse_transform(data_pca)
    #print(x)
    #x = data_pca["PC1"].to_list()
    #y = data_pca["PC2"].to_list()

    '''
    for row in df["indPos"]:
        pos = row.strip('][').split(', ')
        x.append(float(pos[0]))
        y.append(float(pos[1]))
    '''

    #ax.scatter(x, y, label=f"Ind", s=0.5, alpha=0.5)

    if multi:
        ax.fill_between(df["nevals"], df["eo"] - df["eo_std"], df["eo"]+ df["eo_std"], alpha=0.05)

    # Axes labels and limits
    ax.set_xlabel("X", fontsize=20)
    ax.set_ylabel("Y", fontsize=20)
    ax.set_xticks([-100, -75, -50, -25, 0, 25, 50, 75, 100])
    ax.set_yticks([-100, -75, -50, -25, 0, 25, 50, 75, 100])
    #ax.set_xlim(parameters["MIN_POS"], parameters["MAX_POS"])
    #ax.set_ylim(parameters["MIN_POS"], parameters["MAX_POS"])
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    #print(f"x: {min(x)}, {max(x)}")
    #print(f"y: {min(y)}, {max(y)}")

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
    #plt.show()
