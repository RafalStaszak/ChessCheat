import time

from chessboard import *
from rules import Rules


class Moves:
    def __init__(self, moves=None):
        if moves is None:
            moves = list()
        self._moves = moves
        self._filter()

    def _filter(self):
        if self._moves is not None:
            self._moves = list(filter(lambda x: x != '1-0' and x != '0-1' and x != '1/2-1/2', self._moves))

    def new(self, moves):
        length = len(self)
        if len(moves) >= length:
            old = moves[:length]
            new = moves[length:]

            if old == self:
                return new
            else:
                return None
        else:
            return None

    def __eq__(self, other):

        if isinstance(other, Moves):
            if len(self._moves) == len(other._moves):
                for a, b in zip(self._moves, other._moves):
                    if a != b:
                        return False

                return True
            else:
                return False

        else:
            return False

    def __getitem__(self, item):
        if self._moves is not None:
            if isinstance(item, slice):
                return Moves(self._moves[item])
            elif isinstance(item, int):
                return self._moves[item]
            else:
                return None
        else:
            return None

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        return self._moves.__iter__()

    def __str__(self):
        return str(self._moves)

    def __len__(self):
        if self._moves is not None:
            return len(self._moves)
        else:
            return 0


class Game:
    def __init__(self):
        self._board = Chessboard()
        self.board.starting_position()
        self.white_to_play = True
        self.en_passant = None
        self.wk, self.wq, self.bk, self.bq = True, True, True, True

    def put(self, data):
        raise NotImplementedError

    @property
    def board(self):
        return self._board

    @property
    def fen(self):
        if self._board is not None:
            position = str(self._board)
            player = 'w' if self.white_to_play else 'b'

            castle = ''
            if self.wk:
                castle += 'K'
            if self.wq:
                castle += 'Q'
            if self.bk:
                castle += 'k'
            if self.bq:
                castle += 'q'

            if len(castle) == 0:
                castle = '-'

            en_passant = self.en_passant if self.en_passant is not None else '-'

            return '{} {} {} {} {} {}'.format(position, player, castle, en_passant, 0, 1)

        return None

    def reset(self):
        self._board.starting_position()
        self.white_to_play = True
        self.en_passant = None
        self.wk, self.wq, self.bk, self.bq = True, True, True, True

    def update_castle(self, wk, wq, bk, bq):
        self.wk *= wk
        self.wq *= wq
        self.bk *= bk
        self.bq *= bq


class PgnGame(Game):
    def __init__(self):
        super().__init__()
        self._moves = Moves()
        self.white_to_play = True
        self.pattern = re.compile(r'([KQNBR]?)([^=+#]+)[=]?([QNBR]?)')

        self.reset()

    def put(self, moves: Moves):
        new_moves = self._moves.new(moves)

        if new_moves is None:
            self._moves = moves
            self.reset()
            self.white_to_play = True
            new_moves = moves
        else:
            self._moves = moves

        for move in new_moves:
            self.make_move(move, self.white_to_play)
            self.white_to_play = not self.white_to_play

    def make_move(self, move: str, white):
        match = self.pattern.match(move)

        piece_type = Pieces.get('p' if match.group(1) == '' else match.group(1), white=True)
        move = match.group(2).replace('x', '')
        promotion = match.group(3)

        rules = Rules()
        rules.put(self._board, self.en_passant, self.wk, self.wq, self.bk, self.bq,
                  promote=None if promotion == '' else promotion)

        exact_row, exact_col = '', ''
        if move.lower() == 'o-o':
            if white:
                move = 'g1'
            else:
                move = 'g8'
            piece_type = 'K'
        elif move.lower() == 'o-o-o':
            if white:
                move = 'c1'
            else:
                move = 'c8'
            piece_type = 'K'
        elif len(move) == 3:
            char = move[0]
            move = move[-2:]
            if char.isdigit():
                exact_col = char
            else:
                exact_row = char

        pieces, possible_moves = rules.pieces, rules.possible_moves
        for piece, moves in zip(pieces, possible_moves):
            if piece_type == Pieces.get(piece.type, True) and piece.is_white == white and move in moves \
                    and exact_row in piece.square and exact_col in piece.square:

                board_copy = self._board.copy()
                board_copy.update_squares(*rules.make_move(piece.square, move))
                rules_check = Rules()
                rules_check.put(board_copy, self.en_passant, self.wk, self.wq, self.bk, self.bq)
                status = rules_check.status(white)

                if status == Rules.NORMAL:
                    previous_board = self._board.copy()
                    self._board.update_squares(*rules.make_move(piece.square, move))
                    self.update_castle(*Rules.castle_rights(self._board))
                    self.en_passant = Rules.find_en_passant(self._board, previous_board)
                    break


class FenGame(Game):
    def __init__(self):
        super().__init__()
        self.boards = list()

        self.starting_board = Chessboard()
        self.starting_board.starting_position()

    def put(self, board):
        if board == self.starting_board:
            self.reset()

        if len(self.boards) == 0:
            self.boards.append(board)
            self._board = board
            self.white_to_play = True
        elif board != self.boards[-1]:
            self.boards.append(board)
            self._board = board
            from_square, to_square = Rules.last_move(self.boards[-1], self.boards[-2], self.en_passant)
            if to_square is not None:
                if Pieces.is_white(self.boards[-1][to_square]):
                    self.white_to_play = False
                else:
                    self.white_to_play = True

                en_passant = Rules.find_en_passant(self.boards[-1], self.boards[-2])
                self.en_passant = en_passant

                wk, wq, bk, bq = Rules.castle_rights(board)
                self.wk *= wk
                self.wq *= wq
                self.bk *= bk
                self.bq *= bq

            else:
                self.en_passant = None
                self.white_to_play = None
                self.wk, self.wq, self.bk, self.bq = False, False, False, False

    def white_plays(self, play):
        self.white_to_play = play

    def reset(self):
        super().reset()
        self.boards.clear()
