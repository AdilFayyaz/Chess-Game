# The chessboard drawing using pygame was inspired from this youtube tutorial:
# https://www.youtube.com/watch?v=EnYui0e73Rs. However, only the use of pygame
# for drawing was consulted from here, all other implementation was done by ourselves

import copy
import math
import random

import pygame
import simpleaudio as sa
import sys

userColor = "black"
allowIllegalMoves=False
whiteKingDanger = False
blackKingDanger = False
length = 8
colToChar = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
scores = {"Queen": 9, "Rook": 5, "Bishop": 3, "Knight": 3, "Pawn": 1, "King": 1000}


class possibleMove:
    def __init__(self, piece, target, source, isCastling=False, target2=None, source2=None):
        self.piece = getPieceName(piece)
        self.target = target
        self.source = source
        self.pieceNum = piece
        self.castling = isCastling
        self.target2 = target2
        self.source2 = source2


# Class to display the state of the chess board
class ChessBoardState:
    possibleSquares = []

    def __init__(self):
        self.board = [
            ['r1', 'h1', 'b1', 'q1', 'k1', 'b1', 'h1', 'r1'],
            ['p1', 'p1', 'p1', 'p1', 'p1', 'p1', 'p1', 'p1'],
            ['*', '*', '*', '*', '*', '*', '*', '*', ],
            ['*', '*', '*', '*', '*', '*', '*', '*', ],
            ['*', '*', '*', '*', '*', '*', '*', '*', ],
            ['*', '*', '*', '*', '*', '*', '*', '*', ],
            ['p2', 'p2', 'p2', 'p2', 'p2', 'p2', 'p2', 'p2'],
            ['r2', 'h2', 'b2', 'q2', 'k2', 'b2', 'h2', 'r2'],
        ]

    def display(self):
        print('\n'.join(map(' '.join, self.board)))

    # target, source, target2, source2
    def action(self, chesspieceaction, player):
        global whiteKingDanger
        global blackKingDanger
        currentColour = player.color
        if len(chesspieceaction.itemDisplaced) > 1:
            if (player.color == "black" and chesspieceaction.itemDisplaced[1] == '1') or (
                    player.color == "white" and chesspieceaction.itemDisplaced[
                1] == '2'):  # if the correct chess piece is being moved

                if (currentColour == "black" and (
                        len(chesspieceaction.itemTargeted) > 1 and chesspieceaction.itemTargeted[
                    1] != '1') or chesspieceaction.itemTargeted == '*') or (
                        currentColour == "white" and (
                        len(chesspieceaction.itemTargeted) > 1 and chesspieceaction.itemTargeted[
                    1] != '2') or chesspieceaction.itemTargeted == '*') or (
                        (chesspieceaction.targetR, chesspieceaction.targetC) in self.getLegalMoves(player,
                                                                                                   chesspieceaction)):  # if the opponent chess piece is being targeted or moving to an empty location
                    if self.legalMove(chesspieceaction, player, self):
                        allMoves = player.getMobility(self)
                        for moves in allMoves:
                            if moves.castling == True:
                                if moves.target == (
                                chesspieceaction.targetR, chesspieceaction.targetC):  # king has been moved in castling
                                    self.board[moves.target2[0]][moves.target2[1]] = self.board[moves.source2[0]][
                                        moves.source2[1]]
                                    self.board[moves.source2[0]][moves.source2[1]] = '*'
                                    player.castling = False
                                # elif moves.target2==(chesspieceaction.targetR, chesspieceaction.targetC) : #rook has been moved in castling

                        self.board[chesspieceaction.sourceR][chesspieceaction.sourceC] = '*'
                        self.board[chesspieceaction.targetR][chesspieceaction.targetC] = chesspieceaction.itemDisplaced
                        player.changeTurn()
                        return 1
                    else:
                        # print("Illegal Move")
                        return -1
                else:
                    # print("Cant kill yourself")
                    return -1
            else:
                # print("Moving wrong piece")
                return -1
        else:
            # print("Select a player!")
            return -1

    def getWinner(self, player1, player2):
        if player1.updateKingLocation(self) == -1 or player1.checkMate(self):
            return player2
        elif player2.updateKingLocation(self) == -1 or player2.checkMate(self):
            return player1
        else:
            return -1

    def moveBlackPawn(self, chesspieceaction):
        if chesspieceaction.sourceR == 1:  # first move by black pawn
            if 0 < chesspieceaction.targetR - chesspieceaction.sourceR <= 2 and chesspieceaction.itemTargeted == '*' and chesspieceaction.targetC == chesspieceaction.sourceC and \
                    self.board[chesspieceaction.sourceR + 1][chesspieceaction.sourceC] == '*':
                return True
            elif (chesspieceaction.targetR - chesspieceaction.sourceR == 1 and abs(
                    chesspieceaction.targetC - chesspieceaction.sourceC) == 1 and chesspieceaction.itemTargeted != '*'):
                return True
            else:
                return False
        else:  # subsequent moves
            if (
                    chesspieceaction.targetR - chesspieceaction.sourceR == 1) and chesspieceaction.itemTargeted == '*' and chesspieceaction.targetC == chesspieceaction.sourceC:
                return True
            elif (chesspieceaction.targetR - chesspieceaction.sourceR == 1 and abs(
                    chesspieceaction.targetC - chesspieceaction.sourceC) == 1 and chesspieceaction.itemTargeted != '*'):
                return True
            else:
                return False

    def moveWhitePawn(self, chesspieceaction):
        if chesspieceaction.sourceR == 6:  # first move by white pawn
            if 0 > chesspieceaction.targetR - chesspieceaction.sourceR >= -2 and chesspieceaction.itemTargeted == '*' and chesspieceaction.targetC == chesspieceaction.sourceC and \
                    self.board[chesspieceaction.sourceR - 1][chesspieceaction.sourceC] == '*':
                return True
            elif (chesspieceaction.targetR - chesspieceaction.sourceR == -1 and abs(
                    chesspieceaction.targetC - chesspieceaction.sourceC) == 1 and chesspieceaction.itemTargeted != '*'):
                return True
            else:
                return False
        else:  # subsequent moves
            if (
                    chesspieceaction.targetR - chesspieceaction.sourceR == -1) and chesspieceaction.itemTargeted == '*' and chesspieceaction.targetC == chesspieceaction.sourceC:
                return True
            elif (chesspieceaction.targetR - chesspieceaction.sourceR == -1 and abs(
                    chesspieceaction.targetC - chesspieceaction.sourceC) == 1 and chesspieceaction.itemTargeted != '*'):
                return True
            else:
                return False

    def moveUpDown(self, chesspieceaction, color):
        # Allowed to move if place is empty
        # Unless blocked by another piece of the same color

        # If not in the same column - movement in row
        if chesspieceaction.sourceC != chesspieceaction.targetC:
            # If moving from left to right
            if chesspieceaction.sourceC < chesspieceaction.targetC:
                for i in range(chesspieceaction.sourceC + 1, chesspieceaction.targetC):
                    if self.board[chesspieceaction.sourceR][i] != "*":
                        # If color of current player matches the target piece color return False
                        if color == "white" and chesspieceaction.itemTargeted.find('2'):
                            return False
                        elif color == 'black' and chesspieceaction.itemTargeted.find('1'):
                            return False
                return True
            # Moving from right to left
            else:
                for i in range(chesspieceaction.targetC, chesspieceaction.sourceC, -1):
                    if self.board[chesspieceaction.sourceR][i] != "*":
                        # If color of current player matches the target piece color return False
                        if color == "white" and chesspieceaction.itemTargeted.find('2'):
                            return False
                        elif color == 'black' and chesspieceaction.itemTargeted.find('1'):
                            return False
                return True
        elif chesspieceaction.sourceR != chesspieceaction.targetR:
            # If moving from up to down
            if chesspieceaction.sourceR < chesspieceaction.targetR:
                for i in range(chesspieceaction.sourceR + 1, chesspieceaction.targetR):
                    if self.board[i][chesspieceaction.sourceC] != '*':
                        # If color of current player matches the target piece color return False
                        if color == "white" and chesspieceaction.itemTargeted.find('2'):
                            return False
                        elif color == 'black' and chesspieceaction.itemTargeted.find('1'):
                            return False
                return True
            # If moving from down to up
            else:
                for i in range(chesspieceaction.targetR, chesspieceaction.sourceR, -1):
                    if self.board[i][chesspieceaction.sourceC] != '*':
                        # If color of current player matches the target piece color return False
                        if color == "white" and chesspieceaction.itemTargeted.find('2'):
                            return False
                        elif color == 'black' and chesspieceaction.itemTargeted.find('1'):
                            return False
                return True

    def moveRook(self, chesspieceaction, color):
        # Movement in the same row or col allowed only
        if chesspieceaction.targetR == chesspieceaction.sourceR or chesspieceaction.targetC == chesspieceaction.sourceC:
            return self.moveUpDown(chesspieceaction, color)
        return False

    def upDiagonalLR(self, chesspieceaction, color):
        rows = chesspieceaction.sourceR
        cols = chesspieceaction.sourceC
        # print("&&&&")
        # print(rows, cols)
        # print("&&&&")
        while rows > 0 and cols > 0:
            if self.board[rows - 1][cols - 1] != "*":
                # and (
                # rows != chesspieceaction.sourceR and cols != chesspieceaction.sourceC):
                # print("out here: " + self.board[rows - 1][cols - 1])
                # print(rows, cols)
                # print(chesspieceaction.targetR, chesspieceaction.targetC)
                if rows - 1 > chesspieceaction.targetR and cols - 1 > chesspieceaction.targetC:
                    # if abs(chesspieceaction.targetR - (rows - 1)) == 1 and abs((cols - 1) - chesspieceaction.targetC) == 1:
                    # print("in here")
                    if color == "white" and chesspieceaction.itemTargeted.find('2'):
                        return False
                    elif color == 'black' and chesspieceaction.itemTargeted.find('1'):
                        return False
            rows -= 1
            cols -= 1
        return True

    def downDiagonalLR(self, chesspieceaction, color):
        rows = chesspieceaction.sourceR
        cols = chesspieceaction.sourceC
        while rows < length - 1 and cols < length - 1:
            if self.board[rows + 1][cols + 1] != "*":
                # and (
                # rows != chesspieceaction.sourceR and cols != chesspieceaction.sourceC):
                if rows + 1 < chesspieceaction.targetR and cols + 1 < chesspieceaction.targetC:
                    if color == "white" and chesspieceaction.itemTargeted.find('2'):
                        return False
                    elif color == 'black' and chesspieceaction.itemTargeted.find('1'):
                        return False
            rows += 1
            cols += 1
        return True

    def upDiagonalRL(self, chesspieceaction, color):
        rows = chesspieceaction.sourceR
        cols = chesspieceaction.sourceC
        while rows > 0 and cols < length - 1:
            if self.board[rows - 1][cols + 1] != "*":
                # and (
                #     rows != chesspieceaction.sourceR and cols != chesspieceaction.sourceC):
                # print(rows-1, cols +1)
                # print(chesspieceaction.targetR, chesspieceaction.targetC)
                if rows - 1 > chesspieceaction.targetR and cols + 1 < chesspieceaction.targetC:
                    if color == "white" and chesspieceaction.itemTargeted.find('2'):
                        return False
                    elif color == 'black' and chesspieceaction.itemTargeted.find('1'):
                        return False
            rows -= 1
            cols += 1
        return True

    def downDiagonalRL(self, chesspieceaction, color):
        rows = chesspieceaction.sourceR
        cols = chesspieceaction.sourceC
        while rows < length - 1 and cols > 0:
            if self.board[rows + 1][cols - 1] != "*":
                # and (
                #     rows != chesspieceaction.sourceR and cols != chesspieceaction.sourceC):
                if rows + 1 < chesspieceaction.targetR and cols - 1 > chesspieceaction.targetC:
                    if color == "white" and chesspieceaction.itemTargeted.find('2'):
                        return False
                    elif color == 'black' and chesspieceaction.itemTargeted.find('1'):
                        return False
            rows += 1
            cols -= 1
        return True

    def moveBishop(self, chesspieceaction, color):
        # If move on the left to right diagonal (up or below the main diagonal) Up the diagonal values should be less, down
        # the diagonal values should be greater

        difference_row = abs(chesspieceaction.targetR - chesspieceaction.sourceR)
        difference_col = abs(chesspieceaction.targetC - chesspieceaction.sourceC)
        # print("diff row: ", difference_row)
        # print("diff col: ", difference_col)
        # up the diagonal ( L -> R )
        if (chesspieceaction.targetR <= chesspieceaction.sourceR - 1 and chesspieceaction.targetC <=
            chesspieceaction.sourceC - 1) and (difference_row == difference_col):
            return self.upDiagonalLR(chesspieceaction, color)

        # down the diagonal ( L -> R )
        elif chesspieceaction.targetR >= chesspieceaction.sourceR + 1 and chesspieceaction.targetC >= chesspieceaction.sourceC + 1 and \
                (difference_row == difference_col):
            return self.downDiagonalLR(chesspieceaction, color)

        # up the diagonal ( R -> L )
        elif chesspieceaction.targetR <= chesspieceaction.sourceR - 1 and chesspieceaction.targetC >= chesspieceaction.sourceC + 1 and \
                (difference_row == difference_col):
            return self.upDiagonalRL(chesspieceaction, color)

        # down the diagonal ( R -> L )
        elif chesspieceaction.targetR >= chesspieceaction.sourceR + 1 and chesspieceaction.targetC <= chesspieceaction.sourceC - 1 and \
                (difference_row == difference_col):
            return self.downDiagonalRL(chesspieceaction, color)

    def moveQueen(self, chesspieceaction, color):
        difference_row = abs(chesspieceaction.targetR - chesspieceaction.sourceR)
        difference_col = abs(chesspieceaction.targetC - chesspieceaction.sourceC)
        # Movement in the same row or col allowed only
        if chesspieceaction.targetR == chesspieceaction.sourceR or chesspieceaction.targetC == chesspieceaction.sourceC:
            # print("0")
            return self.moveUpDown(chesspieceaction, color)
        # up the diagonal ( L -> R )
        elif (chesspieceaction.targetR <= chesspieceaction.sourceR - 1 and chesspieceaction.targetC <=
              chesspieceaction.sourceC - 1) and (difference_row == difference_col):
            return self.upDiagonalLR(chesspieceaction, color)

        # down the diagonal ( L -> R )
        elif chesspieceaction.targetR >= chesspieceaction.sourceR + 1 and chesspieceaction.targetC >= chesspieceaction.sourceC + 1 and \
                (difference_row == difference_col):
            return self.downDiagonalLR(chesspieceaction, color)

        # up the diagonal ( R -> L )
        elif chesspieceaction.targetR <= chesspieceaction.sourceR - 1 and chesspieceaction.targetC >= chesspieceaction.sourceC + 1 and \
                (difference_row == difference_col):
            return self.upDiagonalRL(chesspieceaction, color)

        # down the diagonal ( R -> L )
        elif chesspieceaction.targetR >= chesspieceaction.sourceR + 1 and chesspieceaction.targetC <= chesspieceaction.sourceC - 1 and \
                (difference_row == difference_col):
            return self.downDiagonalRL(chesspieceaction, color)

        return False

    def moveKnight(self, chesspieceaction, color):
        # Translations allowed by knight
        X = [2, 1, -1, -2, -2, -1, 1, 2]
        Y = [1, 2, 2, 1, -1, -2, -2, -1]
        for i in range(length):
            # Find the translation
            x_move = chesspieceaction.sourceR + X[i]
            y_move = chesspieceaction.sourceC + Y[i]
            # If translation does not exceed the board dimensions
            if 0 <= x_move < length and 0 <= y_move < length:
                # and the translation is = to the target position
                if x_move == chesspieceaction.targetR and \
                        y_move == chesspieceaction.targetC:
                    # if position empty return true
                    if self.board[x_move][y_move] == "*":
                        return True
                    # If position has a piece, check if it can kill the piece or not
                    else:
                        if color == "white" and '2' in chesspieceaction.itemTargeted:
                            return False
                        elif color == 'black' and '1' in chesspieceaction.itemTargeted:
                            return False
                        else:
                            return True

        return False

    def moveKing(self, chesspieceaction, color):
        # Translations allowed by king
        X = [1, 1, 1, -1, -1, -1, 0, 0]
        Y = [-1, 0, 1, -1, 0, 1, -1, 1]

        for i in range(length):
            # Find the translation
            x_move = chesspieceaction.sourceR + X[i]
            y_move = chesspieceaction.sourceC + Y[i]
            # If translation does not exceed the board dimensions
            if 0 <= x_move < length and 0 <= y_move < length:
                # and the translation is = to the target position
                if x_move == chesspieceaction.targetR and \
                        y_move == chesspieceaction.targetC:
                    # if position empty return true
                    if self.board[x_move][y_move] == "*":
                        return True
                    # If position has a piece, check if it can kill the piece or not
                    else:
                        if color == "white" and chesspieceaction.itemTargeted[1] == '2':
                            return False
                        elif color == 'black' and chesspieceaction.itemTargeted[1] == '1':
                            return False
                        else:
                            return True
        return False

    def legalMove(self, chesspieceaction, player, boardstate, forDetection=False):
        tempBoard = copy.deepcopy(boardstate)
        tempBoard.board[chesspieceaction.sourceR][chesspieceaction.sourceC] = '*'
        tempBoard.board[chesspieceaction.targetR][chesspieceaction.targetC] = chesspieceaction.itemDisplaced
        player.updateKingLocation(tempBoard)
        dangerToKing = player.getKingSafety(tempBoard)
        # if player.color == userColor:
        #     # print("Danger to king by this move is ", dangerToKing)
        if (dangerToKing > 0):
            # print("King is in danger")
            if allowIllegalMoves==False or forDetection==True:
                return False
        if (chesspieceaction.targetR, chesspieceaction.targetC) in self.getLegalMoves(player, chesspieceaction):
            return True
        piece = getPieceName(chesspieceaction.itemDisplaced)
        if piece == "Pawn":
            if player.color == "black":
                return self.moveBlackPawn(chesspieceaction)

            elif player.color == "white":
                return self.moveWhitePawn(chesspieceaction)

        elif piece == "Rook":
            return self.moveRook(chesspieceaction, player.color)

        elif piece == "Bishop":
            return self.moveBishop(chesspieceaction, player.color)

        elif piece == "Queen":
            return self.moveQueen(chesspieceaction, player.color)

        elif piece == "Knight":
            return self.moveKnight(chesspieceaction, player.color)

        elif piece == "King":
            return self.moveKing(chesspieceaction, player.color)

    def getWhitePawnTargets(self, chesspieceaction):
        availableSquares = []
        if chesspieceaction.sourceR == 6:  # first move by white pawn
            if chesspieceaction.sourceR - 2 >= 0 and self.board[chesspieceaction.sourceR - 2][
                chesspieceaction.sourceC] == '*' and self.board[chesspieceaction.sourceR - 1][
                chesspieceaction.sourceC] == '*':  # 2nd forward square is empty
                availableSquares.append((chesspieceaction.sourceR - 2, chesspieceaction.sourceC))

        if chesspieceaction.sourceR - 1 >= 0 and self.board[chesspieceaction.sourceR - 1][
            chesspieceaction.sourceC] == '*':  # next forward square is empty
            availableSquares.append((chesspieceaction.sourceR - 1, chesspieceaction.sourceC))

        if chesspieceaction.sourceR - 1 >= 0 and chesspieceaction.sourceC - 1 >= 0 and '1' in \
                self.board[chesspieceaction.sourceR - 1][chesspieceaction.sourceC - 1]:
            availableSquares.append((chesspieceaction.sourceR - 1, chesspieceaction.sourceC - 1))

        if chesspieceaction.sourceR - 1 >= 0 and chesspieceaction.sourceC + 1 < 8 and '1' in \
                self.board[chesspieceaction.sourceR - 1][chesspieceaction.sourceC + 1]:
            availableSquares.append((chesspieceaction.sourceR - 1, chesspieceaction.sourceC + 1))

        return availableSquares

    def getBlackPawnTargets(self, chesspieceaction):
        availableSquares = []
        if chesspieceaction.sourceR == 1:  # first move by white pawn
            if chesspieceaction.sourceR + 2 < 8 and self.board[chesspieceaction.sourceR + 2][
                chesspieceaction.sourceC] == '*' and self.board[chesspieceaction.sourceR + 1][
                chesspieceaction.sourceC] == '*':  # 2nd forward square is empty
                availableSquares.append((chesspieceaction.sourceR + 2, chesspieceaction.sourceC))

        if chesspieceaction.sourceR + 1 < 8 and self.board[chesspieceaction.sourceR + 1][
            chesspieceaction.sourceC] == '*':  # next forward square is empty
            availableSquares.append((chesspieceaction.sourceR + 1, chesspieceaction.sourceC))

        if chesspieceaction.sourceR + 1 < 8 and chesspieceaction.sourceC - 1 >= 0 and '2' in \
                self.board[chesspieceaction.sourceR + 1][chesspieceaction.sourceC - 1]:
            availableSquares.append((chesspieceaction.sourceR + 1, chesspieceaction.sourceC - 1))

        if chesspieceaction.sourceR + 1 < 8 and chesspieceaction.sourceC + 1 < 8 and '2' in \
                self.board[chesspieceaction.sourceR + 1][chesspieceaction.sourceC + 1]:
            availableSquares.append((chesspieceaction.sourceR + 1, chesspieceaction.sourceC + 1))

        return availableSquares

    def getRookLegalMoves(self, player, chesspieceaction):
        availableSquares = []
        # downDirection
        for i in range(chesspieceaction.sourceR + 1, 8):
            if (player.color == 'black' and '1' in self.board[i][chesspieceaction.sourceC]):
                break
            if (player.color == 'white' and '2' in self.board[i][chesspieceaction.sourceC]):
                break
            if (self.board[i][chesspieceaction.sourceC] == '*'):
                availableSquares.append((i, chesspieceaction.sourceC))
            elif (player.color == 'black' and '2' in self.board[i][chesspieceaction.sourceC]) or (
                    player.color == 'white' and '1' in self.board[i][chesspieceaction.sourceC]):
                availableSquares.append((i, chesspieceaction.sourceC))
                break

        # updirection
        for i in reversed(range(0, chesspieceaction.sourceR)):
            if (player.color == 'black' and '1' in self.board[i][chesspieceaction.sourceC]):
                break
            if (player.color == 'white' and '2' in self.board[i][chesspieceaction.sourceC]):
                break
            if (self.board[i][chesspieceaction.sourceC] == '*'):
                availableSquares.append((i, chesspieceaction.sourceC))
            elif (player.color == 'black' and '2' in self.board[i][chesspieceaction.sourceC]) or (
                    player.color == 'white' and '1' in self.board[i][chesspieceaction.sourceC]):
                availableSquares.append((i, chesspieceaction.sourceC))
                break

        # leftdirection
        for i in reversed(range(0, chesspieceaction.sourceC)):
            if (player.color == 'black' and '1' in self.board[chesspieceaction.sourceR][i]):
                break
            if (player.color == 'white' and '2' in self.board[chesspieceaction.sourceR][i]):
                break
            if (self.board[chesspieceaction.sourceR][i] == '*'):
                availableSquares.append((chesspieceaction.sourceR, i))
            elif (
                    player.color == 'black' and '2' in self.board[chesspieceaction.sourceR][i]) or (
                    player.color == 'white' and '1' in self.board[chesspieceaction.sourceR][i]):
                availableSquares.append((chesspieceaction.sourceR, i))
                break

        # rightdirection
        for i in (range(chesspieceaction.sourceC + 1, 8)):
            if (player.color == 'black' and '1' in self.board[chesspieceaction.sourceR][i]):
                break
            if (player.color == 'white' and '2' in self.board[chesspieceaction.sourceR][i]):
                break
            if (self.board[chesspieceaction.sourceR][i] == '*'):
                availableSquares.append((chesspieceaction.sourceR, i))
            elif (
                    player.color == 'black' and '2' in self.board[chesspieceaction.sourceR][i]) or (
                    player.color == 'white' and '1' in self.board[chesspieceaction.sourceR][i]):
                availableSquares.append((chesspieceaction.sourceR, i))
                break

        return availableSquares

    def getBishopLegalMoves(self, player, chesspieceaction):
        availableSquares = []
        # down diagonal, LR
        j = chesspieceaction.sourceC
        for i in range(chesspieceaction.sourceR + 1, 8):
            j = j + 1
            if (j >= 8):
                break
            if (player.color == 'black' and '1' in self.board[i][j]):
                break
            if (player.color == 'white' and '2' in self.board[i][j]):
                break
            if (self.board[i][j] == '*'):
                availableSquares.append((i, j))
            elif (player.color == 'black' and '2' in self.board[i][j]) or (
                    player.color == 'white' and '1' in self.board[i][j]):
                availableSquares.append((i, j))
                break
        # down diagonal RL
        j = chesspieceaction.sourceC
        for i in range(chesspieceaction.sourceR + 1, 8):
            j = j - 1
            if (j < 0):
                break
            if (player.color == 'black' and '1' in self.board[i][j]):
                break
            if (player.color == 'white' and '2' in self.board[i][j]):
                break
            if (self.board[i][j] == '*'):
                availableSquares.append((i, j))
            elif (player.color == 'black' and '2' in self.board[i][j]) or (
                    player.color == 'white' and '1' in self.board[i][j]):
                availableSquares.append((i, j))
                break
        # up diagonal, LR
        j = chesspieceaction.sourceC
        i = chesspieceaction.sourceR
        while (True):
            j = j + 1
            if (j >= 8):
                break
            i = i - 1
            if (i < 0):
                break
            if (player.color == 'black' and '1' in self.board[i][j]):
                break
            if (player.color == 'white' and '2' in self.board[i][j]):
                break
            if (self.board[i][j] == '*'):
                availableSquares.append((i, j))
            elif (player.color == 'black' and '2' in self.board[i][j]) or (
                    player.color == 'white' and '1' in self.board[i][j]):
                availableSquares.append((i, j))
                break
        # up diagonal RL
        j = chesspieceaction.sourceC
        i = chesspieceaction.sourceR
        while (True):
            j = j - 1
            if (j < 0):
                break
            i = i - 1
            if (i < 0):
                break
            if (player.color == 'black' and '1' in self.board[i][j]):
                break
            if (player.color == 'white' and '2' in self.board[i][j]):
                break
            if (self.board[i][j] == '*'):
                availableSquares.append((i, j))
            elif (player.color == 'black' and '2' in self.board[i][j]) or (
                    player.color == 'white' and '1' in self.board[i][j]):
                availableSquares.append((i, j))
                break
        return availableSquares

    def getQueenLegalMoves(self, player, chesspieceaction):
        availablesquares = []
        availablesquares = self.getRookLegalMoves(player, chesspieceaction)
        availablesquares += self.getBishopLegalMoves(player, chesspieceaction)

        return availablesquares

    def getKingLegalMoves(self, player, chesspieceaction):
        availableSquares = []
        # square below
        if (chesspieceaction.sourceR + 1 < 8):
            if (self.board[chesspieceaction.sourceR + 1][chesspieceaction.sourceC]) == '*':
                availableSquares.append((chesspieceaction.sourceR + 1, chesspieceaction.sourceC))
            if (player.color == "white"):
                if ('1' in self.board[chesspieceaction.sourceR + 1][chesspieceaction.sourceC]):
                    availableSquares.append((chesspieceaction.sourceR + 1, chesspieceaction.sourceC))
            else:
                if ('2' in self.board[chesspieceaction.sourceR + 1][chesspieceaction.sourceC]):
                    availableSquares.append((chesspieceaction.sourceR + 1, chesspieceaction.sourceC))
        # square above
        if (chesspieceaction.sourceR - 1 >= 0):
            if (self.board[chesspieceaction.sourceR - 1][chesspieceaction.sourceC]) == '*':
                availableSquares.append((chesspieceaction.sourceR - 1, chesspieceaction.sourceC))
            if (player.color == "white"):
                if ('1' in self.board[chesspieceaction.sourceR - 1][chesspieceaction.sourceC]):
                    availableSquares.append((chesspieceaction.sourceR - 1, chesspieceaction.sourceC))
            else:
                if ('2' in self.board[chesspieceaction.sourceR - 1][chesspieceaction.sourceC]):
                    availableSquares.append((chesspieceaction.sourceR - 1, chesspieceaction.sourceC))

        # square right
        if (chesspieceaction.sourceC + 1 < 8):
            if (self.board[chesspieceaction.sourceR][chesspieceaction.sourceC + 1]) == '*':
                availableSquares.append((chesspieceaction.sourceR, chesspieceaction.sourceC + 1))
            if (player.color == "white"):
                if ('1' in self.board[chesspieceaction.sourceR][chesspieceaction.sourceC + 1]):
                    availableSquares.append((chesspieceaction.sourceR, chesspieceaction.sourceC + 1))
            else:
                if ('2' in self.board[chesspieceaction.sourceR][chesspieceaction.sourceC + 1]):
                    availableSquares.append((chesspieceaction.sourceR, chesspieceaction.sourceC + 1))
        # square left
        if (chesspieceaction.sourceC - 1 >= 0):
            if (self.board[chesspieceaction.sourceR][chesspieceaction.sourceC - 1]) == '*':
                availableSquares.append((chesspieceaction.sourceR, chesspieceaction.sourceC - 1))
            if (player.color == "white"):
                if ('1' in self.board[chesspieceaction.sourceR][chesspieceaction.sourceC - 1]):
                    availableSquares.append((chesspieceaction.sourceR, chesspieceaction.sourceC - 1))
            else:
                if ('2' in self.board[chesspieceaction.sourceR][chesspieceaction.sourceC - 1]):
                    availableSquares.append((chesspieceaction.sourceR, chesspieceaction.sourceC - 1))

        # square DR
        if (chesspieceaction.sourceC + 1 < 8 and chesspieceaction.sourceR + 1 < 8):
            if (self.board[chesspieceaction.sourceR + 1][chesspieceaction.sourceC + 1]) == '*':
                availableSquares.append((chesspieceaction.sourceR + 1, chesspieceaction.sourceC + 1))
            if (player.color == "white"):
                if ('1' in self.board[chesspieceaction.sourceR + 1][chesspieceaction.sourceC + 1]):
                    availableSquares.append((chesspieceaction.sourceR + 1, chesspieceaction.sourceC + 1))
            else:
                if ('2' in self.board[chesspieceaction.sourceR + 1][chesspieceaction.sourceC + 1]):
                    availableSquares.append((chesspieceaction.sourceR + 1, chesspieceaction.sourceC + 1))

        # square UL
        if (chesspieceaction.sourceC - 1 >= 0 and chesspieceaction.sourceR - 1 >= 0):
            if (self.board[chesspieceaction.sourceR - 1][chesspieceaction.sourceC - 1]) == '*':
                availableSquares.append((chesspieceaction.sourceR - 1, chesspieceaction.sourceC - 1))
            if (player.color == "white"):
                if ('1' in self.board[chesspieceaction.sourceR - 1][chesspieceaction.sourceC - 1]):
                    availableSquares.append((chesspieceaction.sourceR - 1, chesspieceaction.sourceC - 1))
            else:
                if ('2' in self.board[chesspieceaction.sourceR - 1][chesspieceaction.sourceC - 1]):
                    availableSquares.append((chesspieceaction.sourceR - 1, chesspieceaction.sourceC - 1))

        # square UR
        if (chesspieceaction.sourceC + 1 < 8 and chesspieceaction.sourceR - 1 >= 0):
            if (self.board[chesspieceaction.sourceR - 1][chesspieceaction.sourceC + 1]) == '*':
                availableSquares.append((chesspieceaction.sourceR - 1, chesspieceaction.sourceC + 1))
            if (player.color == "white"):
                if ('1' in self.board[chesspieceaction.sourceR - 1][chesspieceaction.sourceC + 1]):
                    availableSquares.append((chesspieceaction.sourceR - 1, chesspieceaction.sourceC + 1))
            else:
                if ('2' in self.board[chesspieceaction.sourceR - 1][chesspieceaction.sourceC + 1]):
                    availableSquares.append((chesspieceaction.sourceR - 1, chesspieceaction.sourceC + 1))
        # square DL
        if (chesspieceaction.sourceC - 1 >= 0 and chesspieceaction.sourceR + 1 < 8):
            if (self.board[chesspieceaction.sourceR + 1][chesspieceaction.sourceC - 1]) == '*':
                availableSquares.append((chesspieceaction.sourceR + 1, chesspieceaction.sourceC - 1))
            if (player.color == "white"):
                if ('1' in self.board[chesspieceaction.sourceR + 1][chesspieceaction.sourceC - 1]):
                    availableSquares.append((chesspieceaction.sourceR + 1, chesspieceaction.sourceC - 1))
            else:
                if ('2' in self.board[chesspieceaction.sourceR + 1][chesspieceaction.sourceC - 1]):
                    availableSquares.append((chesspieceaction.sourceR + 1, chesspieceaction.sourceC - 1))
        return availableSquares

    def getKnightLegalMoves(self, player, chesspieceaction):
        availableSquares = []
        X = [2, 1, -1, -2, -2, -1, 1, 2]
        Y = [1, 2, 2, 1, -1, -2, -2, -1]
        for i in range(length):
            # Find the translation
            x_move = chesspieceaction.sourceR + X[i]
            y_move = chesspieceaction.sourceC + Y[i]
            # If translation does not exceed the board dimensions
            if 0 <= x_move < length and 0 <= y_move < length:
                # if position empty return true
                if self.board[x_move][y_move] == "*":
                    availableSquares.append((x_move, y_move))
                # If position has a piece, check if it can kill the piece or not
                else:
                    if player.color == "white" and self.board[x_move][y_move][1] == '1':
                        availableSquares.append((x_move, y_move))
                    elif player.color == 'black' and self.board[x_move][y_move][1] == '2':
                        availableSquares.append((x_move, y_move))
        return availableSquares

    def getCastlingOption(self, player, chesspieceaction):
        castlingMoves = []
        piece = getPieceName(chesspieceaction.itemDisplaced)
        player.updateKingLocation(self)
        if player.castling == True:
            if player.color == "black":
                if self.board[0][4] == 'k1' and (self.board[0][7] == 'r1' or self.board[0][0] == 'r1'):
                    if player.getKingSafety(self) == 0:
                        emptySpaces = True
                        for j in range(1, 4):
                            if self.board[0][j] != '*':
                                emptySpaces = False
                        if emptySpaces == True:
                            newMove = possibleMove("King", (0, 2), (0, 4), True, (0, 3), (0, 0))
                            castlingMoves.append(newMove)
                        emptySpaces = True
                        for j in range(5, 7):
                            if self.board[0][j] != '*':
                                emptySpaces = False
                        if emptySpaces == True:
                            newMove = possibleMove("King", (0, 6), (0, 4), True, (0, 5), (0, 7))
                            castlingMoves.append(newMove)
            elif player.color == "white":
                if self.board[7][4] == 'k2' and (self.board[7][7] == 'r2' or self.board[7][0] == 'r2'):
                    if player.getKingSafety(self) == 0:
                        emptySpaces = True
                        for j in range(1, 4):
                            if self.board[7][j] != '*':
                                emptySpaces = False
                        if emptySpaces == True:
                            newMove = possibleMove("King", (7, 2), (7, 4), True, (7, 3), (7, 0))
                            castlingMoves.append(newMove)
                        emptySpaces = True
                        for j in range(5, 7):
                            if self.board[7][j] != '*':
                                emptySpaces = False
                        if emptySpaces == True:
                            newMove = possibleMove("King", (7, 6), (7, 4), True, (7, 5), (7, 7))
                            castlingMoves.append(newMove)
        return castlingMoves

    def getLegalMoves(self, player, chesspieceaction, checkCastling=True):
        possibleMoves = []
        piece = getPieceName(chesspieceaction.itemDisplaced)

        if piece == "Pawn":
            if player.color == "black":
                return self.getBlackPawnTargets(chesspieceaction)

            elif player.color == "white":
                return self.getWhitePawnTargets(chesspieceaction)


        elif piece == "Rook":
            possibleMoves = self.getRookLegalMoves(player, chesspieceaction)
            if checkCastling == True:
                castlingMoves = self.getCastlingOption(player, chesspieceaction)
                for move in castlingMoves:
                    possibleMoves.append(move.target2)
            return possibleMoves
        #
        #
        elif piece == "Bishop":
            return self.getBishopLegalMoves(player, chesspieceaction)
        #
        #
        elif piece == "Queen":
            return self.getQueenLegalMoves(player, chesspieceaction)
        #
        #
        elif piece == "Knight":
            return self.getKnightLegalMoves(player, chesspieceaction)
        #
        #
        elif piece == "King":
            possibleMoves = self.getKingLegalMoves(player, chesspieceaction)
            if checkCastling == True:
                castlingMoves = self.getCastlingOption(player, chesspieceaction)
                for move in castlingMoves:
                    possibleMoves.append(move.target)
            return possibleMoves
        else:
            return possibleMoves
        #
        #


