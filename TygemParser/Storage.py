import numpy as np
from Board import Board
from Move import Move, moveToIdx, flipCol
from Globals import BoardLength, BoardSize, BoardDepth, BoardLengthP, BoardSizeP
from Globals import EMPTY, BLACK, WHITE, OFF_BOARD

# Store gamestates + moves before we write them to disk
class Storage:
    
    yVarCount = 3
    maxMovePerFile = 10000

    def __init__(self, outfileName, maxMovesPerFile, previousStates):
        self.fileCount      = 0
        self.strgIdx        = 0
        self.SaveDepth      = previousStates
        self.outfileName    = outfileName
        self.maxMovePerFile = maxMovesPerFile
        self.storage, self.yStorage = self.zeroBoard()

    def zeroBoard(self):
        self.storage    = np.zeros((self.maxMovePerFile, self.SaveDepth, BoardLength, BoardLength), dtype=np.int8)
        self.yStorage   = np.zeros((self.maxMovePerFile, self.yVarCount), dtype=np.int)
        return self.storage, self.yStorage

    def asignBoard(self, board, idx, color, won):
        self.storage[self.strgIdx]  = board.combineStates(color)
        self.yStorage[self.strgIdx] = [idx, color, won] 
        self.strgIdx += 1
        if self.strgIdx >= self.maxMovePerFile:
            self.writeToFile()
            
    def nextFile(self):
        self.fileCount += 1

    def clear(self):
        self.strgIdx = 0
        self.zeroBoard()

    def writeToFile(self):
        
        self.nextFile() 
        yname = self.outfileName + 'l' + str(self.fileCount)
        name  = self.outfileName + 'f' + str(self.fileCount)

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
