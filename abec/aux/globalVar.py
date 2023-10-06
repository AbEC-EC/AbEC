
'''
    Global vars used in the framework
'''

path = "."
header = ""
filename = ""
runs = []
bestRuns = []
best = None
seedInit = 0
year = 0
month = 0
day = 0
hour = 0
minute = 0


def cleanGlobalVars():
    global nevals
    global run
    global runs
    global gen
    global eo_sum
    global mpb
    global rng
    global best
    global alreadyEvaluated
    global changeEnv
    global flagChangeEnv
    global path
    global peaks
    global randomInit
    global seedInit
    global npops
    global change
    global changeEV
    global tot_pos
    global sspace
    global res
    global Fr

    nevals = 0
    run = 0
    runs = []
    gen = 0
    eo_sum = 0
    mpb = None
    rng = None
    best = None
    alreadyEvaluated = []
    changeEnv = 0
    flagChangeEnv = 0
    path = "."
    peaks = 0
    randomInit = [0]
    seedInit = 0
    npops = 0
    change = 0
    changeEV = 1
    tot_pos = 0
    sspace = []
    res = 0.5
    Fr = 0

'''
# datetime variables
= datetime.datetime.now()
year = year
month = month
day = day
hour = hour
minute = minute
'''
