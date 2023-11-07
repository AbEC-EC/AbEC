import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import seaborn as sns
import matplotlib.colors as mcolors

from sklearn.decomposition import TruncatedSVD
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn import manifold
from sklearn.pipeline import Pipeline

plt.style.use("dark_background")
plt.rcParams["axes.facecolor"] = "#1c1c1c"
plt.rcParams["savefig.facecolor"] = "#1c1c1c"
plt.rcParams["figure.figsize"] = (20, 16)



def PCA_reduction(df, plotDebug = 0):
    
    if (plotDebug):
        fig, ax = plt.subplots(nrows=3, ncols=2, figsize=(20, 16))
        sns.heatmap(df.corr(), ax=ax[0, 0])        
        
        
    pca = PCA(n_components = 2)
    pca.fit(df)
    
    autovalores = pca.explained_variance_
    autovetores = pca.components_
    fatores_x = ['F1','F2', "F3", "F4", "F5"]
    
    data_pca = pca.transform(df)
    data_pca = pd.DataFrame(data_pca,columns=['PC1','PC2'])
    print(data_pca.head())
    
    if (plotDebug):
        #fig.set_figheight(10)
        #fig.set_figwidth(10)
        ax[1, 0].bar(x=fatores_x, height= autovalores)


        # Plot of the first 2 dimensions
        ax[2, 0].scatter(df["d1"], df["d2"])
        ax[2, 0].set_xlim(0, 100)
        ax[2, 0].set_ylim(0, 100)
        plt.grid(which="major", color="dimgrey", linewidth=0.8)
        plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)
        ax[2, 0].grid(True)

        # Plot heatmap PCA in 2d
        #fig, ax = plt.subplots()
        
        sns.heatmap(data_pca.corr(), ax=ax[0, 1])
        
        ax[2, 1].scatter(data_pca["PC1"], data_pca["PC2"])
        plt.grid(which="major", color="dimgrey", linewidth=0.8)
        plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)
        ax[2, 1].grid(True)
        ax[2, 1].set_xlim(-4, 4)
        ax[2, 1].set_ylim(-4, 4)
        plt.show()
    
    return data_pca["PC1"].to_list(), data_pca["PC2"].to_list()

def SVD_reduction(df, plotDebug = 0):
    svd = TruncatedSVD(2)
    x = []
    y  =[]

    data_svd = svd.fit_transform(df)
    print(data_svd)
    for i in range(len(data_svd)):
        x.append(data_svd[i][0])
        y.append(data_svd[i][1])
    return x, y

def ISOMAP_reduction(df, plotDebug = 0):  
    iso = manifold.Isomap(n_components = 2)
    iso.fit(df)
    manifold_2Da = iso.transform(df)
    manifold_2D = pd.DataFrame(manifold_2Da, columns=['c1', 'c2'])
    print(manifold_2D)
    return manifold_2D["c1"].to_list(), manifold_2D["c1"].to_list()

def LLE_reduction(df, plotDebug = 0):  
    lle = manifold.LocallyLinearEmbedding(n_components = 2)
    #lle.fit(df)
    x = []
    y  =[]

    data_lle = lle.fit_transform(df)
    print(data_lle)
    for i in range(len(data_lle)):
        x.append(data_lle[i][0])
        y.append(data_lle[i][1])
    return x, y


def main(): 
    
    scaler = 0
    
    
    df = []
    vd1 = 0
    vd2 = 0
    vd3 = 0
    vd4 = 0
    vd5 = 0
    for variance in [1, 20, 50]:
        
        d1 = np.random.normal(50, variance+vd1, 1000)
        d2 = np.random.normal(50, variance+vd2, 1000)
        d3 = np.random.normal(50, variance+vd3, 1000)
        d4 = np.random.normal(50, variance+vd4, 1000)
        d5 = np.random.normal(50, variance+vd5, 1000)
        
        data = {"d1":d1, "d2":d2, "d3":d3, "d4":d4, "d5":d5}
        dframe = pd.DataFrame(data)
        
        if(scaler):
            scalar = StandardScaler()
            dframe = pd.DataFrame(scalar.fit_transform(dframe)) #scaling the data
        
        df.append(dframe)
        
        

    methods = ["PCA", "SVD", "ISOMAP", "LLE"]
    fig, ax = plt.subplots(nrows=3, ncols=len(methods)+1, figsize=(20, 16))
    
    ax[0, 0].set_title(f"Raw data")
    for i, data in enumerate(df):
        if(scaler):
            ax[i, 0].scatter(data[0], data[1])
            ax[i, 0].set_xlim(-4, 4)
            ax[i, 0].set_ylim(-4, 4)
        else:
            ax[i, 0].scatter(data["d1"], data["d2"])
            ax[i, 0].set_xlim(0, 100)
            ax[i, 0].set_ylim(0, 100)
        plt.grid(which="major", color="dimgrey", linewidth=0.8)
        plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)
        ax[i, 0].grid(True)
        
        
            
        for j, algo in enumerate(methods):
            if(i == 0):
                ax[i, 1+j].set_title(f"{algo}")
            if (algo == "ISOMAP"):
                x, y = ISOMAP_reduction(data)
            elif (algo == "SVD"):
                x, y = SVD_reduction(data)
            elif (algo == "PCA"):
                x, y = PCA_reduction(data)
            elif (algo == "LLE"):
                x, y = LLE_reduction(data)
            
            ax[i, 1+j].scatter(x, y, label=f"{algo}", c=list(mcolors.CSS4_COLORS)[j])
            plt.grid(which="major", color="dimgrey", linewidth=0.8)
            plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)
            ax[i, 1+j].grid(True)
            if(scaler):
                ax[i, 1+j].set_xlim(-4, 4)
                ax[i, 1+j].set_ylim(-4, 4)
            else:
                ax[i, 1+j].set_xlim(-150, 200)
                ax[i, 1+j].set_ylim(-150, 200)
    
    
            
            
    plt.savefig(f"aee-{variance}.png", format="png")
    plt.show()
        
    
    
  
# Using the special variable  
# __name__ 
if __name__=="__main__": 
    main() 