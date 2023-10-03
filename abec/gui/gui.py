import PySimpleGUI as sg
from random import randint
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import plot.rtPlot as rtPlot
import matplotlib.colors as mcolors
import os
import sys

#plt.ion()
sg.theme("DarkGray")
"""
    Demo sg.Columns and sg.Frames
    Demonstrates using mixture of sg.Column and sg.Frame elements to create a nice window layout.
    A couple of the concepts shown here include:
    * Using sg.Columns and sg.Frames with specific sizes on them
    * Buttons that have the same text on them that arew differentiated using explicit keys
    * One way to hard-code the size of a Frame is to hard-code the size of a Column inside the frame

    CAUTION:
        Using explicit sizes on Column and Frame elements may not have the same effect on
        all computers.  Hard coding parts of layouts can sometimes not have the same result on all computers.
    
    There are 3 sg.Columns.  Two are side by side at the top and the third is along the bottom
    
    When there are multiple Columns on a row, be aware that the default is for those Columns to be
    aligned along their center.  If you want them to be top-aligned, then you need to use the
    vtop helper function to make that happen.
    
    Copyright 2021 PySimpleGUI
"""
sg.set_options(font = ("FreeMono", 14, "bold"))
sg.theme_background_color("#1c1c1c")

SYMBOL_UP =    '+'
SYMBOL_DOWN =  '-'



def collapse(layout, key):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"
    :param layout: The layout for the section
    :param key: Key used to make this seciton visible / invisible
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return sg.pin(sg.Column(layout, key=key))


# Yet another usage of MatPlotLib with animations.
def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def configAxes(ax, type = 1):
    if type == 1:
        ax[0].clear()
        ax[1].clear()
        ax[0].grid(True)
        ax[1].grid(True)
        plt.grid(which="major", color="dimgrey", linewidth=0.8)
        plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)

        ax[0].set_ylabel("Current Error (Ec)", fontsize=16)
        ax[0].set_xlim(0, 666)
        ax[1].set_xlabel("NEVALS", fontsize=16)
        ax[1].set_ylabel("Offline Error (Eo)", fontsize=16)
        '''
        ax.clear()
        ax.grid(True)
        plt.grid(which="major", color="dimgrey", linewidth=0.8)
        plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)

        ax.set_ylabel("Current Error (Ec)", fontsize=16)
        ax.set_xlim(0, 666)
        ax.set_xlabel("NEVALS", fontsize=16)
        '''

    elif type == 2:
        ax.clear()
        ax.grid(True)
        plt.grid(which="major", color="dimgrey", linewidth=0.8)
        plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)

        ax.set_ylabel("Y", fontsize=16)
        ax.set_xlim(0, 666)
        ax.set_xlabel("X", fontsize=16)

    return ax

