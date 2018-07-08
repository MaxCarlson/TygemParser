from CurateData import curateTygem


kifuFolder = input('Kifu Folder: ')
indexFolder = input('Index Folder: ')
movesPerGame = int(input('Moves per game: '))
totalMoves = int(input('Total moves to process: '))

curateTygem(kifuFolder, indexFolder, movesPerGame, totalMoves)
