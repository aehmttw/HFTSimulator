import pandas as pd
import matplotlib.pyplot as plotter
import numpy as np

class Grapher:
    def __init__(self, dir: str, amount: int):
        self.dir: str = dir
        self.amount: int = amount
        self.data = list()

        for i in range(amount):
        #    print("Reading " + str(i))
            self.data.append(pd.read_csv(dir + str(i) + ".csv"))

    def graphAll(self, property: str):
        plotter.figure()
        plotter.xlabel("Time")
        plotter.ylabel(property)
        colors = ["#ff0000", "#ff0f00", "#ff1e00", "#ff2d00", "#ff3d00", "#ff4c00", "#ff5b00", "#ff6b00", "#ff7a00", "#ff8900", "#ff9900", "#ffa800", "#ffb700", "#ffc600", "#ffd600", "#ffe500", "#fff400", "#f9ff00", "#eaff00", "#dbff00", "#ccff00", "#bcff00", "#adff00", "#9eff00", "#8eff00", "#7fff00", "#70ff00", "#60ff00", "#51ff00", "#42ff00", "#33ff00", "#23ff00", "#14ff00", "#05ff00", "#00ff0a", "#00ff19", "#00ff28", "#00ff38", "#00ff47", "#00ff56", "#00ff66", "#00ff75", "#00ff84", "#00ff93", "#00ffa3", "#00ffb2", "#00ffc1", "#00ffd1", "#00ffe0", "#00ffef", "#00ffff", "#00efff", "#00e0ff", "#00d1ff", "#00c1ff", "#00b2ff", "#00a3ff", "#0093ff", "#0084ff", "#0075ff", "#0066ff", "#0056ff", "#0047ff", "#0038ff", "#0028ff", "#0019ff", "#000aff", "#0500ff", "#1400ff", "#2300ff", "#3300ff", "#4200ff", "#5100ff", "#6000ff", "#7000ff", "#7f00ff", "#8e00ff", "#9e00ff", "#ad00ff", "#bc00ff", "#cc00ff", "#db00ff", "#ea00ff", "#f900ff", "#ff00f4", "#ff00e5", "#ff00d6", "#ff00c6", "#ff00b7", "#ff00a8", "#ff0099", "#ff0089", "#ff007a", "#ff006b", "#ff005b", "#ff004c", "#ff003d", "#ff002d", "#ff001e", "#ff000f"]

        df = self.data[0]
    
        i: int = 0
        for dataFrame in self.data:
            plotter.plot(np.array(dataFrame.loc[:, "Timestamp"]), np.array(dataFrame.loc[:, property]), color=colors[(i * 11) % 100])
            i += 1
