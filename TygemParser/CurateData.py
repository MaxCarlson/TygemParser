import os
import random
import numpy as np
from Globals import BoardLength, BoardSize, BoardDepth, BoardLengthP, BoardSizeP
from Globals import EMPTY, BLACK, WHITE, OFF_BOARD

from Board import Board
from Move import Move, moveToIdx, flipCol

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

        # Shuffle the results so we don't have large 
        # chunks of the same game next to eachtoher
        state = np.random.get_state()
        np.random.shuffle(self.storage)
        np.random.set_state(state)
        np.random.shuffle(self.yStorage)

        np.save(name, self.storage)
        np.save(yname, self.yStorage)
        self.clear()

# We store and save the board as black/white
def writeMoveAndBoardToFile(storage, move, board, col, won):

    storage.asignBoard(board, move, won)    
    
    if storage.strgIdx >= storage.maxMovePerFile:
        storage.writeToFile()

    return



def processGame(storage, line):

    # We'll convert the board array to 19x19 when we write it to the file
    # for now we'll just use the move index
    # TODO: add 1 tile edges to board to make it easier to compute things like libs
    board = Board()

    semiCount = 0
    i = 0

    whoWon = 0

    # TODO: Igore handicap games!
    # Find the start of the game (Should later look at handicaps?)
    for ch in line:
        i += 1
        if semiCount < 2 and ch == ';':
            semiCount += 1
        elif semiCount > 1:
            break

        # Find who won the game
        if line[i] == 'R' and line[i+1] == 'E':
            if line[i+3] == 'B':
                whoWon = BLACK
            elif line[i+3] == 'W':
                whoWon = WHITE

    # Process game into moves and boards
    col = BLACK
    last = False
    while i < len(line):
        mv = line[i-1:i+5]

        # Skip all moves in a game after passes 
        # ( Since passes aren't a move in the model yet )
        # Pass seems to look like ...;W[];B[la]...
        # Only 1 in 1000 games in this dataset though so 
        # might need a differnet data set to train the network to pass reasonably well
        if mv[2] == ']':
        #    print(line)
            break

        m = Move(mv)

        # Determine whether the side
        # to move won or lost
        won = whoWon == col

        writeMoveAndBoardToFile(storage, m, board, col, won)
        board.makeMove(m, col)
        col = flipCol(col)
        i += 6

class FileLoader():
    def __init__(self, kifuFolder, indexFolder):
        self.kifuFolder = kifuFolder
        self.indexFolder = indexFolder
        self.kifuList = os.listdir(kifuFolder)
        self.indexList = os.listdir(indexFolder)
        self.fileIdx = 0
        self.fileKifuIdx = 0
        self.loadNewFile = True
        self.indexFile = ''
        self.kifuFile = ''

    def loadNextFile(self):
        if self.indexFile == '':
            self.indexFile = open(self.indexList[self.fileIdx])
            self.fileKifuIdx = 0
        else:
            year = self.indexList[self.fileIdx][0:4]
            nextKifuYear = self.kifuList[self.fileKifuIdx+1][0:4]
            self.fileKifuIdx += 1
            self.kifuFile = open(self.kifuList[self.fileKifuIdx])

            if year != nextKifuYear:
                self.fileIdx += 1
                self.indexFile = open(self.indexList[self.fileIdx])

    
    def next(self):
        if self.loadNewFile:
            self.loadNextFile()
            self.loadNewFile = False



def curateTygem(kifuFolder, indexFolder, movesPerGame = 1, totalMoves = 1):
    
    movesPerFile = 10000
    outFolder = 'outData/'
    outfilename = outFolder + input("Enter output file name: ")

    kifuList = os.listdir(kifuFolder)
    indexList = os.listdir(indexFolder)

    storage = Storage(outfilename, movesPerFile)
    loader = FileLoader(kifuFolder, indexFolder)

    stop = False
    fileIndex = 0
    movesProcessed = 0
    
    while movesProcessed < totalMoves and stop == False:

        game = loader.next()

        if stop:
            storage.writeToFile()



# Current format of output 
#
# Numpy Feature array:
# [MaxMovesPerFile, BoardLayers, BoardLength, BoardLength]
#
# state = Board state before move 
# BoardLayers = [state, state - 1, state - 2]
#
# Numpy Label array:
# [MoveIndex, color]
# MoveIndex = my * BoardLength + mx
#
# This is similar to, but different, from the
# format that is fed to the model. That format is:
#
# [MovesPerBatch, BoardLayers * 2 + 1, BoardLength, BoardLength]
# BoardLayers = [BinaryColorLayer, Binary1stStateBlack, Binary1stStateWhite, ..., BinaryNthStateWhite]
#
# BinaryColorLayer = all 1's for black all 0's for white
# BinaryNthStateColor = a binary layer with only color stones or not color stones (ones where stones
# of that color are, 0's everywhere else)
#
#
# Misc
# Data is randomized when written to disk,
# but only within the bounds of the movesPerFile
def curateData():

    movesPerFile = 10000
    outFolder = 'outData/' 
    outfilename = outFolder + input("Enter output file name: ")
    count = int(input("Enter number of games to write to disk: "))

    filename = outFolder + 'pro2000+.txt'
    file = open(filename)

    
    storage = Storage(outfilename, movesPerFile)
   
    for i in range(count):

        line = file.readline()

        processGame(line, storage)

        if i >= count - 1:
            storage.writeToFile()



