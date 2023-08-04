

import matplotlib.pyplot as plt

plt.ion()


class plotUpdate():

    def __init__(self, parameters):
        #Suppose we know the x range
        self.min_x = 0
        self.max_x = parameters["FINISH_RUN_MODE_VALUE"]
        self.min_y = 0
        self.max_y = 10


    def on_launch(self, parameters):
        #Set up plot
        #CONFIGURE
        self.configPlot(GRID = 1)
        #self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([],[])

        #Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(True)
        self.ax.set_xlim(self.min_x, self.max_x)
        #self.ax.set_xlim(self.min_x, self.max_x)
        #Other stuff
        self.ax.grid(True)
        ...

    def on_running(self, xdata, ydata):
        #Update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def configPlot(self, THEME = 1, GRID = 1):
        # Configure colors
        plt.style.use("dark_background")
        plt.rcParams["axes.facecolor"] = "#1c1c1c"
        plt.rcParams["savefig.facecolor"] = "#1c1c1c"
        plt.rcParams["figure.figsize"] = (16, 9)
        if(THEME == 1):
            plt.style.use("dark_background")
            plt.rcParams["axes.facecolor"] = "#1c1c1c"
            plt.rcParams["savefig.facecolor"] = "#1c1c1c"
            plt.rcParams["figure.figsize"] = (16, 9)
        elif(THEME == 2):
            plt.rcParams["axes.facecolor"] = "white"
            plt.rcParams["figure.figsize"] = (11, 8)

        self.fig, self.ax = plt.subplots(1)

        # Color of grids
        if(GRID == 1):
            self.ax.grid(True)
            plt.grid(which="major", color="dimgrey", linewidth=0.8)
            plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)
        else:
            self.ax.grid(False)


    #Example
    def __call__(self):
        import numpy as np
        import time
        self.on_launch()
        xdata = []
        ydata = []
        for x in np.arange(0,10,0.1):
            xdata.append(x)
            ydata.append(np.sin(x))
            self.on_running(xdata, ydata)
            time.sleep(0.1)
        return xdata, ydata