class ChessPieceAction():

    def __init__(self, source, target, board):
        self.targetC = target[1]
        self.targetR = target[0]
        self.sourceC = source[1]
        self.sourceR = source[0]

        self.itemTargeted = board[self.targetR][self.targetC]
        self.itemDisplaced = board[self.sourceR][self.sourceC]


x = ChessBoardState()

# INITIALIZE PYGAME
pygame.init()

# Set the height and width of the board
h = 640
w = 640
total_height = w + 100
tileSize = h // 8
PiecesImage = {}

PiecesImage['r1'] = pygame.transform.scale(pygame.image.load('images/r1.png'), (tileSize, tileSize))
PiecesImage['r2'] = pygame.transform.scale(pygame.image.load('images/r2.png'), (tileSize, tileSize))
PiecesImage['p1'] = pygame.transform.scale(pygame.image.load('images/p1.png'), (tileSize, tileSize))
PiecesImage['p2'] = pygame.transform.scale(pygame.image.load('images/p2.png'), (tileSize, tileSize))
PiecesImage['q1'] = pygame.transform.scale(pygame.image.load('images/q1.png'), (tileSize, tileSize))
PiecesImage['q2'] = pygame.transform.scale(pygame.image.load('images/q2.png'), (tileSize, tileSize))
PiecesImage['h1'] = pygame.transform.scale(pygame.image.load('images/h1.png'), (tileSize, tileSize))
PiecesImage['h2'] = pygame.transform.scale(pygame.image.load('images/h2.png'), (tileSize, tileSize))
PiecesImage['b1'] = pygame.transform.scale(pygame.image.load('images/b1.png'), (tileSize, tileSize))
PiecesImage['b2'] = pygame.transform.scale(pygame.image.load('images/b2.png'), (tileSize, tileSize))
PiecesImage['k1'] = pygame.transform.scale(pygame.image.load('images/k1.png'), (tileSize, tileSize))
PiecesImage['k2'] = pygame.transform.scale(pygame.image.load('images/k2.png'), (tileSize, tileSize))


