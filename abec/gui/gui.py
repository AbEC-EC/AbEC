import PySimpleGUI as sg
from random import randint
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import plot.rtPlot as rtPlot

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


# Yet another usage of MatPlotLib with animations.

def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

class interface():

    def __init__(self, parameters):

        NUM_DATAPOINTS = parameters["FINISH_RUN_MODE_VALUE"]

        self.col2 = sg.Column([[sg.Frame("Graphs:", [[sg.Text('Current Error (Ec)', size=(40, 1),
                        justification='center', font='Helvetica 20')],
                      [sg.Canvas(size=(600, 400), key='-CANVAS-')],
                      [sg.Text('Number os Evaluations (NEVALS)')],
                      [sg.Slider(range=(0, NUM_DATAPOINTS), size=(60, 10),
                        orientation='h', key='-SLIDER-')]])]]
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
            [sg.Frame('Categories:',[[ sg.Radio('Websites', 'radio1', default=True, key='-WEBSITES-', size=(10,1)),
                                    sg.Radio('Software', 'radio1', key='-SOFTWARE-',  size=(10,1))]],)],
            # Information sg.Frame
            [sg.Frame('Information:', [[sg.Text(), sg.Column([[sg.Text('Account:')],
                                     [sg.Input(key='-ACCOUNT-IN-', size=(19,1))],
                                     [sg.Text('User Id:')],
                                     [sg.Input(key='-USERID-IN-', size=(19,1)),
                                      sg.Button('Copy', key='-USERID-')],
                                     [sg.Text('Password:')],
                                     [sg.Input(key='-PW-IN-', size=(19,1)),
                                      sg.Button('Copy', key='-PASS-')],
                                     [sg.Text('Location:')],
                                     [sg.Input(key='-LOC-IN-', size=(19,1)),
                                      sg.Button('Copy', key='-LOC-')],
                                     [sg.Text('Notes:')],
                                     [sg.Multiline(key='-NOTES-', size=(25,5))],
                                     ], size=(235,350), pad=(0,0))]])], ], pad=(0,0))

        self.col3 = sg.Column([[sg.Frame('Actions:',
                                    [[sg.Column([[sg.Button('Save'), sg.Button('Clear'), sg.Button('Delete'), ]],
                                                size=(450,45), pad=(0,0))]])]], pad=(0,0))

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
        self.window = sg.Window('Demo Application - Embedding Matplotlib In PySimpleGUI',
                    self.layout, finalize=True)

        self.canvas_elem = self.window["-CANVAS-"]
        self.slider_elem = self.window['-SLIDER-']
        self.slider_elem.update(0)       # slider shows "progress" through the data points
        self.canvas = self.canvas_elem.TKCanvas

        # Configure colors
        plt.style.use("dark_background")
        plt.rcParams["axes.facecolor"] = "#1c1c1c"
        plt.rcParams["savefig.facecolor"] = "#1c1c1c"
        plt.rcParams["figure.figsize"] = (6, 4)

        #self.fig, self.ax = plt.subplots(1)
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True)
        plt.grid(which="major", color="dimgrey", linewidth=0.8)
        plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)

        self.ax.set_xlabel("NEVALS")
        self.ax.set_ylabel("Current Error (Ec)")
        self.ax.set_xlim(0, parameters["FINISH_RUN_MODE_VALUE"])
        self.fig_agg = draw_figure(self.canvas, self.fig)


    def run(self, x, y):
        #dpts = [randint(0, 10) for x in range(NUM_DATAPOINTS)]
        #self.ax.cla()
        event, values = self.window.read(timeout=10)
        self.ax.plot(x, y, c="orange")
        self.slider_elem.update(x[-1])       # slider shows "progress" through the data points
        self.fig_agg.draw()

    '''
    def __call__(self):
        for i in range(len(dpts)):

            event, values = window.read(timeout=10)
            if event in ('Exit', None):
                exit(69)
            
            ax.cla()                    # clear the subplot
            ax.grid()                   # draw the grid
            ax.set_xlim(0, 1000)
            #data_points = int(values['-SLIDER-DATAPOINTS-']) # draw this many data points (on next line)
            #ax.plot(0, dpts[i:i+data_points],  color='purple')
            ax.plot(range(i), dpts[0:i],  color='purple')
            fig_agg.draw()
    '''

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
