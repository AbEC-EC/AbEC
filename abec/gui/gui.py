import PySimpleGUI as sg
from random import randint
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import plot.rtPlot as rtPlot
import matplotlib.colors as mcolors
import os

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
sg.set_options(font = "FreeMono 14")

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


opt1 = [[sg.Input('Input opt 1', key='-IN1-')],
[sg.Input(key='-IN11-')],
[sg.Button('Button1',  button_color='yellow on green')]]

opt2 = [[sg.I('Input opt 2', k='-IN2-')],
[sg.I(k='-IN21-')],
[sg.B('Button1',  button_color=('yellow', 'purple'))]]


c1 = [[sg.Input('Input c 1', key='-IN1-')],
[sg.Input(key='-IN11-')],
[sg.Button('Button1',  button_color='yellow on green')]]

c2 = [[sg.I('Input c 2', k='-IN2-')],
[sg.I(k='-IN21-')],
[sg.B('Button1',  button_color=('yellow', 'purple'))]]


# Yet another usage of MatPlotLib with animations.
def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

class interface():

    def __init__(self, parameters):

        NUM_DATAPOINTS = parameters["FINISH_RUN_MODE_VALUE"]

        self.col2 = sg.Column([[sg.Frame("Analysis curves:",
                                [[sg.Canvas(size=(800, 600), key='-CANVAS-')]]
                             )]]
        )

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
            [sg.Frame('Emperiment:',[[sg.Button("Configuration", key="-EXP-")]
                                    ],size=(300, 60))],

            [sg.Frame('Algorithm:',[[sg.Button("Configuration", key="-ALGO-")]
                                    ],size=(300, 60))],


            [sg.Frame('Problem:',[[sg.Button("Configuration", key="-PRO-")],
                                    [sg.Text("Choose the file", key="butao")],
                                    [sg.Input(key='-FILE-', visible=False, enable_events=True), sg.FileBrowse("Input file")]
                                  ],size=(300, 130))],

            [sg.Frame('Resume:',
                                [[sg.Text("Resumo da opera")]],
                                                size=(300, 361))]
            ])


        self.col3 = sg.Column([
            [sg.Frame('Terminal:',
                [[sg.Output(size=(300, 10), font='FreeMono 14')],
                [sg.Button('Continue')]
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


   # window = sg.Window('Columns and Frames', layout)

    def launch(self, parameters):
       # create the form and show it without the plot
        self.window = sg.Window("AbEC - Ajustable Evolutionary Components",
                    self.layout, finalize=True)

        self.canvas_elem = self.window["-CANVAS-"]
        self.canvas = self.canvas_elem.TKCanvas

        # Configure colors
        plt.style.use("dark_background")
        plt.rcParams["axes.facecolor"] = "#1c1c1c"
        plt.rcParams["savefig.facecolor"] = "#1c1c1c"
        plt.rcParams["figure.figsize"] = (8, 6)

        self.fig, self.ax = plt.subplots(nrows=2, ncols=1, sharex=True)
        #self.fig = Figure()
        #self.ax = self.fig.add_subplot(111)
        self.ax[0].grid(True)
        self.ax[1].grid(True)
        plt.grid(which="major", color="dimgrey", linewidth=0.8)
        plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)

        self.ax[0].set_ylabel("Current Error (Ec)", fontsize=16)
        self.ax[0].set_xlim(0, parameters["FINISH_RUN_MODE_VALUE"])
        self.ax[1].set_xlabel("NEVALS", fontsize=16)
        self.ax[1].set_ylabel("Offline Error (Eo)", fontsize=16)
        self.fig_agg = draw_figure(self.canvas, self.fig)


    def run(self, x, y1, y2, r=0):
        #dpts = [randint(0, 10) for x in range(NUM_DATAPOINTS)]
        #self.ax.cla()
        event, values = self.window.read(timeout=10)
        self.ax[0].plot(x, y1, c=list(mcolors.CSS4_COLORS)[r+r])
        self.ax[1].plot(x, y2, c=list(mcolors.CSS4_COLORS)[r+r])
        self.fig_agg.draw()

    def set(self):
        while(True):
            event, values = self.window.read()
            #print(event, values)
            if event == 'EXIT' or event == sg.WIN_CLOSED:
                self.window.close()
            elif event == 'Continue':
                break
            elif event == '-EXP-':
                os.system("open ./frameConfig.ini")
            elif event == '-ALGO-':
                os.system("open ./algoConfig.ini")
            elif event == '-PRO-':
                os.system("open ./problemConfig.ini")
            elif(event == "-FILE-"):
                filename = values["-FILE-"].split("/")[-1]
                #self.window("butao").update(f"{filename}")
                print(f'You chose: {filename}')

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