class Player:
    def __init__(self, color):
        self.color = color

        if color == "white":
            self.turn = True
        else:
            self.turn = False
        self.totalScore = 0
        self.pieceMaterial = 239
        self.moves = 0
        self.kingLocation = (0, 0)
        self.castling = True

    def isTerminal(self, state):
        # possibleMoves = self.getMobility(state)
        ischeck = self.checkMate(state)
        isKing = self.updateKingLocation(state)
        isKingSafe = self.getKingSafety(state)

        if not ischeck and isKing != -1:
            return True
        return False

    def getTerminalStateValue(self, state):
        return self.evaluationFunction(state)

    def minValue(self, state, alpha, beta, bestAction):
        if self.isTerminal(state):
            return self.getTerminalStateValue(state), bestAction

        value = math.inf
        possible_moves = self.getMobility(state)
        for move in possible_moves:
            # Get the target and source locations of the actions

            target = move.target
            source = move.source
            newState = copy.deepcopy(state)
            # get the chess piece action on the board
            actionDone = ChessPieceAction(source, target, newState.board)
            if newState.legalMove(actionDone, self, newState):
                # make the action on the board
                newState.action(actionDone, self)
                newValue, newAction = self.maxValue(newState, alpha, beta, actionDone)
                value = min(value, newValue)
                if value <= alpha:
                    bestAction = actionDone
                    return value, bestAction
                beta = min(beta, value)
        return value, bestAction

    def maxValue(self, state, alpha, beta, bestAction):
        if self.isTerminal(state):
            return self.getTerminalStateValue(state), bestAction

        value = -math.inf
        possible_moves = self.getMobility(state)
        for move in possible_moves:
            # Get the target and source locations of the actions
            target = move.target
            source = move.source
            newState = copy.deepcopy(state)
            # get the chess piece action on the board
            actionDone = ChessPieceAction(source, target, newState.board)
            if newState.legalMove(actionDone, self, newState):
                # make the action on the board
                newState.action(actionDone, self)
                newValue, newAction = self.minValue(newState, alpha, beta, actionDone)
                value = max(value, newValue)
                if value >= beta:
                    bestAction = actionDone
                    return value, bestAction
                alpha = max(alpha, value)
        return value, bestAction

    def alphaBetaSearch(self, state, alpha, beta):  # Returns an action for the AI to take
        # If terminal test state return utility state
        bestVal = -math.inf
        maxState = state
        bestAction = None
        beta = math.inf
        possible_moves = self.getMobility(state)
        for move in possible_moves:
            tempAction = ChessPieceAction(move.source, move.target, state.board)
            if (state.legalMove(tempAction, self, state) == True):
                bestAction = tempAction
                break

        for actions in possible_moves:
            # depth = 100
            # Get the target and source locations of the actions
            target = actions.target
            source = actions.source
            newState = copy.deepcopy(state)
            # get the chess piece action on the board
            actionDone = ChessPieceAction(source, target, newState.board)
            if newState.legalMove(actionDone, self, newState):
                # make the action on the board
                newState.action(actionDone, self)
                pieceName = actions.piece

                piece = copy.deepcopy(self)
                piece.evaluationFunction(newState)
                value, action = self.maxValue(newState, bestVal, beta, actionDone)
                if value >= bestVal:
                    bestVal = value
                    maxState = newState
                    bestAction = action
        return maxState, bestAction

    def evaluationFunction(self, boardstate):
        pieceMaterial = 0
        score = 0
        self.updateKingLocation(boardstate)
        # print("location of king is ", self.kingLocation)
        # going over all material for the AI side
        for i in range(length):
            for j in range(length):
                if boardstate.board[i][j] != '*':
                    if (self.color == "white" and boardstate.board[i][j][1] == "2") or (
                            self.color == "black" and boardstate.board[i][j][1] == "1"):
                        pieceMaterial += scores[getPieceName(boardstate.board[i][j])]
                    else:

                        pieceMaterial -= scores[getPieceName(boardstate.board[i][j])]

        # Get opponent mobility
        opponent = Player("black") if self.color == 'white' else Player("white")
        opponent_moves = opponent.getMobility(boardstate)
        opponentKingDanger = opponent.getKingSafety(boardstate)
        self.moves = len(self.getMobility(boardstate))
        self.pieceMaterial = pieceMaterial
        dangertoKing = self.getKingSafety(boardstate)
        # print("Danger to king from", dangertoKing, "pieces")
        # print("Total moves: ", self.moves)
        # print("Piece Material: ", pieceMaterial)
        score += pieceMaterial + 0.1 * (self.moves - len(opponent_moves)) - (3 * dangertoKing) + (
                3 * opponentKingDanger)
        self.totalScore = score

        if self.checkMate(boardstate):
            print("Checkmate")
        # #print("Score is: ", score)
        return score

    def getMobility(self, boardstate, checkCastling=True):
        moves = 0
        possibleMoves = []
        if self.color == 'white':
            for i in range(8):
                for j in range(8):
                    if '2' in boardstate.board[i][j]:  # found a white piece
                        chesspiece = ChessPieceAction((i, j), (i, j), boardstate.board)
                        possibleMovestemp = boardstate.getLegalMoves(self, chesspiece, checkCastling)
                        for move in possibleMovestemp:
                            possibleMoves.append(possibleMove(boardstate.board[i][j], move, (i, j)))
                        if 'k' in boardstate.board[i][j]:
                            if checkCastling == True:
                                castlingMoves = boardstate.getCastlingOption(self, chesspiece)
                                possibleMoves += castlingMoves
                        moves += len(possibleMoves)
        else:
            for i in range(8):
                for j in range(8):
                    if '1' in boardstate.board[i][j]:  # found a black piece
                        chesspiece = ChessPieceAction((i, j), (i, j), boardstate.board)
                        possibleMovestemp = boardstate.getLegalMoves(self, chesspiece, checkCastling)
                        for move in possibleMovestemp:
                            possibleMoves.append(possibleMove(boardstate.board[i][j], move, (i, j)))
                        if 'k' in boardstate.board[i][j]:
                            if checkCastling == True:
                                castlingMoves = boardstate.getCastlingOption(self, chesspiece)
                                possibleMoves += castlingMoves
                        moves += len(possibleMoves)

        return possibleMoves

    def updateKingLocation(self, boardstate):
        if self.color == 'white':
            for i in range(8):
                for j in range(8):
                    if 'k2' in boardstate.board[i][j]:
                        self.kingLocation = (i, j)
                        # print("Location of king ", self.kingLocation)
                        return i, j
        elif self.color == 'black':
            for i in range(8):
                for j in range(8):
                    if 'k1' in boardstate.board[i][j]:
                        self.kingLocation = (i, j)
                        # print("Location of king ", self.kingLocation)
                        return i, j
        return -1

    def getKingSafety(self, boardstate):
        if self.color == 'white':
            oppPlayer = Player('black')
        else:
            oppPlayer = Player('white')
        oppPossibleMoves = oppPlayer.getMobility(boardstate, False)  # get all possible moves of opponent team

        piecesAttackingKing = 0

        # if any(move.target==self.kingLocation for move in oppPossibleMoves ):  # if any possible move can be made on the king with current boardstate
        #     return False
        # else:
        #     return True

        for move in oppPossibleMoves:
            # print(move.target)
            # print(self.kingLocation)
            if move.target[0] == self.kingLocation[0] and move.target[1] == self.kingLocation[1]:
                piecesAttackingKing += 1
        return piecesAttackingKing

    def checkMate(self, boardstate):
        self.updateKingLocation(boardstate)
        allpossibleMoves = self.getMobility(boardstate)
        safe = False
        safemoves = 0
        for move in allpossibleMoves:  # loop through all possible moves, apply and see what boardstate is now
            # tempboardstate = copy.deepcopy(boardstate)
            # tempboardstate.action(ChessPieceAction(move.source, move.target, tempboardstate.board), self)
            # self.updateKingLocation(tempboardstate)
            # kingDanger = self.getKingSafety(tempboardstate)
            # if kingDanger == 0:
            #     safe = True
            #     safemoves+=1
            # if (safe == True):  # a move exists that can make the king safe
            #     return False  # checkmate has not happened
            tempAction = ChessPieceAction(move.source, move.target, boardstate.board)
            if boardstate.legalMove(tempAction, self, boardstate, True) == True:
                safe = True
                break

        if (safe == False):  # no move can make the king safe
            print("checkmate")
            print("Safe moves: ", safemoves)
            return True  # checkmate
        else:  # safe is true, a move exists that makes king safe
            return False  # not checkmate

        # if for all moves, self.getKingSafety is false, checkmate has happened, player loses

    def changeTurn(self):
        if self.turn:
            self.turn = False
        else:
            self.turn = True


