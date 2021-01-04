import simpy

class Event:
    def __init__(self, env):
        self.env = env
        self.action = env.process(self.run())

    def run(self):
       while True:
           pass
           #todo - add events

