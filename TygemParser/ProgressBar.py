import sys
import re
import time

# Slightly modified and from https://stackoverflow.com/a/36985003/7965931
class ProgressBar(object):
    DEFAULT = 'Progress: %(bar)s %(percent)3d%%'
    FULL = '%(bar)s %(current)d/%(total)d (%(percent)3d%%) %(remaining)d to go %(time left:)d seconds left'

    def __init__(self, total, width=40, fmt=DEFAULT, symbol='=',
                 output=sys.stderr):
        assert len(symbol) == 1

        self.total = total
        self.width = width
        self.symbol = symbol
        self.output = output
        self.fmt = re.sub(r'(?P<name>%\(.+?\))d',
            r'\g<name>%dd' % len(str(total)), fmt)

        self.current = 0
        self.time = time.time()
        self.timeRemaining = 0
        self.updateTime = total // 300
        self.updateIdx = 0
        self.processedSince = 0

    def __call__(self, count):
        percent = self.current / float(self.total)
        size = int(self.width * percent)
        remaining = self.total - self.current
        bar = '[' + self.symbol * size + ' ' * (self.width - size) + ']'

        self.updateIdx += 1
        self.processedSince += count
        if self.updateIdx >= self.updateTime:
            self.timeRemaining = self.timeLeft(count, remaining)

        args = {
            'total': self.total,
            'bar': bar,
            'current': self.current,
            'percent': percent * 100,
            'remaining': remaining,
            'time left:': self.timeRemaining
        }
        print('\r' + self.fmt % args, file=self.output, end='')
        self.current += count

    def timeLeft(self, itemsInTime, remaining):
        t           = time.time()
        processedIn = t - self.time
        self.time   = t
        processed = self.processedSince
        self.processedSince = 0
        self.updateIdx = 0
        if processed == 0:
            return 0

        return remaining * (processedIn / processed)

    def done(self):
        self.current = self.total
        self()
        print('', file=self.output)