def getPieceName(filename):
    if filename[0] == 'r':
        return "Rook"
    elif filename[0] == 'p':
        return "Pawn"
    elif filename[0] == 'q':
        return "Queen"
    elif filename[0] == 'h':
        return "Knight"
    elif filename[0] == 'b':
        return "Bishop"
    elif filename[0] == 'k':
        return "King"


def convertNameToNum(name):
    col = -1
    row = -1
    for key, value in colToChar:
        if name[0] == value:
            col = key
    row = 8 - (int(name[1]))

    return row, col


def convertNumToName(squareLocation):
    name = ""
    if squareLocation[1] in colToChar:
        name += colToChar[squareLocation[1]]
    else:
        return "Error"
    if 8 > squareLocation[0] > -1:
        name += str(8 - squareLocation[0])
    else:
        return "Error"
    return name


def displayGameState(display, gameState):
    displayBoard(display, gameState.board, gameState.possibleSquares)
    # displayPieces(display, gameState.board)


def menuPopUp(display):
    pygame.draw.rect(display, pygame.Color('blue'), pygame.rect.Rect(200, 200, 10, 10), 200)
    pygame.display.set_caption('Chess Board Game')
    # white color
    color = (255, 255, 255)
    color_light = (150, 162, 182)
    color_dark = (0, 0, 0)

    width = display.get_width()
    height = display.get_height()

    optionsButton=height-70
    whiteButton = height / 3
    blackButton = height / 2
    w = width / 2 - 65

    smallfont = pygame.font.SysFont('Corbel', 35)
    boldfont = pygame.font.SysFont('Corbel', 30)
    tinyfont=pygame.font.SysFont('Corbel', 20)
    boldfont.set_bold(True)

    choosetext = boldfont.render('Choose Your Colour', True, color)
    text = smallfont.render('White', True, color_dark)
    text2 = smallfont.render('Black', True, color)
    textmoves = tinyfont.render('Allow Receiving Check', True, color)

    illegalMoves=False
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if ev.type == pygame.MOUSEBUTTONDOWN:

                if w <= mouse[0] <= w + 140 and whiteButton <= mouse[1] <= whiteButton + 40:
                    return 'white', illegalMoves
                elif w <= mouse[0] <= w + 140 and blackButton <= mouse[1] <= blackButton + 40:
                    return 'black', illegalMoves
                elif w-35<=mouse[0]<=(w-35)+210 and optionsButton<=mouse[1]<=optionsButton+35:
                    if illegalMoves==False:
                        illegalMoves=True
                        textmoves=tinyfont.render('Disallow Receiving Check', True, color)
                    else:
                        illegalMoves=False
                        textmoves=tinyfont.render('Allow Receiving Check', True, color)

        display.fill((118, 150, 86))
        mouse = pygame.mouse.get_pos()

        if w <= mouse[0] <= w + 140 and whiteButton <= mouse[1] <= whiteButton + 40:
            pygame.draw.rect(display, color_light, [w, whiteButton, 140, 40])
        else:
            pygame.draw.rect(display, color, [w, whiteButton, 140, 40])

        if w <= mouse[0] <= w + 140 and blackButton <= mouse[1] <= blackButton + 40:
            pygame.draw.rect(display, color_light, [w, blackButton, 140, 40])
        else:
            pygame.draw.rect(display, color_dark, [w, blackButton, 140, 40])

        if w-35 <= mouse[0] <= (w-35)+210 and optionsButton <= mouse[1] <= optionsButton + 35:
            pygame.draw.rect(display, color_light, [w-35, optionsButton, 210, 35])
        else:
            pygame.draw.rect(display, color_dark, [w-35, optionsButton, 210, 35])

        # superimposing the text onto our button
        display.blit(choosetext, (w - 78, whiteButton - 50))
        display.blit(text, (w + 35, whiteButton + 5))
        display.blit(text2, (w + 35, blackButton + 5))
        display.blit(textmoves, (w -25, optionsButton + 5))

        # updates the frames of the game
        pygame.display.update()


