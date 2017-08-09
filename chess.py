#! -*- coding: utf-8 -*-
from abc import abstractmethod, ABCMeta


THINKING_DEPTH = 4


class Color(object):
    BLACK = 1
    WHITE = 2
    EMPTY = 0

    @classmethod
    def invert(cls, color):
        if color == cls.EMPTY:
            return color
        return cls.BLACK if color == cls.WHITE else cls.WHITE


class Chessboard(object):
    SPACE_COLOR_WHITE = 209
    SPACE_COLOR_BLACK = 94

    board = None

    def fill(self):
        board = self.board = [[EmptyCell() for x in range(8)] for y in range(8)]
        black = Color.BLACK
        white = Color.WHITE
        # simple start position on the board
        board[1][0] = ChessmanPawn(black)
        board[1][1] = ChessmanPawn(black)
        board[1][2] = ChessmanPawn(black)
        board[1][3] = ChessmanKing(black)
        board[3][1] = ChessmanPawn(white)
        board[3][3] = ChessmanKing(white)
        board[2][2] = ChessmanRook(white)

    def clone(self):
        cb = Chessboard()
        cb.board = [self.board[i][:] for i in range(8)]
        return cb

    def get_chessman(self, x, y):
        return self.board[y][x]

    def get_color(self, x, y):
        return self.get_chessman(x, y).color

    def get_chessman_moves(self, x, y):
        return self.get_chessman(x, y).get_moves(self, x, y)

    def move_chessman(self, xy_from, xy_to):
        captured = self.board[xy_to[1]][xy_to[0]]
        self.board[xy_to[1]][xy_to[0]] = self.board[xy_from[1]][xy_from[0]]
        self.board[xy_from[1]][xy_from[0]] = EmptyCell()
        return captured

    def is_empty(self, x, y):
        return self.get_chessman(y, x).CODE == 'empty'

    def rate(self, color):
        res = 0
        pawn_x_position = []
        for y in range(8):
            for x in range(8):
                if self.get_color(x, y) != color:
                    continue
                chessman = self.get_chessman(x, y)
                res += chessman.rate(self, x, y)
                if chessman.CODE == 'pawn':
                    pawn_x_position.append(x)
        # double pawns reduce the rate
        p = pawn_x_position
        res += 2 * (len(set(p)) - len(p))
        # alone pawn reduce the rate
        for i in range(1, 6):
            if i in p and (i-1) not in p and (i+1) not in p:
                res -= 2
        return res

    def __str__(self):
        res = " a b c d e f g h\n"
        for y in range(8):
            res += "\033[0m" + str(8 - y)
            for x in range(8):
                color = self.SPACE_COLOR_BLACK if (x + y) % 2 else self.SPACE_COLOR_WHITE
                res += '\033[48;5;%sm%s ' % (color, self.board[y][x])
            res += "\n"
        res += "\033[0m"
        return res


class EmptyCell(object):
    CODE = 'empty'
    color = Color.EMPTY

    def get_moves(self, board, x, y):
        raise Exception('Error!')

    def rate(self, board, x, y):
        raise Exception('Error!')

    def __str__(self):
        return ' '


class Chessman(object):
    __metaclass__ = ABCMeta

    CODE = None
    VALUE = None
    WHITE_IMG = None
    BLACK_IMG = None

    color = None

    def __init__(self, color):
        self.color = color

    @abstractmethod
    def get_moves(self, board, x, y):
        return []

    @abstractmethod
    def rate(self, board, x, y):
        return 0

    def enemy_color(self):
        return Color.invert(self.color)

    def __str__(self):
        return self.WHITE_IMG if self.color == Color.WHITE else self.BLACK_IMG


