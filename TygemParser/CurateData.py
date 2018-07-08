import os
import time
import random
import numpy as np
from FileLoader import FileLoader
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

# We store and save the board as black/white
def writeMoveAndBoardToFile(storage, move, board, col, won):

    storage.asignBoard(board, move, won)    
    
    if storage.strgIdx >= storage.maxMovePerFile:
        storage.writeToFile()

    return

def processGame(storage, info, game, movesToWrite):

    # We'll convert the board array to 19x19 when we write it to the file
    # for now we'll just use the move index
    # TODO: add 1 tile edges to board to make it easier to compute things like libs
    board = Board()

    semiCount = 0
    i = 0

    winner = info.split('\t')[8]

    assert(winner[0] == 'B' or winner[0] == 'W')
    whoWon = BLACK if winner[0] == 'B' else WHITE

    moves = game.split(';')[1:]

    idxMovesToWrite = []

    for i in range(movesToWrite):
        roll = random.randint(0, len(moves))
        if roll in idxMovesToWrite:
            i -= 1
            continue
        idxMovesToWrite.append(roll)

    # Process game into moves and boards
    i = 0
    col = BLACK
    last = False
    processedMoves = 0
    for mv in moves:
        # Skip all moves in a game after passes 
        # ( Since passes aren't a move in the model yet )
        # Pass seems to look like ...;W[];B[la]...
        # Only 1 in 1000 games in this dataset though so 
        # might need a differnet data set to train the network to pass reasonably well
        if mv[2] == ']':
        #    print(game)
            break

        m = Move(mv)

        # Determine whether the side
        # to move won or lost
        won = whoWon == col

        # If it's one of the randomly chosen moves, write it to disk
        # If it's the last move, we can stop writting this game
        if i in idxMovesToWrite:
            processedMoves += 1
            writeMoveAndBoardToFile(storage, m, board, col, won)
            if all(i >= m for m in idxMovesToWrite):
                break
        
        
        board.makeMove(m, col)
        col = flipCol(col)
        i += 1

    return processedMoves

from ProgressBar import ProgressBar

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

    t0 = time.time()
    
    bar = ProgressBar(totalMoves, width=60, fmt=ProgressBar.FULL)

    while movesProcessed < totalMoves and stop == False:

        info, game = loader.next()
        mc = processGame(storage, info, game, movesPerGame)
        movesProcessed += mc
        bar(mc)

    storage.writeToFile()

    t1 = time.time()
    print('Total time for ' + str(totalMoves) + ' moves: ', t1-t0)





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

