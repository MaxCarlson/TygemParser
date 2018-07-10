import os
import time
import random
import numpy as np
from Board import Board
from Storage import Storage
from FileLoader import FileLoader
from ProgressBar import ProgressBar
from Move import Move, moveToIdx, flipCol
from Globals import EMPTY, BLACK, WHITE, OFF_BOARD

def processGame(storage, info, game, movesToWrite):

    # We'll convert the board array to 19x19 when we write it to the file
    # for now we'll just use the move index
    # TODO: add 1 tile edges to board to make it easier to compute things like libs
    board = Board()

    winner = info.split('\t')[8]
    moves  = game.split(';')[1:]

    assert(winner[0] == 'B' or winner[0] == 'W')
    whoWon = BLACK if winner[0] == 'B' else WHITE

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
            storage.asignBoard(board, m.idx, m.color, won)
            if all(i >= m for m in idxMovesToWrite):
                break
        
        
        board.makeMove(m, col)
        col = flipCol(col)
        i += 1
        del m

    return processedMoves

def curateTygem(kifuFolder, indexFolder, movesPerGame = 1, totalMoves = 1):
    
    movesPerFile = 10000
    outFolder = 'outData/'
    outfilename = outFolder + input("Enter output file name: ")

    storage = Storage(outfilename, movesPerFile)
    loader = FileLoader(kifuFolder, indexFolder)

    fileIndex = 0
    movesProcessed = 0

    startTime = time.time()
    bar = ProgressBar(totalMoves, width=60, fmt=ProgressBar.FULL)

    while movesProcessed < totalMoves:

        info, game = loader.next()
        mc = processGame(storage, info, game, movesPerGame)
        movesProcessed += mc
        bar(mc)

    storage.writeToFile()

    endTime = time.time()
    print('\nTotal time for ' + str(totalMoves) + ' moves: ', startTime-endTime)





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

