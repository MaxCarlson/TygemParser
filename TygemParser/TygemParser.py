from CurateData import curateTygem

# TODO: Command line args
kifuFolder = input('Kifu Folder: ')
indexFolder = input('Index Folder: ')
previousStates = int(input('Previous board states: '))
movesPerGame = int(input('Moves per game: '))
totalMoves = int(input('Total moves to process: '))


curateTygem(kifuFolder, indexFolder, movesPerGame, totalMoves, previousStates)
