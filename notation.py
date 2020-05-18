from chessboard import *
from rules import Rules


class AlgebraicNotation:

    def __init__(self):
        self.castling = lambda x: 'O-O' if x.upper() == 'K' else 'O-O-O'
        self.promoting = lambda x: '=' + x if x is not None else ''
        self.threatening = lambda x: '+' if x == Rules.CHECK else '#' if x == Rules.CHECKMATE else ''
        self.taking = lambda x: 'x' if x else ''
        self.moving = lambda x: '' if x.upper() == 'P' else x.upper()
        self.castle_type = lambda x, y: 'K' if (x == 'e1g1' or x == 'e8g8') and y.upper() == 'K' \
            else 'Q' if (x == 'e1c1' or x == 'e8c8') and y.upper() == 'K' else None
        self.rules = Rules()
        self.en_passant = None

    def pgn(self, board: Chessboard, line, white_plays=True, en_passant=None):
        out = list()
        self.en_passant = en_passant

        for move in line:
            if move is None:
                out.append('Invalid Move!')

            if move == '(none)':
                self.rules.put(board, en_passant=self.en_passant)
                status = self.rules.status(white_plays)
                if status == Rules.CHECKMATE:
                    out.append('Checkmate!')
                elif status == Rules.STALEMATE:
                    out.append('Stalemate!')
                break

            promote = None
            if len(move) == 5:
                promote = move[-1].upper()
                move = move[:4]

            self.rules.put(board, en_passant=self.en_passant, promote=promote)

            from_square = move[:2]
            to_square = move[2:]
            piece = board[from_square]

            castle = self.castle_type(move, piece)
            takes = False
            ambigious = ''

            if board[to_square] != '':
                takes = True
            elif self.en_passant:
                if piece.upper() == 'P' and to_square == self.en_passant:
                    takes = True

            reaching_pieces = self.rules.reaching(to_square)
            reaching_pieces = list(
                filter(lambda x: x.type == piece.upper() and x.is_white == white_plays, reaching_pieces))

            if len(reaching_pieces) > 1:
                rows, cols = list(), list()
                col, row = from_square[0], from_square[1]
                for p in reaching_pieces:
                    cols.append(p.square[0])
                    rows.append(p.square[1])
                if cols.count(col) > 1:
                    ambigious += row
                elif rows.count(row) > 1:
                    ambigious += col
                else:
                    ambigious += col

            board.update_squares(*self.rules.make_move(from_square, to_square))

            self.rules.put(board, self.en_passant)
            status = self.rules.status(not white_plays)

            if piece.upper() == 'P':
                if abs(int(from_square[1]) - int(to_square[1])) == 2:
                    self.en_passant = from_square[0] + str((int(from_square[1]) + int(to_square[1])) // 2)

                if takes:
                    ambigious = from_square[0]

            white_plays = not white_plays

            out.append(self.move(piece, to_square, takes, status, promote, ambigious, castle))

        return out

    def move(self, piece, square, takes=False, status=Rules.NORMAL, promote=None, ambigious='', castle=None):
        if castle:
            return self.castling(castle)
        else:
            return '{}{}{}{}{}{}'.format(self.moving(piece), ambigious, self.taking(takes), square,
                                         self.promoting(promote), self.threatening(status))