def gameOver(display, winner):
    display = pygame.display.set_mode((300, 300))
    display.fill(pygame.Color("black"))

    pygame.draw.rect(display, pygame.Color('blue'), pygame.rect.Rect(200, 200, 10, 10), 200)
    pygame.display.set_caption('Chess Board Game')
    # white color
    color = (255, 255, 255)
    color_light = (150, 162, 182)
    color_dark = (0, 0, 0)

    width = display.get_width()
    height = display.get_height()

    whiteButton = height / 3
    blackButton = height / 2
    w = width / 2 - 65

    smallfont = pygame.font.SysFont('Corbel', 35)
    winner = winner.upper()
    boldfont = pygame.font.SysFont('Corbel', 30)
    boldfont.set_bold(True)

    winnerText = boldfont.render(winner + ' WINS!', True, color)
    text = smallfont.render('Rematch', True, color_dark)
    text2 = smallfont.render('Quit', True, color)
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if ev.type == pygame.MOUSEBUTTONDOWN:

                if w <= mouse[0] <= w + 140 and whiteButton <= mouse[1] <= whiteButton + 40:
                    pyGameBoard()
                elif w <= mouse[0] <= w + 140 and blackButton <= mouse[1] <= blackButton + 40:
                    pygame.quit()

        display.fill((118, 150, 86))
        mouse = pygame.mouse.get_pos()

        if w <= mouse[0] <= w + 140 and whiteButton <= mouse[1] <= whiteButton + 40:
            pygame.draw.rect(display, color_light, [w, whiteButton, 140, 40])
        else:
            pygame.draw.rect(display, color, [w, whiteButton, 140, 40])

        if w <= mouse[0] <= w + 140 and blackButton <= mouse[1] <= blackButton + 40:
            pygame.draw.rect(display, color_light, [w, blackButton, 140, 40])
        else:
            pygame.draw.rect(display, color_dark, [w, blackButton, 140, 40])

        # superimposing the text onto our button
        display.blit(winnerText, (w - 25, whiteButton - 50))
        display.blit(text, (w + 10, whiteButton + 5))
        display.blit(text2, (w + 35, blackButton + 5))

        # updates the frames of the game
        pygame.display.update()


