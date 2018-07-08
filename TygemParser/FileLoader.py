import os

# Handles the loading of the TYGEM dataset files
# Once they've been extracted from their archives
class FileLoader():
    def __init__(self, kifuFolder, indexFolder):
        self.kifuFolder     = kifuFolder
        self.indexFolder    = indexFolder
        self.kifuList       = os.listdir(kifuFolder)
        self.indexList      = os.listdir(indexFolder)
        self.indexIdx       = 0
        self.kifuIdx        = 0
        self.loadNewFile    = False
        self.iLinesIdx      = 0
        self.kLinesIdx      = 0
        self.indexFile      = self.openFile(self.indexFolder, self.indexList, self.indexIdx) 
        self.kifuFile       = self.openFile(self.kifuFolder,  self.kifuList,  self.kifuIdx )
        self.indexLines     = self.indexFile.readlines()
        self.kifuLines      = self.kifuFile.readlines()

    def openFile(self, folder, fileList, fileIdx):
        return open(folder + '/' + fileList[fileIdx], "r", encoding="utf-8")

    # Load the file and make sure to properly align kifu
    # and index files when their indexes in the lists don't align
    def loadNextFile(self):
            year            = self.indexList[self.indexIdx][4:8]
            nextKifuYear    = self.kifuList[self.kifuIdx+1][0:4]
            self.kifuIdx    += 1
            self.kifuFile   = self.openFile(self.kifuFolder, self.kifuList, self.kifuIdx)
            self.kifuLines  = self.kifuFile.readlines()
            self.kLinesIdx  = 0
            
            if year != nextKifuYear:
                self.indexIdx   += 1
                self.indexFile  = self.openFile(self.indexFolder, self.indexList, self.indexIdx)
                self.indexLines = self.indexFile.readlines()
                self.iLinesIdx  = 0

    # Provide both the info about the next game
    # as well as the game lines themselves
    def next(self):
        if self.loadNewFile:
            self.loadNextFile()
            self.loadNewFile = False

        game = self.kifuLines[self.kLinesIdx]
        info = self.indexLines[self.iLinesIdx]

        self.kLinesIdx += 1
        self.iLinesIdx += 1

        if self.kLinesIdx >= len(self.kifuLines) \
        or self.iLinesIdx >= len(self.indexLines):
            self.loadNewFile = True

        # If the id's aren't the same game, we have a problem...
        t = game.split('\t')[0]
        r = info.split('\t')[0]
        assert t == r, "Mismatched Kifu/Index ID's!"

        return info, game


