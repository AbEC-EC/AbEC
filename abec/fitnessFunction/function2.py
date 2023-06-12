import numpy as np

optimal = [-np.sqrt(2), 0]

def equation(s):
    return 5*s[0]*np.exp(- ( ((s[0])**2) + ((s[1])**2) )/4)

def function(x, nevals):
    opt = equation(optimal)
    fit = equation(x)
    #error = abs(opt - fit)
    return fit