def displayBoard(display, gameBoard, possibleSquares=None):
    global whiteKingDanger
    global blackKingDanger
    if possibleSquares is None:
        possibleSquares = []
    for row in range(0, 8):
        for col in range(0, 8):
            if (row + col) % 2 == 0:
                color = pygame.Color((238, 238, 210))
                width = 0
            else:
                color = pygame.Color((118, 150, 86))
                width = 0
            if (row, col) in possibleSquares:
                color = pygame.Color((176, 21, 44))
                width = 5
            pygame.draw.rect(display, color, pygame.Rect(col * tileSize, (row * tileSize), tileSize, tileSize), width)
            if 'k' in gameBoard[row][col]:
                if '1' in gameBoard[row][col] and blackKingDanger == True:
                    pygame.draw.rect(display, pygame.Color("yellow"),
                                     pygame.Rect(col * tileSize, (row * tileSize), tileSize, tileSize),
                                     width)
                elif '2' in gameBoard[row][col] and whiteKingDanger == True:
                    pygame.draw.rect(display, pygame.Color("yellow"),
                                     pygame.Rect(col * tileSize, (row * tileSize), tileSize, tileSize),
                                     width)
            if gameBoard[row][col] != '*':
                display.blit(PiecesImage[gameBoard[row][col]],
                             pygame.Rect(col * tileSize, (row * tileSize), tileSize, tileSize))


