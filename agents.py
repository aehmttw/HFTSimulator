class Agent:
    def __init__(self):
        self.balance = 10000.0
        
        # Symbol -> amount
        self.shares = dict()
        self.baseLatency = 0
     
    # Returns an Order telling what to do, or noOrder if nothing should be done
    def trade(self): # Limit order book as input or trades (market data)
        raise NotImplementedError #instead of return add to queue
    
    # Returns a latency for an action
    # If latency varies for each action by a bit, that variation can be added here to a base latency
    def _getLatency(self):
        raise NotImplementedError

#todo - add multiple agent types