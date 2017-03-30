class SignalState:
    Red = 1
    Amber = 2
    Green = 3
    AmberAgain = 4
    Off = None

class Signal:
    def __init__(self):
        self.disable()

    def enable(self):
        self.state = SignalState.Red

    def disable(self):
        self.state = SignalState.Off

    def next(self):
        if self.state == SignalState.Red:
            self.state = SignalState.Amber
        elif self.state == SignalState.Amber:
            self.state = SignalState.Green
        elif self.state == SignalState.Green:
            self.state = SignalState.AmberAgain
        elif self.state == SignalState.AmberAgain:
            self.state = SignalState.Red
        else:
            self.state = SignalState.Off

s = Signal()
print s.state   # None
s.next()
print s.state   # None
s.enable()
print s.state   # 1
s.next()
print s.state   # 2
s.next()
print s.state   # 3
s.next()
print s.state   # 4
s.next()
print s.state   # 1
