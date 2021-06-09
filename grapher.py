import pandas as pd
import matplotlib.pyplot as plotter
import numpy as np
import multiprocessing
import sys

class Grapher:
    def __init__(self, dir: str, amount: int, interval: float, limits: list):
        self.dir: str = dir
        self.amount: int = amount
        self.data = list()
        self.rows = 0
        self.interval = interval
        
        self.lowerlimits = dict()
        self.upperlimits = dict()

        for l in limits:
            self.addLimits(l[0], l[1], l[2])

        for i in range(amount):
        #    print("Reading " + str(i))
            df = pd.read_csv(dir + str(i) + ".csv")

            indexes = list()
            i = 0
            last = 0

            for col in df["Timestamp"]:
                if i > 0:
                    dif = int(col / interval) - int(last / interval)
                    for j in range(dif):
                        indexes.append(i - 1)
                
                last = col

                i += 1

            self.rows = max(self.rows, len(indexes))

            df2 = df.iloc[indexes]
            df2.reset_index()
            self.data.append(df2)
            del df

    def addLimits(self, property: str, lower: float, upper: float):
        self.lowerlimits[property] = lower
        self.upperlimits[property] = upper

    def graphAll(self, property: str):
        plotter.figure()
        plotter.xlabel("Time")
        plotter.ylabel(property)
        colors = ["#ff0000", "#ff0f00", "#ff1e00", "#ff2d00", "#ff3d00", "#ff4c00", "#ff5b00", "#ff6b00", "#ff7a00", "#ff8900", "#ff9900", "#ffa800", "#ffb700", "#ffc600", "#ffd600", "#ffe500", "#fff400", "#f9ff00", "#eaff00", "#dbff00", "#ccff00", "#bcff00", "#adff00", "#9eff00", "#8eff00", "#7fff00", "#70ff00", "#60ff00", "#51ff00", "#42ff00", "#33ff00", "#23ff00", "#14ff00", "#05ff00", "#00ff0a", "#00ff19", "#00ff28", "#00ff38", "#00ff47", "#00ff56", "#00ff66", "#00ff75", "#00ff84", "#00ff93", "#00ffa3", "#00ffb2", "#00ffc1", "#00ffd1", "#00ffe0", "#00ffef", "#00ffff", "#00efff", "#00e0ff", "#00d1ff", "#00c1ff", "#00b2ff", "#00a3ff", "#0093ff", "#0084ff", "#0075ff", "#0066ff", "#0056ff", "#0047ff", "#0038ff", "#0028ff", "#0019ff", "#000aff", "#0500ff", "#1400ff", "#2300ff", "#3300ff", "#4200ff", "#5100ff", "#6000ff", "#7000ff", "#7f00ff", "#8e00ff", "#9e00ff", "#ad00ff", "#bc00ff", "#cc00ff", "#db00ff", "#ea00ff", "#f900ff", "#ff00f4", "#ff00e5", "#ff00d6", "#ff00c6", "#ff00b7", "#ff00a8", "#ff0099", "#ff0089", "#ff007a", "#ff006b", "#ff005b", "#ff004c", "#ff003d", "#ff002d", "#ff001e", "#ff000f"]
    
        i: int = 0
        for dataFrame in self.data:
            plotter.plot(np.array(dataFrame.loc[:, "Timestamp"]), np.array(dataFrame.loc[:, property]), color=colors[(i * 11) % 100])
            i += 1

    def graphAvg(self, property: str, interval: float, chained: bool = False, color1: str = "#0000ff", color2: str = "#7f7fff"):
        if not chained:
            plotter.figure()
            plotter.xlabel("Time")
            plotter.ylabel(property)
            
            if property in self.lowerlimits:
                plotter.ylim([self.lowerlimits[property], self.upperlimits[property]])
        
        #colors = ["#ff0000", "#ff0f00", "#ff1e00", "#ff2d00", "#ff3d00", "#ff4c00", "#ff5b00", "#ff6b00", "#ff7a00", "#ff8900", "#ff9900", "#ffa800", "#ffb700", "#ffc600", "#ffd600", "#ffe500", "#fff400", "#f9ff00", "#eaff00", "#dbff00", "#ccff00", "#bcff00", "#adff00", "#9eff00", "#8eff00", "#7fff00", "#70ff00", "#60ff00", "#51ff00", "#42ff00", "#33ff00", "#23ff00", "#14ff00", "#05ff00", "#00ff0a", "#00ff19", "#00ff28", "#00ff38", "#00ff47", "#00ff56", "#00ff66", "#00ff75", "#00ff84", "#00ff93", "#00ffa3", "#00ffb2", "#00ffc1", "#00ffd1", "#00ffe0", "#00ffef", "#00ffff", "#00efff", "#00e0ff", "#00d1ff", "#00c1ff", "#00b2ff", "#00a3ff", "#0093ff", "#0084ff", "#0075ff", "#0066ff", "#0056ff", "#0047ff", "#0038ff", "#0028ff", "#0019ff", "#000aff", "#0500ff", "#1400ff", "#2300ff", "#3300ff", "#4200ff", "#5100ff", "#6000ff", "#7000ff", "#7f00ff", "#8e00ff", "#9e00ff", "#ad00ff", "#bc00ff", "#cc00ff", "#db00ff", "#ea00ff", "#f900ff", "#ff00f4", "#ff00e5", "#ff00d6", "#ff00c6", "#ff00b7", "#ff00a8", "#ff0099", "#ff0089", "#ff007a", "#ff006b", "#ff005b", "#ff004c", "#ff003d", "#ff002d", "#ff001e", "#ff000f"]
    
        
        time: float = 0

        timestamps = list()
        #averages = list()
        #deviations = list()

        medians = list()
        p5 = list()
        p95 = list() 

        #print(self.rows)
        for j in range(self.rows):
            time = j * interval

            i: int = 0

            currentVals = np.zeros(100)

            for dataFrame in self.data:
                #print(j)
                r = dataFrame.iloc[j, :]
                currentVals[i] = r.loc[property]
                i += 1

            sorted = np.sort(currentVals)

            medians.append((sorted[49] + sorted[50]) / 2)
            p5.append(sorted[4])
            p95.append(sorted[94])
            timestamps.append(time)
        
        plotter.plot(timestamps, medians, color1)
        plotter.plot(timestamps, p5, color2)
        plotter.plot(timestamps, p95, color2)

    def saveAllAvg(self):
        groups = dict()
        for key in self.data[0].keys():
            if key != "Timestamp":
                if "/" in key:
                    first = key.split("/")[0]

                    if not(first in groups):
                        groups[first] = list()
                    
                    groups[first].append(key)
                else:
                    p = multiprocessing.Process(target=self.graphAndSaveOne, args=(key, self.interval,))
                    p.start()

        for key in groups:
            p = multiprocessing.Process(target=self.graphAndSaveGroup, args=(key, self.interval, groups[key]))
            p.start()

    def graphAndSaveOne(self, key, interval):
        self.graphAvg(key, interval)
        plotter.savefig(self.dir + "-" + key.replace("/", "-") + ".png")

    def graphAndSaveGroup(self, key, interval, group):
        plotter.figure()
        plotter.xlabel("Time")
        plotter.ylabel(key)

        if key in self.lowerlimits:
            plotter.ylim([self.lowerlimits[key], self.upperlimits[key]])

        l: list = list()

        colors = ["#0000ff", "#00ff00", "#ff0000", "#ff00ff", "#00ffff", "#ffff00", "#000000"]
        colors2 = ["#7f7fff", "#7fff7f", "#ff7f7f", "#ff7fff", "#7fffff", "#ffff7f", "#7f7f7f"]
 
        index: int = 0
        for s in group:
            self.graphAvg(s, interval, True, colors[index % len(colors)], colors2[index % len(colors2)])
            index += 1
            s: str = s.split("/")[1]
            l.append(s)
            l.append("_" + s + " 5%")
            l.append("_" + s + " 95%")

        plotter.legend(l)
        plotter.savefig(self.dir + "-" + key + ".png")

def main():
    limits = list()

    limits.append(("Net Worth", 9997000, 10003000))
    limits.append(("Book Size", 0, 70))
    limits.append(("Gap", 0, 100))
    #self.addLimits("sqa-agent Orders", 0, 5000)
    #self.addLimits("sqa-agent2 Orders", 0, 5000)
    #self.addLimits("sqa-agent-slow Orders", 0, 5000)

    g = Grapher("runs/3speedsqa/output", 100, 5000, limits)
    g.saveAllAvg()

if __name__ == "__main__":
    main()
