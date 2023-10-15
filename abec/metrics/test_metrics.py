import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import seaborn as sns

plt.style.use("dark_background")
plt.rcParams["axes.facecolor"] = "#1c1c1c"
plt.rcParams["savefig.facecolor"] = "#1c1c1c"
plt.rcParams["figure.figsize"] = (20, 16)

fig, ax = plt.subplots(nrows=3, ncols=2, figsize=(20, 16))

#fig.set_figheight(15)
#fig.set_figwidth(15)


#d1 = np.linspace(0, 100, num=100)
#d2 = np.linspace(10, 100, num=100)
#d3 = np.linspace(20, 100, num=100)
#d4 = np.linspace(10, 100, num=100)
#d5 = np.linspace(20, 100, num=100)

#d1 = np.random.rand(100)
#d2 = np.random.rand(100)
#d3 = np.random.rand(1000)
#d4 = np.random.rand(1000)
#d5 = np.random.rand(1000)

d1 = np.random.normal(50, 1, 1000)
d2 = np.random.normal(50, 1, 1000)
d3 = np.random.normal(50, 1, 1000)
d4 = np.random.normal(50, 1, 1000)
d5 = np.random.normal(50, 1, 1000)


data = {"d1":d1, "d2":d2, "d3":d3, "d4":d4, "d5":d5}
df = pd.DataFrame(data)
print(df)


scalar = StandardScaler()
scaled_data = pd.DataFrame(scalar.fit_transform(df)) #scaling the data
print(scaled_data)
sns.heatmap(scaled_data.corr(), ax=ax[0, 0])


# Factors of the PCA
pca = PCA()
pca.fit(scaled_data)

autovalores = pca.explained_variance_
autovetores = pca.components_

fatores_x = ['F1','F2', "F3", "F4", "F5"]
#fig.set_figheight(10)
#fig.set_figwidth(10)
ax[1, 0].bar(x=fatores_x, height= autovalores)


# Plot of the first 2 dimensions
ax[2, 0].scatter(d1, d2)
ax[2, 0].set_xlim(0, 100)
ax[2, 0].set_ylim(0, 100)
plt.grid(which="major", color="dimgrey", linewidth=0.8)
plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)
ax[2, 0].grid(True)

# Plot heatmap PCA in 2d
#fig, ax = plt.subplots()
pca = PCA(n_components = 2)
pca.fit(scaled_data)
data_pca = pca.transform(scaled_data)
data_pca = pd.DataFrame(data_pca,columns=['PC1','PC2'])
print(data_pca.head())
sns.heatmap(data_pca.corr(), ax=ax[0, 1])
#plt.show()


# Plor of the first two factors PCA
ax[2, 1].scatter(data_pca["PC1"], data_pca["PC2"])
plt.grid(which="major", color="dimgrey", linewidth=0.8)
plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)
ax[2, 1].grid(True)
ax[2, 1].set_xlim(-4, 4)
ax[2, 1].set_ylim(-4, 4)
plt.show()
