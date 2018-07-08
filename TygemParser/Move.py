#import numpy as np
from Globals import BoardDepth, BoardLength, BoardSize, BoardLengthP, BoardSizeP
from Globals import EMPTY, BLACK, WHITE, OFF_BOARD

def moveToIdx(x, y):
    return y * BoardLength + x

def pidxToXy(idx):
    x = idx % BoardLengthP
    y = idx // BoardLengthP
    return x, y

def flipCol(col):
    if col == BLACK:
        return WHITE
    return BLACK


class Move:
    def __init__(self, str):
        self.color = self.getColor(str)
        # Actual index
        self.idx = int(self.processMove(str))
        # Padded index
        self.pIdx = int(self.paddedMoveIdx())

    def getColor(self, str):
        ch = str[0]
        if ch == 'B' or ch == 'b':
            return BLACK
        return WHITE

    def processMove(self, m):
        x = ord(m[2])
        y = ord(m[3])
        self.x = x - ord('a')
        self.y = y - ord('a')

        return moveToIdx(self.x, self.y)

    def paddedMoveIdx(self):
        self.pX = self.x + 1
        self.pY = self.y + 1
        return self.pY * BoardLengthP + self.pX

