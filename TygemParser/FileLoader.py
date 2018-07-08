import os

class FileLoader():
    def __init__(self, kifuFolder, indexFolder):
        self.kifuFolder = kifuFolder
        self.indexFolder = indexFolder
        self.kifuList = os.listdir(kifuFolder)
        self.indexList = os.listdir(indexFolder)
        self.indexIdx = 0
        self.kifuIdx = 0
        self.loadNewFile = True
        self.indexFile = ''
        self.kifuFile = ''
        self.iLinesIdx = 0
        self.kLinesIdx = 0
        self.indexLines = ''
        self.kifuLines = ''

    def openFile(self, folder, fileList, fileIdx):
        return open(folder + '/' + fileList[fileIdx], "r", encoding="utf-8")

    def loadNextFile(self):
        if self.indexFile == '':
            self.indexFile = self.openFile(self.indexFolder, self.indexList, self.indexIdx) 
            self.indexLines = self.indexFile.readlines()
            self.iLinesIdx = 0
            self.kifuFile = self.openFile(self.kifuFolder, self.kifuList, self.kifuIdx)
            self.kifuLines = self.kifuFile.readlines()
            self.kLinesIdx = 0
        else:
            year = self.indexList[self.indexIdx][0:4]
            nextKifuYear = self.kifuList[self.kifuIdx+1][0:4]
            self.kifuIdx += 1
            self.kifuFile = self.openFile(self.kifuFolder, self.kifuList, self.kifuIdx)
            self.kifuLines = self.kifuFile.readlines()
            self.kLinesIdx = 0
            
            if year != nextKifuYear:
                self.indexIdx += 1
                self.indexFile = self.openFile(self.indexFolder, self.indexList, self.indexIdx)
                self.indexLines = self.indexFile.readlines()
                self.iLinesIdx = 0

    def next(self):
        if self.loadNewFile:
            self.loadNextFile()
            self.loadNewFile = False

        game = self.kifuLines[self.kLinesIdx]
        suffix = self.indexLines[self.iLinesIdx]

        self.kLinesIdx += 1
        self.iLinesIdx += 1

        if self.kLinesIdx >= len(self.kifuLines) \
        or self.iLinesIdx >= len(self.indexLines):
            self.loadNewFile = True

        # If the id's aren't the same game, we have a problem...
        t = game.split('\t')[0]
        r = suffix.split('\t')[0]
        assert(t == r)

        return suffix, game


