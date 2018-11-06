############################################################
# CMPSC442: Homework 4
############################################################

student_name = "Tomoki Takasawa"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.
import collections
from copy import deepcopy
import itertools
import Queue
#from Queue import PriorityQueue
try:
    set
except NameError:
    from sets import Set as set


############################################################
# Section 1: Sudoku
############################################################


class StateTracker(object):
    def __init__(self):
        self.counter = 0
        self.state = 0

    def increment(self):
        self.counter += 1

    def getCounter(self):
        return self.counter

    def setState(self):
        self.state = self.counter
        self.counter = 0

    def reset(self):
        self.state = 0
        self.counter = 0

    def checkState(self, counter):
        return self.state == counter

    def __repr__(self):
        return "<__main__.State: counter = " + str(self.counter) +  ">"

def sudoku_cells():
    cellList = []
    for i in range(9):
        for j in range(9):
            cellList.append((i, j))

    return cellList


def sudoku_arcs():
    arcs = []
    for i in range(9):
        for j in range(9):
            for k in range(9):
                for l in range(9):
                    if i == k and j == l:
                        pass
                    elif (i == k) or (j == l) or ((i//3 == k//3) and (j//3 == l//3)):
                        arcs.append(((i, j), (k, l)))
    return arcs



def read_board(path):
    file = open(path, 'r')
    return file.read()

class Sudoku(object):

    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()
    defaultAvailables = [1,2,3,4,5,6,7,8,9]

    def __init__(self, board):

        oneDimensionalBoard = []
        twoDimensionalBoard = []
        for i in range(len(board)):
            if board[i] == '\n':
                twoDimensionalBoard.append(oneDimensionalBoard)
                oneDimensionalBoard = []
            else:
                if board[i] == '*':
                    oneDimensionalBoard.append(0)
                else:
                    try:
                        oneDimensionalBoard.append(int(board[i]))
                    except ValueError:
                        pass
        twoDimensionalBoard.append(oneDimensionalBoard)

        self.board = twoDimensionalBoard
        self.availableDicts = {}
        self.state = StateTracker()
                

    def getBoard(self):
        return self.board

    def get_values(self, cell):

        if cell in self.availableDicts:
            return self.availableDicts[cell]
        else:
            self.availableDicts[cell] = set(self.defaultAvailables) if self.board[cell[0]][cell[1]] == 0 else set([self.board[cell[0]][cell[1]]])
            return self.availableDicts[cell]

    def setValues(self):
        for i in range(9):
            for j in range(9):
                self.board[i][j] = str(self.availableDicts[(i, j)].pop())

    def remove_inconsistent_values(self, cell1, cell2):

        availables = self.get_values(cell1)
        eliminatable = self.get_values(cell2)

        if len(eliminatable) != 1:
            return False

        if len(availables) > 1:
            eliminatable = list(eliminatable)[0]

            if eliminatable in availables:

                availables.remove(eliminatable)
                self.availableDicts[cell1] = availables
                return True

        return False


    def copy(self):
        return deepcopy(self)

    def infer_ac3(self, flag = True):
        queue = []

        for item in self.ARCS:
            queue.append(item)

        while queue != []:
            nextState = queue.pop(0)
            if self.remove_inconsistent_values(nextState[0], nextState[1]):
                if len(self.ARCS) == 0:
                    return False
                for reminder in self.ARCS:
                    if (reminder[1] == nextState[0]):
                        queue.append(reminder)

        if flag:
            self.setValues()

        return True

    def examineARC(self, cellLocation, val):

        examinations = iter([
            self.examineRowCol(cellLocation, val, True), 
            self.examineRowCol(cellLocation, val, False), 
            self.examineBlock(cellLocation, val)
        ])

        for item in examinations:
            if not item:
                return True
            
        return False

    def examineBlock(self, cellLocation, val):
        for location in self.getAllCellInBlock(cellLocation):
            if val in self.get_values(location):
                return True
        return False


    def getAllCellInBlock(self, cellLocation):
        for i in range(9):
            for j in range(9):
                if i == cellLocation[0] and j == cellLocation[1]:
                    continue
                elif (i // 3 == cellLocation[0] // 3) and (j // 3 == cellLocation[1] // 3):
                    yield(i, j)

    def examineRowCol(self, cellLocation, val, isRow):
        for i in range(9):
            if isRow:
                location = (cellLocation[0], i)
            else:
                location = (i, cellLocation[1])

            if location == cellLocation:
                continue
            elif val in self.get_values(location):
                return True

        return False

    def infer_improved_helper(self, flag):

        self.infer_ac3(False)

        for cell in self.CELLS:

            cellOptions = self.get_values(cell)
            cellOptionLength = len(cellOptions) 

            if (cellOptionLength < 1):
                return
            elif (cellOptionLength > 1):
                self.state.increment()
                
                for vals in cellOptions:
                    if self.examineARC(cell, vals):
                        self.availableDicts[cell] = [vals]
                        break

        if self.state.checkState(self.state.getCounter()) or self.state.getCounter() == 0:
            if self.state.getCounter() == 0 and flag:
                self.setValues()
            self.state.reset()
            return
        else:
            self.state.setState()
            self.infer_improved()

    def infer_improved(self):
        self.infer_improved_helper(True)


    def checkBoardValue(self):
        oneCol = ''
        for i in range(9):
            for j in range(9):
                cell = str(self.board[i][j])
                if len(list(cell)) > 1:
                    print('not solved')
                    break
                oneCol += cell
            print(oneCol)
            oneCol = ''

    def printAllValue(self):
        for i in range(9):
            for j in range(9):
                print('At ' + str((i, j)) + " : " + str(self.board[i][j]))


    def checkBoard(self):
        for points in self.CELLS:
            if len(self.get_values(points)) > 1:
                return False

        for arcs in self.ARCS:
            cell = arcs[0]
            for arc_points in self.ARCS:
                if arcs[0] == arc_points[0] and self.get_values(arc_points[1]) == self.get_values(arcs[0]):
                    return False
        return True

    def copy(self):
        return deepcopy(self)

    def backTrack(self, currentState):

        if currentState.checkBoard():
            return True

        currentState.infer_improved_helper(False)

        for cells in currentState.CELLS:
            cellOptions = currentState.get_values(cells)
            cellOptionLength = len(cellOptions) 

            if cellOptionLength < 1:
                return False
            
            if cellOptionLength > 1:
                nextState = self.copy()

                for options in cellOptions:
                    
                    nextState.availableDicts[cells] = [options]
                    nextState.infer_improved_helper(False)
                    if nextState.checkBoard():
                        if self.backTrack(nextState):
                            self.availableDicts = nextState.availableDicts
                            return True
                    else:
                        break

                    
        return False

    def infer_with_guessing(self):
        self.backTrack(self)
        self.setValues()


############################################################
# Section 2: Feedback
############################################################

feedback_question_1 = """
24 hours or so
"""

feedback_question_2 = """
infer_improved was difficult
"""

feedback_question_3 = """
This time, it was actual game I know that we solved.
"""
