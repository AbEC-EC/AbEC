# Graphic interface
    if layout:
        #Lists for real time graphs
        runVars.rtPlotNevals.append(runVars.nevals)
        runVars.rtPlotError.append(runVars.best["fit"])
        runVars.rtPlotEo.append(runVars.Eo)
        runVars.rtPlotFr.append(runVars.Fr)

        layout.window.refresh()
        if layout.enablePF:
            layout.run(runVars.rtPlotNevals, runVars.rtPlotError, runVars.rtPlotEo)
        if layout.enableSS:
            xSS, ySS = getSearchSpace(subpop, layout)
            layout.run(x = xSS, y1 = ySS, type = 2)
            



            if layout:
                layout.ax_ss.scatter(subpop.best['pos'][0], subpop.best['pos'][1], c="white", s=0.5)
                

        # Graphic interface
        if layout:
            #Lists for real time graphs
            runVars.rtPlotNevals.append(runVars.nevals)
            runVars.rtPlotError.append(runVars.best["fit"])
            runVars.rtPlotEo.append(runVars.Eo)
            runVars.rtPlotFr.append(runVars.Fr)

            layout.window.refresh()
            if layout.enablePF:
                layout.run(runVars.rtPlotNevals, runVars.rtPlotError, runVars.rtPlotEo, r = runVars.id())
            if layout.enableSS:
                xSS, ySS = getSearchSpace(runVars.pop, layout)
                layout.ax_ss.scatter(runVars.best["pos"][0], runVars.best["pos"][1], c="red", s=50 )
                layout.run(x = xSS, y1 = ySS, type = 2)
                
def getSearchSpace(pop, layout):
    x = []
    y = []
    i = 0
    for subpop in pop:
        x = [d["pos"][0] for d in subpop.ind]
        y = [d["pos"][1] for d in subpop.ind]
        layout.ax_ss.scatter(x, y, c=list(mcolors.CSS4_COLORS)[i], s=0.5, alpha=0.5)
        #layout.ax_ss.scatter(subpop.best["pos"][0], subpop.best["pos"][1], c=list(mcolors.CSS4_COLORS)[i], s=80, alpha=0.8 )
        #print(f"{subpop.best['pos']}, {subpop.best['fit']}")
        i += 1
    return x, y
