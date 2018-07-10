import numpy as np
from Board import Board
from Move import Move, moveToIdx, flipCol
from Globals import BoardLength, BoardSize, BoardDepth, BoardLengthP, BoardSizeP
from Globals import EMPTY, BLACK, WHITE, OFF_BOARD


# Store gamestates + moves before we write them to disk
class Storage:
    fileCount = 0
    strgIdx = 0
    # Number of planes of the feature map that are written to disk
    SaveDepth = (BoardDepth - 1) // 2
    maxMovePerFile = 10000

    def __init__(self, outfileName, maxMovesPerFile):
        self.outfileName = outfileName
        self.maxMovePerFile = maxMovesPerFile
        self.storage, self.yStorage = self.zeroBoard()

    def zeroBoard(self):
        self.storage = np.zeros((self.maxMovePerFile, self.SaveDepth, BoardLength, BoardLength), dtype=np.int8)
        self.yStorage = np.zeros((self.maxMovePerFile, 3), dtype=int)
        return self.storage, self.yStorage

    def asignBoard(self, board, move, won):
        self.storage[self.strgIdx] = board.combineStates(move.color)
        self.yStorage[self.strgIdx] = [move.idx, move.color, won] 
        self.strgIdx += 1

    def nextFile(self):
        self.fileCount += 1

    def clear(self):
        self.strgIdx = 0
        self.zeroBoard()

    def writeToFile(self):
        
        self.nextFile() 
        yname = self.outfileName + 'l' + str(self.fileCount)
        name = self.outfileName  + 'f' + str(self.fileCount)

        if self.strgIdx < self.maxMovePerFile:
            self.storage = self.storage[0:self.strgIdx]
            self.yStorage = self.yStorage[0:self.strgIdx]

        # Shuffle the results so we don't have
        # moves from the same game next to eachother
        # Only really needed for movesPerGame > 1
        state = np.random.get_state()
        np.random.shuffle(self.storage)
        np.random.set_state(state)
        np.random.shuffle(self.yStorage)

        np.save(name, self.storage)
        np.save(yname, self.yStorage)
        self.clear()
