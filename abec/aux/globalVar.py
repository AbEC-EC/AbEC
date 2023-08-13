
'''
    Global vars used in the framework
'''

nevals = 0
run = 0
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

def cleanGlobalVars():
    global nevals
    global run
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

    nevals = 0
    run = 0
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

'''
# datetime variables
cDate = datetime.datetime.now()
year = cDate.year
month = cDate.month
day = cDate.day
hour = cDate.hour
minute = cDate.minute
'''