class ChessmanPawn(Chessman):
    CODE = 'pawn'
    VALUE = 10
    WHITE_IMG = '♙'
    BLACK_IMG = '♟'

    def get_moves(self, board, x, y):
        moves = []
        y += -1 if self.color == Color.WHITE else 1
        if y == -1 or y == 8:
            return moves
        if x > 0 and board.get_color(x-1, y) == self.enemy_color():
            moves.append([x-1, y])
        if x < 7 and board.get_color(x+1, y) == self.enemy_color():
            moves.append([x+1, y])
        if board.is_empty(x, y):
            moves.append([x, y])
            if self.color == Color.WHITE and y == 5 and board.is_empty(x, y-1):
                moves.append([x, y-1])
            if self.color == Color.BLACK and y == 2 and board.is_empty(x, y+1):
                moves.append([x, y+1])
        return moves

    def rate(self, board, x, y):
        return self.VALUE + 1 * (8-y if self.color == Color.WHITE else y)


class ChessmanKing(Chessman):
    CODE = 'king'
    VALUE = 0
    WHITE_IMG = '♔'
    BLACK_IMG = '♚'

    def get_moves(self, board, x, y):
        moves = []
        for j in (y-1, y, y+1):
            for i in (x-1, x, x+1):
                if i == x and j == y:
                    continue
                if 0 <= i <= 7 and 0 <= j <= 7 and board.get_color(i, j) != self.color:
                    moves.append([i, j])
        return moves

    def rate(self, board, x, y):
        return self.VALUE


class ChessmanRook(Chessman):
    CODE = 'rook'
    VALUE = 50
    WHITE_IMG = '♖'
    BLACK_IMG = '♜'

    def get_moves(self, board, x, y):
        moves = []
        for j in (-1, 1):
            i = x + j
            while 0 <= i <= 7:
                color = board.get_color(i, y)
                if color == self.color:
                    break
                moves.append([i, y])
                if color != Color.EMPTY:
                    break
                i += j
        for j in (-1, 1):
            i = y + j
            while 0 <= i <= 7:
                color = board.get_color(x, i)
                if color == self.color:
                    break
                moves.append([x, i])
                if color != Color.EMPTY:
                    break
                i += j
        return moves

    def rate(self, board, x, y):
        return self.VALUE


class AI(object):
    def __init__(self, my_color, depth):
        self.my_color = my_color
        self.enemy_color = Color.invert(my_color)
        self.depth = depth

    def do(self, board, depth=0):
        enemy = bool(depth % 2)
        color = self.enemy_color if enemy else self.my_color
        if depth == self.depth:
            return board.rate(self.my_color) - board.rate(self.enemy_color)*1.1
        rates = []
        for y in range(8):
            for x in range(8):
                if board.get_color(x, y) != color:
                    continue
                xy_from = [x, y]
                for xy_to in board.get_chessman_moves(x, y):
                    new_board = board.clone()
                    target_cell = new_board.move_chessman(xy_from, xy_to)
                    captured = target_cell.CODE != 'empty'
                    if captured and target_cell.CODE == 'king':
                        rate = -1000 if enemy else 1000  # king capturing
                    else:
                        rate = self.do(new_board, depth + 1)
                        if rate is None:
                            continue
                        if captured and not enemy:
                            rate += self.depth - depth  # a little more aggression
                    if depth:
                        rates.append(rate)
                    else:
                        rates.append([rate, xy_from, xy_to])
        if not depth:
            return rates
        if not rates:
            return None
        rate = min(rates) if enemy else max(rates)
        return rate


class Game(object):
    @staticmethod
    def clear_screen():
        print "\033[2J\033[1;3H\033[14;0m"

    def __init__(self):
        cb = Chessboard()
        cb.fill()

        self.clear_screen()
        print cb

        color = Color.WHITE
        for i in range(22):
            max_rate = -9999
            xy_from = xy_to = None
            rates = AI(color, THINKING_DEPTH).do(cb)
            for rate in rates:
                if rate[0] < max_rate:
                    continue
                max_rate, xy_from, xy_to = rate
            if not xy_from:
                print 'end'
                exit()
            cb.move_chessman(xy_from, xy_to)
            color = Color.invert(color)
            self.clear_screen()
            print cb

Game()