def markKing(state):
    global whiteKingDanger
    global blackKingDanger
    whitePlayer = Player("white")
    blackPlayer = Player("black")
    whitePlayer.updateKingLocation(state)
    blackPlayer.updateKingLocation(state)
    if whitePlayer.getKingSafety(state) > 0:
        whiteKingDanger = True
    else:
        whiteKingDanger = False
    if blackPlayer.getKingSafety(state) > 0:
        blackKingDanger = True
    else:
        blackKingDanger = False


def playSound(track):
    if track == "winner":
        winnerFile = 'images/Winner.wav'
        wave_obj = sa.WaveObject.from_wave_file(winnerFile)
        play = wave_obj.play()
        play.wait_done()
    else:
        loserFile = 'images/Loser.wav'
        wave_obj = sa.WaveObject.from_wave_file(loserFile)
        play = wave_obj.play()
        play.wait_done()


def pyGameBoard():
    pygame.init()
    clk = pygame.time.Clock()
    global allowIllegalMoves
    global whiteKingDanger
    global blackKingDanger
    displayMenu = pygame.display.set_mode((300, 300))
    displayMenu.fill(pygame.Color("black"))
    userColor, allowIllegalMoves= menuPopUp(displayMenu)

    User = Player(userColor)
    AI = Player("white") if User.color == "black" else Player("black")
    whiteKingDanger=False
    blackKingDanger=False

    display = pygame.display.set_mode((h, w))
    display.fill(pygame.Color("white"))
    gameState = ChessBoardState()

    cont = True
    clickedTiles = ()
    userSelected = []
    counter = -1
    # gameOver(display, "white")
    while cont:
        winner = gameState.getWinner(AI, User)
        if winner != -1:
            if winner.color == userColor:
                playSound("winner")
            else:
                playSound("loser")
            gameState.display()
            gameOver(display, winner.color)
            print("Winner is: ", winner.color)
            break
        if counter % 2 == 0:
            AI_State, actionDone = AI.alphaBetaSearch(gameState, -math.inf, math.inf)
            # if gameState == AI_State:
            #     print("No more legal moves for AI")
            #     winner = gameState.getWinner(AI, User)
            #     if winner != -1:
            #         if winner.color == userColor:
            #             playSound("winner")
            #         else:
            #             playSound("loser")
            #         gameState.display()
            #         gameOver(display, winner.color)
            #         print("Winner is: ", winner.color)
            #         break
            gameState = copy.deepcopy(AI_State)
            winner = gameState.getWinner(AI, User)
            if winner != -1:
                if winner.color == userColor:
                    playSound("winner")
                else:
                    playSound("loser")
                gameState.display()
                gameOver(display, winner.color)
                print("Winner is: ", winner.color)
                break

            User.changeTurn()
            if (actionDone != None):
                print(AI.color + " Move: " + getPieceName(actionDone.itemDisplaced) + convertNumToName(
                    (actionDone.targetR, actionDone.targetC)))
            markKing(gameState)
            counter += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cont = False
            elif event.type == pygame.MOUSEBUTTONDOWN and counter == -1:
                if AI.color == 'white':
                    counter += 1  # First Turn AI
                else:
                    counter += 2
                if counter % 2 == 0:
                    AI_State, actionDone = AI.alphaBetaSearch(gameState, -math.inf, math.inf)
                    gameState = copy.deepcopy(AI_State)
                    User.changeTurn()
                    print(AI.color + " Move: " + getPieceName(actionDone.itemDisplaced) + convertNumToName(
                        (actionDone.targetR, actionDone.targetC)))
                    markKing(gameState)
                    counter += 1
            elif event.type == pygame.MOUSEBUTTONDOWN and counter % 2 == 1:

                point = pygame.mouse.get_pos()
                col = point[0] // tileSize
                row = point[1] // tileSize
                if clickedTiles == (row, col):
                    clickedTiles = ()
                    userSelected = []

                clickedTiles = (row, col)
                userSelected.append(clickedTiles)
                if len(userSelected) == 1:  # First Click
                    if gameState.board[row][col] != "*":
                        action = ChessPieceAction(userSelected[0], userSelected[0], gameState.board)
                        gameState.possibleSquares = gameState.getLegalMoves(User, action, True)

                    else:  # If the user selects an empty box
                        userSelected = []
                    # If the user selected a valid box but there were no possible squares
                    if not gameState.possibleSquares:
                        userSelected = []
                if len(userSelected) == 2:  # Second Click
                    action = ChessPieceAction(userSelected[0], userSelected[1], gameState.board)
                    valid = gameState.action(action, User)
                    if valid == -1:
                        print("Illegal Move")
                        userSelected = []
                    if valid != -1:
                        print(User.color + " Move: " + getPieceName(action.itemDisplaced) + convertNumToName(
                            (action.targetR, action.targetC)))
                        AI.changeTurn()
                        markKing(gameState)
                        counter += 1
                        gameState.possibleSquares = []
                    clickedTiles = ()
                    userSelected = []

        displayGameState(display, gameState)
        clk.tick(15)
        pygame.display.flip()


def main():
    pyGameBoard()


if __name__ == "__main__":
    main()
