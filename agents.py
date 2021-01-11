class Agent:
    def __init__(self):
        self.balance = 10000.0
        
        # Symbol -> amount
        self.shares = dict()
        self.baseLatency = 0
     
    def inputData(self, trade: 'Trade'):
        raise NotImplementedError #add to own record of data

    # Returns an Order telling what to do, or noOrder if nothing should be done
    # Make sure to set the order timestamp based on the latency
    def trade(self): # Limit order book as input or trades (market data)
        raise NotImplementedError #instead of return add to queue
    
    # Returns a latency for an action
    # If latency varies for each action by a bit, that variation can be added here to a base latency
    # Maybe add other latencies to separate places too, depending on how this will be implemented
    def getLatency(self) -> int:
        raise NotImplementedError

# todo - add multiple agent types

# one agent will use a simple algorithm
# another could be a market maker w/ historical data