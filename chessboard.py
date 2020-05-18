import re


class Pieces:
    black_king = 'k'
    black_queen = 'q'
    black_bishop = 'b'
    black_knight = 'n'
    black_rook = 'r'
    black_pawn = 'p'
    white_king = 'K'
    white_queen = 'Q'
    white_bishop = 'B'
    white_knight = 'N'
    white_rook = 'R'
    white_pawn = 'P'

    @staticmethod
    def is_white(piece: str):
        return piece in 'KQBNRP'

    @staticmethod
    def is_piece(piece: str):
        return piece.upper() in 'KQBNRP' and piece != ''

    @staticmethod
    def get(piece: str, white):
        if piece is None:
            return ''

        if white is True:
            if piece.upper() == 'P':
                return Pieces.white_pawn
            if piece.upper() == 'R':
                return Pieces.white_rook
            if piece.upper() == 'N':
                return Pieces.white_knight
            if piece.upper() == 'B':
                return Pieces.white_bishop
            if piece.upper() == 'K':
                return Pieces.white_king
            if piece.upper() == 'Q':
                return Pieces.white_queen

        else:
            if piece.upper() == 'P':
                return Pieces.black_pawn
            if piece.upper() == 'R':
                return Pieces.black_rook
            if piece.upper() == 'N':
                return Pieces.black_knight
            if piece.upper() == 'B':
                return Pieces.black_bishop
            if piece.upper() == 'K':
                return Pieces.black_king
            if piece.upper() == 'Q':
                return Pieces.black_queen

        return ''


class Square:
    @staticmethod
    def square_to_index(square: str):
        square.lower()
        assert 'a' <= square[0] <= 'h' and '1' <= square[1] <= '8'

        row = ord(square[1]) - ord('1')
        col = ord(square[0]) - ord('a')

        return row, col

    @staticmethod
    def between(a, b):
        squares = list()
        row_a, col_a = Square.square_to_index(a)
        row_b, col_b = Square.square_to_index(b)

        dir_row = 1 if row_b - row_a > 0 else -1 if row_b - row_a < 0 else 0
        dir_col = 1 if col_b - col_a > 0 else -1 if col_b - col_a < 0 else 0

        if abs(row_b - row_a) == abs(col_b - col_a) or dir_row == 0 or dir_col == 0:
            while row_a != row_b or col_a != col_b:
                row_a += dir_row
                col_a += dir_col
                if row_a != row_b or col_a != col_b:
                    squares.append(Square.index_to_square(row_a, col_a))

        return squares

    @staticmethod
    def index_to_square(row, col):
        assert 0 <= row <= 7 and 0 <= col <= 7

        col_letter = chr(ord('a') + col)
        row_number = row + 1

        return col_letter + str(row_number)

    @staticmethod
    def move(square, row, col):
        r, c = Square.square_to_index(square)

        return Square.index_to_square(r + row, c + col)

    @staticmethod
    def is_index_valid(row, col):
        if 0 <= row <= 7 and 0 <= col <= 7:
            return True
        else:
            return False

    @staticmethod
    def is_square_valid(square):
        square.lower()
        if len(square) == 2:
            return 'a' <= square[0] <= 'h' and '1' <= square[1] <= '8'
        else:
            return False


class Chessboard:
    def __init__(self):
        self.squares = [['' for _ in range(8)] for _ in range(8)]

    def copy(self):
        copy = Chessboard()
        for i in range(8):
            for j in range(8):
                copy.squares[i][j] = self.squares[i][j]

        return copy

    def starting_position(self):
        for i in range(2, 6):
            for j in range(8):
                self.squares[i][j] = ''

        self['a1'] = Pieces.white_rook
        self['b1'] = Pieces.white_knight
        self['c1'] = Pieces.white_bishop
        self['d1'] = Pieces.white_queen
        self['e1'] = Pieces.white_king
        self['f1'] = Pieces.white_bishop
        self['g1'] = Pieces.white_knight
        self['h1'] = Pieces.white_rook

        for code in range(ord('a'), ord('h') + 1):
            letter = chr(code)
            self[letter + '2'] = Pieces.white_pawn
            self[letter + '7'] = Pieces.black_pawn

        self['a8'] = Pieces.black_rook
        self['b8'] = Pieces.black_knight
        self['c8'] = Pieces.black_bishop
        self['d8'] = Pieces.black_queen
        self['e8'] = Pieces.black_king
        self['f8'] = Pieces.black_bishop
        self['g8'] = Pieces.black_knight
        self['h8'] = Pieces.black_rook

    @property
    def visual(self):
        out = ''

        for i in range(8):
            for j in range(8):
                value = self.squares[7 - i][j]
                if Pieces.is_piece(value):
                    out = out + "| {} ".format(self.squares[7 - i][j])
                else:
                    out = out + "|   "

            out = out + '|\n'

        return out

    def update_squares(self, squares, values):
        for s, v in zip(squares, values):
            self[s] = v

    def __getitem__(self, item):
        row, col = Square.square_to_index(item)
        return self.squares[row][col]

    def __setitem__(self, key, value):
        row, col = Square.square_to_index(key)
        self.squares[row][col] = value

    def __eq__(self, other):
        if isinstance(other, Chessboard):
            for i in range(8):
                for j in range(8):
                    if self.squares[i][j] != other.squares[i][j]:
                        return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __sub__(self, other):
        result = Chessboard()
        for i in range(8):
            for j in range(8):
                if self.squares[i][j] != other.squares[i][j]:
                    result.squares[i][j] = self.squares[i][j]
                else:
                    result.squares[i][j] = ''
        return result

    def __str__(self):
        line = ''
        for i in range(8):
            j = 0
            empty = 0
            while True:
                square = self.squares[7 - i][j]
                if square == '':
                    empty = empty + 1
                else:
                    if empty > 0:
                        line = line + str(empty)
                        empty = 0
                    line = line + square
                j = j + 1

                if j == 8:
                    if empty > 0:
                        line = line + str(empty)
                    break
            if i != 7:
                line = line + '/'

        return line

    @staticmethod
    def from_fen(fen):
        out = Chessboard()

        regex = re.compile('\S+\/\S+\/\S+\/\S+\/\S+\/\S+\/\S+\/\S+')
        match = regex.match(fen)

        positions = match.group(0)
        lines = positions.split('/')

        for i, line in enumerate(lines):
            j = 0
            for char in line:
                if '1' <= char <= '8':
                    count = ord(char) - ord('0')
                    for k in range(count):
                        out.squares[7 - i][j + k] = ''
                    j = j + count
                else:
                    out.squares[7 - i][j] = char
                    j = j + 1
        return out
