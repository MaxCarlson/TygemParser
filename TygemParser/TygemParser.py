from CurateData import curateTygem


kifuFolder = input('Kifu Folder?')
indexFolder = input('Index Folder?')
movesPerGame = int(input('Moves per game?'))

curateTygem(kifuFolder, indexFolder, movesPerGame)
