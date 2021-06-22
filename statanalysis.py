import pandas as pd
import matplotlib.pyplot as plotter
import numpy as np
import multiprocessing
import sys

# This class compiles and prints statistics from multiple runs of a given simulation, after they have all been run.
class StatsAnalyzer:
    def __init__(self, dir: str, amount: int):
        self.dir: str = dir
        self.amount: int = amount
        self.data = dict()
        self.rows = 0

        df0 = df = pd.read_csv(dir + "0.csv")
        self.agentGroups = list()

        for i in range(len(df0.columns)):
            if i - 8 >= 0 and (i - 8) % 5 == 0:
                self.agentGroups.append(df0.columns.values[i])

        for i in range(amount):
            df = pd.read_csv(dir + str(i) + ".csv")
            
            index = 0

            for row in df["Agent"]:
                if not(row in self.data):
                    self.data[row] = AgentStats(row, self.agentGroups)

                self.data[row].ordersSent += df.loc[index, "OrdersSent"]
                self.data[row].ordersMatched += df.loc[index, "OrdersMatched"]
                self.data[row].ordersCanceled += df.loc[index, "OrdersCanceled"]
                self.data[row].ordersStanding += df.loc[index, "OrdersStanding"]

                if not np.isnan(df.loc[index, "AveragePriceTraded"]): # fix amounts
                    self.data[row].transactPriceSum += df.loc[index, "AveragePriceTraded"]
                    self.data[row].tradedPresentCount += 1

                if not np.isnan(df.loc[index, "AveragePriceBuy"]):
                    self.data[row].transactPriceSumBuy += df.loc[index, "AveragePriceBuy"]
                    self.data[row].boughtPresentCount += 1

                if not np.isnan(df.loc[index, "AveragePriceSell"]):
                    self.data[row].transactPriceSumSell += df.loc[index, "AveragePriceSell"]
                    self.data[row].soldPresentCount += 1

                for agent in self.data[row].transactAgents:
                    self.data[row].transactAgents[agent] += df.loc[index, agent]
                    self.data[row].transactAgentBuyCount[agent] += df.loc[index, agent + "BuyCount"]
                    self.data[row].transactAgentSellCount[agent] += df.loc[index, agent + "SellCount"]

                    if not np.isnan(df.loc[index, agent + "BuyPrice"]):
                        self.data[row].transactAgentBuyPrices[agent] += df.loc[index, agent + "BuyPrice"]
                        self.data[row].agentBoughtPresentCount[agent] += 1

                    if not np.isnan(df.loc[index, agent + "SellPrice"]):
                        self.data[row].transactAgentSellPrices[agent] += df.loc[index, agent + "SellPrice"]
                        self.data[row].agentSoldPresentCount[agent] += 1

                index += 1

            del df

    # For each agent, prints numbers of orders sent, matched, canceled, and remaining in the order book;
    # average price at which the agent traded in general, 
    # and a breakdown of the agent's trades, by the other agent it traded with
    def print(self):
        for agent in self.data:
            a = self.data[agent]
            s = agent + ", Sent: " + str(a.ordersSent) + ", Matched: " + str(a.ordersMatched) + ", Canceled: " + str(a.ordersCanceled) + ", Standing: " + str(a.ordersStanding)
            s += ", Avg. Trade Price: " + str(a.transactPriceSum / a.tradedPresentCount) + ", Avg. Buy Price: " + str(a.transactPriceSumBuy / a.boughtPresentCount) + ", Avg. Sell Price: " + str(a.transactPriceSumSell / a.soldPresentCount)
            
            for agent in a.transactAgents:
                if a.transactAgents[agent] > 0:
                    s += ", Traded " + str(a.transactAgents[agent]) + "x with " + agent + " (" + str(a.transactAgentBuyCount[agent]) + " buy at avg. " + str(a.transactAgentBuyPrices[agent] / a.agentBoughtPresentCount[agent]) + ", " + str(a.transactAgentSellCount[agent]) + " sell at avg. " + str(a.transactAgentSellPrices[agent] / a.agentSoldPresentCount[agent]) + ")"

            print(s)

# One agent's stats
class AgentStats:
    def __init__(self, name: str, agents: list):
        self.name = name

        self.ordersSent = 0
        self.ordersMatched = 0
        self.ordersCanceled = 0
        self.ordersStanding = 0

        self.transactPriceSum = 0
        self.transactPriceSumBuy = 0
        self.transactPriceSumSell = 0

        self.transactAgents = dict()
        
        self.transactAgentBuyCount = dict()
        self.transactAgentSellCount = dict()
        self.transactAgentBuyPrices = dict()
        self.transactAgentSellPrices = dict()

        self.tradedPresentCount = 0
        self.boughtPresentCount = 0
        self.soldPresentCount = 0
        
        self.agentBoughtPresentCount = dict()
        self.agentSoldPresentCount = dict()           

        for agent in agents:
            self.agentBoughtPresentCount[agent] = 0
            self.agentSoldPresentCount[agent] = 0

            self.transactAgents[agent] = 0
            self.transactAgentBuyCount[agent] = 0
            self.transactAgentSellCount[agent] = 0
            self.transactAgentBuyPrices[agent] = 0
            self.transactAgentSellPrices[agent] = 0

# Print an analysis of the stats generated by the running of multiple simulations under one setup
def analyzeStats(name: str, count: int):
    g = StatsAnalyzer("runs/" + name + "/stats", count)
    g.print()


def main():
    # Edit this line to specify which setup you want to analyze stats for, and how many simulations were run
    # Make sure you have run the simulations in the tester file first!
    analyzeStats("3speedsqa", 100)

if __name__ == "__main__":
    main()