class interface():

    def __init__(self, parameters):

        NUM_DATAPOINTS = parameters["FINISH_RUN_MODE_VALUE"]
        self.reset = 0
        self.enablePF = 1
        self.enableSS = 0



        '''
         # For now will only show the name of the file that was chosen
        self.col2 = sg.Column([
                [sg.Frame("Graphs:", [
                        [sg.Text('You choose from the list:')],
                        [sg.Text(size=(40,1), key='-TOUT-')],
                        [sg.Image(key='-IMAGE-')],
                        [sg.Slider(range=(0, NUM_DATAPOINTS), size=(60, 10),
                            orientation='h', key='-SLIDER-')]])]]
        )
        '''

        self.col1 = sg.Column([
            # Categories sg.Frame
            #[sg.Frame('Algorithm:',[[ sg.Radio('', 'radio1', default=True, key='-WEBSITES-', size=(10,1)),
            #                        sg.Radio('Software', 'radio1', key='-SOFTWARE-',  size=(10,1))]],)],
            [sg.Frame('Experiment:',[[sg.Button("Configuration File", key="-EXP-", disabled=True)]
                                    ],size=(300, 60))],

            [sg.Frame('Algorithm:',[[sg.Button("Configuration File", key="-ALGO-", disabled=True)]
                                    ],size=(300, 60))],


            [sg.Frame('Problem:',[[sg.Button("Configuration File", key="-PRO-", disabled=True)],
                                    [sg.Text("Choose the file", visible = True, key="butao")],
                                    [sg.Input(key='-FILE-', visible=False, enable_events=True), sg.FileBrowse("Input Fitness Function", visible=True, disabled=True, key="browseFit")]
                                  ],size=(300, 130))],

            [sg.Frame('Programs:',
                                [[sg.Radio("Simple Run", "program", key="program.sr", enable_events=True, visible=False)],
                                [sg.Radio("Component Evaluation", "program", enable_events=True, key="program.ct", visible=False)],
                                [sg.Combo([], key="-COMPS-", visible=False, size=(30, 10))],
                                [sg.Radio("Auto Algorithm Design", "program", key="program.aad", enable_events=True, visible=False)]
                                ],
                                size=(300, 361), visible = True, key="-PROGRAMS-")]
            ])

        performGraph = [
            [sg.Checkbox("Enable performance curves", enable_events=True, key='-HAB-PF')],
            [sg.Canvas(size=(800, 600), key='-CANVAS-PF-')]]

        sSpaceGraph = [
            [sg.Checkbox("Enable search spaces curves", enable_events=True, key='-HAB-SS')],
            [sg.Canvas(size=(800, 600), key='-CANVAS-SS-')]]


        self.col2 = sg.Column([
            [sg.TabGroup([
                [sg.Tab("Performance", performGraph)],
                [sg.Tab("Search Space", sSpaceGraph)]], size=(815, 600)
                )
            ]
        ])


        self.col3 = sg.Column([
            [sg.Frame('Terminal:',
                [[sg.Output(size=(300, 10), font=("FreeMono", 14, "bold"), background_color = "#1c1c1c", text_color="green", key="-OUTPUT-")],
                [sg.Button('Continue', key="continueBT"), sg.Button("Reset", key="resetBT", disabled=True)]
               ], size=(1140, 250))
           ]
        ])

        # The final layout is a simple one
        self.layout = [[self.col1, self.col2],
                  [self.col3]]

        # A perhaps better layout would have been to use the vtop layout helpful function.
        # This would allow the col2 column to have a different height and still be top aligned
        # layout = [sg.vtop([col1, col2]),
        #           [col3]]


       # create the form and show it without the plot
        self.window = sg.Window("AbEC - Ajustable Evolutionary Components",
                    self.layout, finalize=True)

        self.window["-HAB-PF"].update(True)
        self.window["-HAB-SS"].update(False)

        self.canvas_elem_pf = self.window["-CANVAS-PF-"]
        self.canvas_elem_ss = self.window["-CANVAS-SS-"]
        self.canvas_pf = self.canvas_elem_pf.TKCanvas
        self.canvas_ss = self.canvas_elem_ss.TKCanvas

   # window = sg.Window('Columns and Frames', layout)

    def launch(self, parameters):
        # Configure colors
        plt.style.use("dark_background")
        plt.rcParams["axes.facecolor"] = "#1c1c1c"
        plt.rcParams["savefig.facecolor"] = "#1c1c1c"
        plt.rcParams["figure.figsize"] = (8, 6)

        self.fig_pf, self.ax_pf = plt.subplots(nrows=2, ncols=1, sharex=True)
        #self.fig_pf, self.ax_pf = plt.subplots(nrows=1, ncols=1, sharex=True)
        self.fig_ss, self.ax_ss = plt.subplots(nrows=1, ncols=1, sharex=True)

        self.ax_pf = configAxes(self.ax_pf, 1)
        self.ax_ss = configAxes(self.ax_ss, 2)

        self.fig_agg_pf = draw_figure(self.canvas_pf, self.fig_pf)
        self.fig_agg_ss = draw_figure(self.canvas_ss, self.fig_ss)


    def run(self, x, y1, y2 = 0, type = 1, r=0):
        event, values = self.window.read(timeout=10)
        if event == '-HAB-PF':
            if values["-HAB-PF"] == True:
                self.enablePF = 1
            else:
                self.enablePF = 0
        elif event == '-HAB-SS':
            if values["-HAB-SS"] == True:
                self.enableSS = 1
            else:
                self.enableSS = 0
        if type == 1:
            
            self.ax_pf[0].set_xlim(x[0])
            self.ax_pf[0].plot(x, y1, c=list(mcolors.CSS4_COLORS)[r+r])
            self.ax_pf[1].plot(x, y2, c=list(mcolors.CSS4_COLORS)[r+r])
            #self.ax_pf[0].set_yscale('log')
            
            '''
            self.ax_pf.set_xlim(x[0])
            self.ax_pf.plot(x, y1, c=list(mcolors.CSS4_COLORS)[r+r])
            self.ax_pf.plot(x, y2, c=list(mcolors.CSS4_COLORS)[r+r], linestyle="--")
            self.ax_pf.set_yscale('log')
            '''
            self.fig_agg_pf.draw()
        elif type == 2:
            self.ax_ss.set_xlim(0, 100)
            self.ax_ss.set_ylim(0, 100)
            #self.ax_ss.scatter(x, y1, c="orange", label=f"ind",s=10, alpha=0.5)
            self.fig_agg_ss.draw()

    def set(self, step = 1):
        while(True):
            event, values = self.window.read()
            #print(event, values)
            if event in ('EXIT', sg.WIN_CLOSED):
                self.window.Close()
                exit()
            elif event == 'continueBT':
                if step == 1 or step == 0:
                    break
                elif step == 2:
                    break
                elif step == 3:
                    if  values["program.sr"] or \
                            values["program.ct"] or \
                            values["program.aad"]:
                        break
            elif event == "resetBT":
                self.reset = 1
                break
            elif event == '-EXP-':
                os.system("open ./frameConfig.ini")
            elif event == '-ALGO-':
                os.system("open ./algoConfig.ini")
            elif event == '-PRO-':
                os.system("open ./problemConfig.ini")
            elif event == '-HAB-PF':
                if values["-HAB-PF"] == True:
                    self.enablePF = 1
                else:
                    self.enablePF = 0
            elif event == '-HAB-SS':
                if values["-HAB-SS"] == True:
                    self.enableSS = 1
                else:
                    self.enableSS = 0
            elif event == 'program.sr':
                self.window["-COMPS-"].update(visible=False)
                self.window.refresh()
            elif event == 'program.ct':
                self.window["-COMPS-"].update(visible=True)
                self.window.refresh()
            elif event == 'program.aad':
                self.window["-COMPS-"].update(visible=False)
                self.window.refresh()
            elif(event == "-FILE-"):
                filename = values["-FILE-"].split("/")[-1]
                self.window["butao"].update(f"{filename}")

    #window.close()


#if __name__ == '__main__':
    #main()



'''
while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED:
        break

window.close()
'''
