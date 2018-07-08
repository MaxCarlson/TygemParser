from CurateData import curateTygem


kifuFolder = 'Kifu' #input('Kifu Folder?') # Commented out for fast testing
indexFolder = 'index' #input('Index Folder?')
movesPerGame = int(input('Moves per game? '))
totalMoves = int(input('Total moves to process? '))

curateTygem(kifuFolder, indexFolder, movesPerGame, totalMoves)
