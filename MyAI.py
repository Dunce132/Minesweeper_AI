# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
from collections import defaultdict
import itertools


class MyAI( AI ):

    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################
        self.row = colDimension
        self.col = rowDimension
        self.totalMines = totalMines
        self.prevX = startX
        self.prevY = startY
        self.board = [['.']*self.col for i in range(self.row)]
        # self.board = [['.']*self.row for i in range(self.col)]
        # self.board = [["." for j in range(colDimension)] for i in range(rowDimension)]

        self.coveredUnmarked = self.row * self.col - 1
        self.numBombsonBoard = 0
        self.uncoveredTups = set()
        self.uncoveredTups.add((startX,startY))
        self.queue = []
        self.currentX = startX 
        self.currentY = startY
        #self.board[self.currentX][self.currentY] = 0
        self.turn = -1
        self.nothingHappens = 0
        self.prevSize = 0
        self.potentialMine = set()
        self.bruteForce = False
        self.V = list()
        self.C = list()
        self.threshold = 0 
        self.prevUncoveredTups = 0
        # 0 represents uncovered tile
        # 1 represents covered + marked tile
        # 2 represents covered + unmarked tile
        # we start off as everything being covered + unmarked
        ########################################################################
        #							YOUR CODE ENDS							   #
        ########################################################################
    
    def flag(self, x, y):
        self.board[x][y] = 'B'
        self.numBombsonBoard += 1

    def getCoveredNeighbors(self, x, y):
        adjacency = [-1, 0, 1]
        count = []
        for i in adjacency:
            for j in adjacency:
                if (x + i) >= 0 and (x + i) < self.row:
                    if (y + j) >= 0 and (y + j) < self.col:
                        if self.board[x + i][y + j] == '.':
                            count.append((x + i, y + j))
        return count

    def UoM(self, x, y):
        adjacency = [-1, 0, 1]
        existingTiles = list()
        for i in adjacency:
            for j in adjacency:
                if (x + i) >= 0 and (x + i) < self.row:
                    if (y + j) >= 0 and (y + j) < self.col:
                        if self.board[x + i][y + j] == 'B' or isinstance(self.board[x + i][y + j], int):
                            existingTiles.append((x, y))
        return existingTiles

    def markedNeighbor(self, x, y):
        adjacency = [-1, 0, 1]
        existingTiles = list()
        for i in adjacency:
            for j in adjacency:
                if (x + i) >= 0 and (x + i) < self.row:
                    if (y + j) >= 0 and (y + j) < self.col:
                        if self.board[x + i][y + j] == 'B':
                            existingTiles.append((x, y))
        return existingTiles

    def effectiveLabel(self, x, y):
        return self.board[x][y] - len(self.markedNeighbor(x, y))

    def backtracking(self):
        index = 0
        while index < len(self.C):
            c = self.C[index]
            cNeighbor = self.getCoveredNeighbors(c[0], c[1])
            if len(cNeighbor) == self.effectiveLabel(c[0], c[1]):
                if len(cNeighbor) > 0:
                    for i in cNeighbor:
                        self.flag(i[0], i[1])
                    index = 0
                    continue
            index += 1

    def hasUncovered(self, x, y):
        adjacency = [-1, 0, 1]
        count = 0
        for i in adjacency:
            for j in adjacency:
                if (x + i) >= 0 and (x + i) < self.row:
                    if (y + j) >= 0 and (y + j) < self.col:
                        if isinstance(self.board[x+i][y+j], int):
                            count += 1
        return count > 0

    def scanAll(self):
        self.C = list()
        self.V = list()
        for x in range(self.row):
            for y in range(self.col):
                if isinstance(self.board[x][y], int):
                    if self.effectiveLabel(x, y) > 0:
                        if len(self.getCoveredNeighbors(x, y)) == self.effectiveLabel(x, y):
                          for i in self.getCoveredNeighbors(x, y):
                            self.flag(i[0], i[1])
                        else:
                            self.C.append((x, y))
                    elif self.effectiveLabel(x, y) == 0:
                        self.enqueue(x, y)
                elif self.board[x][y] == '.':
                    if self.hasUncovered(x, y):
                        self.V.append((x, y))

    def enqueue(self, x, y):
        adjacency = [-1, 0, 1]
        for i in adjacency:
            for j in adjacency:
                if (x + i) >= 0 and (x + i) < self.row:
                    if (y + j) >= 0 and (y + j) < self.col:
                            if (self.board[x + i][y + j] == '.'):
                                if not (x,y) in self.queue:
                                    self.queue.append((x + i, y + j))

    def print_board(self):
        index = 0
        test = '  '
        for i in reversed(self.board):
            print(i)
        for i in range(self.col):
            test += (str(i) + '   ')
        print(test)

    def calculate_probabilities(self):
        # stores combinations for each tile in C
        cdict = {}

        for c in self.C:
            vNeighbors = [v for v in self.getVNeighbors(c) if v in self.V]
            cdict[c] = list(itertools.combinations(vNeighbors, self.effectiveLabel(c[0], c[1])))

        # stores the count of how often each tile is included in the combinations
        countDict = defaultdict(int)

        for combinations in cdict.values():
            for combo in combinations:
                for coord in combo:
                    countDict[coord] += 1

        # calculate the total number of combinations generated
        total_combinations = sum(len(combos) for combos in cdict.values())

        # stores the probability of each tile being a mine
        probabilityDict = {}

        for coord, count in countDict.items():
            probabilityDict[coord] = count / total_combinations if total_combinations > 0 else 0

        min_probability = min(probabilityDict,key=probabilityDict.get)
        
        self.queue.append(min_probability)

    def getVNeighbors(self, c):
        x, y = c
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.row and 0 <= ny < self.col and (nx, ny) in self.V:
                    neighbors.append((nx, ny))
        return neighbors

    def bruteForceLastTile(self):
        self.queue = list()
        for x in range(self.row):
            for y in range(self.col):
                if self.board[x][y] == '.':
                    self.queue.append((x, y))
    
    def getAction(self, number: int) -> "Action Object":

        # self.print_board()
        self.board[self.prevX][self.prevY] = number

        #check Win Condition
        if len(self.uncoveredTups) == ((self.row * self.col) - self.totalMines):
            return Action(AI.Action.LEAVE)

        # simple 
        if self.numBombsonBoard == self.totalMines or self.numBombsonBoard == self.totalMines-1:
            self.bruteForceLastTile()

        if self.effectiveLabel(self.prevX, self.prevY) == len(self.getCoveredNeighbors(self.prevX, self.prevY)):
            toFlag = self.getCoveredNeighbors(self.prevX, self.prevY)
            for i in toFlag:
                self.flag(i[0], i[1])
        if self.effectiveLabel(self.prevX, self.prevY) == 0:
            self.enqueue(self.prevX, self.prevY)

        # advance logic
        self.scanAll()
        self.backtracking()

        if len(self.queue) == 0:
            self.scanAll()
            if len(self.queue) == 0:
                self.calculate_probabilities()
                
        nextCoord = self.queue.pop()

        while nextCoord in self.uncoveredTups and len(self.queue) > 0:
            nextCoord = self.queue.pop()

        if self.prevUncoveredTups == len(self.uncoveredTups):
            self.threshold += 1
        else:
            self.threshold = 0
        
        if self.threshold == 5:
            self.queue = list()
            self.calculate_probabilities()

        self.prevX, self.prevY = nextCoord

        self.prevUncoveredTups = len(self.uncoveredTups)
        self.uncoveredTups.add(nextCoord)

        # self.print_board()
        
        return Action(AI.Action.UNCOVER, self.prevX, self.prevY)

