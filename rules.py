from chessboard import *


class RulePiece:
    def __init__(self, square, is_white):
        self.type = ''
        self.square = square
        self.straight = True
        self.diagonal = True
        self.is_white = is_white
        self.max_move = 7

    def possible_moves(self, chessboard):
        moves = list()
        row, col = Square.square_to_index(self.square)

        directions = list()
        if self.straight:
            directions.extend([(1, 0), (0, 1), (-1, 0), (0, -1), ])
        if self.diagonal:
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1), ])

        for direction in directions:
            for i in range(1, self.max_move + 1):
                reach_row, reach_col = row + i * direction[0], col + i * direction[1]
                if Square.is_index_valid(reach_row, reach_col):
                    value = chessboard.squares[reach_row][reach_col]
                    if not Pieces.is_piece(value):
                        moves.append(Square.index_to_square(reach_row, reach_col))
                    else:
                        if Pieces.is_white(value) != self.is_white:
                            moves.append(Square.index_to_square(reach_row, reach_col))
                        break

        return moves


class RuleQueen(RulePiece):
    def __init__(self, square, is_white):
        super().__init__(square, is_white)
        self.type = 'Q'


class RuleKing(RulePiece):
    def __init__(self, square, is_white, kingside=True, queenside=True):
        super().__init__(square, is_white)
        self.type = 'K'
        self.max_move = 1
        self.kingside = kingside
        self.queenside = queenside

    def possible_moves(self, chessboard):
        moves = super(RuleKing, self).possible_moves(chessboard)
        if self.kingside:
            if self.is_white:
                if chessboard['e1'] == Pieces.white_king and chessboard['f1'] == '' and chessboard['g1'] == '' and \
                        chessboard['h1'] == Pieces.white_rook:
                    moves.append('g1')
            else:
                if chessboard['e8'] == Pieces.black_king and chessboard['f8'] == '' and chessboard['g8'] == '' and \
                        chessboard['h8'] == Pieces.black_rook:
                    moves.append('g8')
        if self.queenside:
            if self.is_white:
                if chessboard['e1'] == Pieces.white_king and chessboard['d1'] == '' and chessboard['c1'] == '' and \
                        chessboard['b1'] == '' and chessboard['a1'] == Pieces.white_rook:
                    moves.append('c1')
            else:
                if chessboard['e8'] == Pieces.black_king and chessboard['d8'] == '' and chessboard['c8'] == '' and \
                        chessboard['b8'] == '' and chessboard['a8'] == Pieces.black_rook:
                    moves.append('c8')

        return moves

    def is_kingside_castle(self, move):
        if self.is_white:
            if self.square == 'e1' and move == 'g1':
                return True
        else:
            if self.square == 'e8' and move == 'g8':
                return True

        return False

    def is_queenside_castle(self, move):
        if self.is_white:
            if self.square == 'e1' and move == 'c1':
                return True
        else:
            if self.square == 'e8' and move == 'c8':
                return True

        return False


class RuleRook(RulePiece):
    def __init__(self, square, is_white):
        super().__init__(square, is_white)
        self.type = 'R'
        self.diagonal = False


class RuleBishop(RulePiece):
    def __init__(self, square, is_white):
        super().__init__(square, is_white)
        self.type = 'B'
        self.straight = False


class RuleKnight(RulePiece):
    def __init__(self, square, is_white):
        super().__init__(square, is_white)
        self.type = 'N'
        self.straight = False
        self.diagonal = False

    def possible_moves(self, chessboard):
        moves = list()

        row, col = Square.square_to_index(square=self.square)
        targets = [(row + 2, col + 1), (row + 2, col - 1), (row - 2, col + 1), (row - 2, col - 1), (row + 1, col + 2),
                   (row + 1, col - 2), (row - 1, col + 2), (row - 1, col - 2)]

        for target in targets:
            if Square.is_index_valid(target[0], target[1]):
                target_square = Square.index_to_square(target[0], target[1])
                if chessboard[target_square] == '':
                    moves.append(target_square)
                elif self.is_white != Pieces.is_white(chessboard[target_square]):
                    moves.append(target_square)

        return moves


class RulePawn(RulePiece):
    def __init__(self, square, is_white, en_passant=None):
        super().__init__(square, is_white)
        self.type = 'P'
        self.square = square
        self.en_passant = en_passant
        self.forward = 1
        self.is_white = is_white

    def is_en_passant(self, to_square):
        row, col = Square.square_to_index(self.square)
        if self.is_white and row == 1:
            if Square.move(self.square, 2, 0) == to_square:
                return True
        elif not self.is_white and row == 6:
            if Square.move(self.square, -2, 0) == to_square:
                return True

        return False

    def is_promotion(self, to_square):
        row, col = Square.square_to_index(to_square)
        if self.is_white and row == 7:
            return True
        elif not self.is_white and row == 0:
            return True

        return False

    def possible_moves(self, chessboard):
        moves = list()

        row, col = Square.square_to_index(square=self.square)

        if self.is_white:
            push_square = Square.index_to_square(row + 1, col)
            if not Pieces.is_piece(chessboard[push_square]):
                moves.append(push_square)
                if row == 1:
                    double_push_square = Square.index_to_square(row + 2, col)
                    if chessboard[double_push_square] == '':
                        moves.append(double_push_square)

        else:
            push_square = Square.index_to_square(row - 1, col)
            if not Pieces.is_piece(chessboard[push_square]):

                moves.append(push_square)
                if row == 6:
                    double_push_square = Square.index_to_square(row - 2, col)
                    if not Pieces.is_piece(chessboard[double_push_square]):
                        moves.append(double_push_square)

        hit_squares = list()
        if self.is_white:
            if col - 1 >= 0:
                hit_squares.append(Square.index_to_square(row + 1, col - 1))
            if col + 1 <= 7:
                hit_squares.append(Square.index_to_square(row + 1, col + 1))
        else:
            if col - 1 >= 0:
                hit_squares.append(Square.index_to_square(row - 1, col - 1))
            if col + 1 <= 7:
                hit_squares.append(Square.index_to_square(row - 1, col + 1))

        for hit in hit_squares:
            if chessboard[hit] != '' and Pieces.is_white(chessboard[hit]) != self.is_white:
                moves.append(hit)

        if self.en_passant:
            is_en_passant_white = True if self.en_passant[-1] == '3' else False
            if self.is_white != is_en_passant_white and self.en_passant in hit_squares:
                moves.append(self.en_passant)

        return moves


class Rules:
    NORMAL = 1
    CHECK = 2
    CHECKMATE = 3
    STALEMATE = 4

    def __init__(self):
        self.board = Chessboard()
        self.pieces = list()
        self.possible_moves = list()

        self.en_passant = None

        self.K = True
        self.Q = True
        self.k = True
        self.q = True

        self.promote = None

    def __getitem__(self, item):
        for piece, moves in zip(self.pieces, self.possible_moves):
            if piece.square == item:
                return piece, moves
        return None, None

    def reaching(self, item):
        reaching_pieces = list()

        for piece, moves in zip(self.pieces, self.possible_moves):
            if item in moves:
                reaching_pieces.append(piece)

        return reaching_pieces

    def put(self, board, en_passant=None, wk=True, wq=True, bk=True,
            bq=True, promote=None):
        self.board = board
        self.en_passant = en_passant
        self.K = wk
        self.Q = wq
        self.k = bk
        self.q = bq
        self._pieces()
        self.promote = promote

    def make_move(self, from_square, to_square):
        for piece, moves in zip(self.pieces, self.possible_moves):
            if piece.square == from_square:
                if to_square in moves:
                    piece_value = Pieces.get(piece.type, piece.is_white)

                    if piece.type == 'P':
                        if self.en_passant == to_square:
                            return [from_square, to_square, Square.move(to_square, -1 if piece.is_white else 1, 0)], \
                                   ['', piece_value, '']
                        if piece.is_promotion(to_square):
                            return [from_square, to_square], ['', Pieces.get(self.promote, piece.is_white)]

                        else:
                            return [from_square, to_square], ['', piece_value]

                    if piece.type == 'K':
                        if piece.is_kingside_castle(to_square):
                            return [from_square, to_square, 'f1' if piece.is_white else 'f8',
                                    'h1' if piece.is_white else 'h8'], \
                                   ['', piece_value, Pieces.get('R', piece.is_white), '']
                        if piece.is_queenside_castle(to_square):
                            return [from_square, to_square, 'd1' if piece.is_white else 'd8',
                                    'a1' if piece.is_white else 'a8'], \
                                   ['', piece_value, Pieces.get('R', piece.is_white), '']
                        else:
                            return [from_square, to_square], \
                                   ['', piece_value]

                    return [from_square, to_square], ['', piece_value]

        return [], []

    def _possible_moves(self):
        for piece in self.pieces:
            self.possible_moves.append(piece.possible_moves(self.board))

    def _pieces(self):
        def _selector(piece, square, is_white):
            if piece == Pieces.white_rook or piece == Pieces.black_rook:
                return RuleRook(square, is_white)
            elif piece == Pieces.white_knight or piece == Pieces.black_knight:
                return RuleKnight(square, is_white)
            elif piece == Pieces.white_bishop or piece == Pieces.black_bishop:
                return RuleBishop(square, is_white)
            elif piece == Pieces.white_queen or piece == Pieces.black_queen:
                return RuleQueen(square, is_white)
            elif piece == Pieces.white_king:
                return RuleKing(square, is_white, self.K, self.Q)
            elif piece == Pieces.black_king:
                return RuleKing(square, is_white, self.k, self.q)
            elif piece == Pieces.white_pawn or piece == Pieces.black_pawn:
                return RulePawn(square, is_white, self.en_passant)

        self.pieces.clear()
        self.possible_moves.clear()

        for i in range(8):
            for j in range(8):
                square = Square.index_to_square(i, j)
                value = self.board[square]
                if Pieces.is_piece(value):
                    is_white = Pieces.is_white(value)
                    self.pieces.append(_selector(value, square, is_white))

        self._possible_moves()

    @staticmethod
    def check(board: Chessboard, white_plays):
        rules = Rules()
        rules.put(board, wk=False, wq=False, bk=False, bq=False)
        king = None
        for piece, moves in zip(rules.pieces, rules.possible_moves):
            if piece.type == 'K' and piece.is_white is white_plays:
                king = piece
        for piece, moves in zip(rules.pieces, rules.possible_moves):
            if piece.is_white is not white_plays:
                for move in moves:
                    if king.square == move:
                        return True

        return False

    def status(self, white_plays):
        status = Rules.NORMAL

        king = None
        king_moves = None
        for piece, moves in zip(self.pieces, self.possible_moves):
            if piece.type == 'K' and piece.is_white is white_plays:
                king = piece
                king_moves = moves

        can_move = False
        for king_move in king_moves:
            valid_move = True
            # for piece, moves in zip(self.pieces, self.possible_moves):
            #     if piece.is_white is not white_plays:
            #         if king_move in moves:
            #             valid_move = False
            #             break

            board_king_move = self.board.copy()
            board_king_move.update_squares(*self.make_move(king.square, king_move))
            if Rules.check(board_king_move, white_plays):
                valid_move = False

            if valid_move:
                can_move = True
                break

        check_pieces = list()
        check_moves = list()

        for piece, moves in zip(self.pieces, self.possible_moves):
            if piece.is_white is not white_plays:
                for move in moves:
                    if king.square == move:
                        check_pieces.append(piece)

                        moves_between = list()
                        moves_between.append(move)
                        moves_between.extend(Square.between(piece.square, move))
                        check_moves.append(moves_between)
                        status = Rules.CHECK
                        break

        if status == Rules.CHECK:

            if not can_move:
                can_deflect = False
                can_capture = False

                if len(check_pieces) == 1:
                    for piece, moves in zip(self.pieces, self.possible_moves):
                        if piece.type != 'K' and piece.is_white is white_plays:
                            for move in moves:

                                if move in check_moves[0]:
                                    can_deflect = True
                                    break

                                if move == check_pieces[0].square:
                                    board_update = self.board.copy()
                                    board_update.update_squares(*self.make_move(piece.square, move))
                                    if not Rules.check(board_update, white_plays):
                                        can_capture = True
                                        break

                            if can_deflect or can_capture:
                                break

                    if not can_deflect and not can_capture:
                        status = Rules.CHECKMATE
                else:
                    status = Rules.STALEMATE
                    for piece, moves in zip(self.pieces, self.possible_moves):
                        if piece.is_white and piece.type != 'K':
                            if len(moves) != 0:
                                status = Rules.NORMAL
                                break

        return status

    @staticmethod
    def last_move(current, previous, en_passant=None):
        difference = previous - current
        rules = Rules()
        promote = Rules.find_promotion(current, previous)
        rules.put(difference, en_passant=en_passant, wk=True, wq=True, bk=True, bq=True, promote=promote)

        for piece, moves in zip(rules.pieces, rules.possible_moves):
            for move in moves:
                board = previous.copy()
                squares, values = rules.make_move(piece.square, move)
                board.update_squares(squares, values)
                if current == board:
                    return piece.square, move

        return None, None

    @staticmethod
    def find_en_passant(current, previous):
        difference = previous - current
        rules = Rules()
        rules.put(difference, en_passant=None, wk=True, wq=True, bk=True, bq=True)

        for piece, moves in zip(rules.pieces, rules.possible_moves):
            for move in moves:
                if piece.type == 'P':
                    after_move = previous.copy()
                    after_move.update_squares(*rules.make_move(piece.square, move))
                    if after_move == current:
                        if piece.is_en_passant(move):
                            if piece.is_white:
                                return Square.move(piece.square, 1, 0)
                            else:
                                return Square.move(piece.square, -1, 0)

        return None

    @staticmethod
    def castle_rights(current):
        wk, wq, bk, bq = True, True, True, True
        if current['e1'] != Pieces.white_king:
            wk, wq = False, False
        elif current['h1'] != Pieces.white_rook:
            wk = False
        elif current['a1'] != Pieces.white_rook:
            wq = False

        if current['e8'] != Pieces.black_king:
            bk, bq = False, False
        elif current['h8'] != Pieces.black_rook:
            bk = False
        elif current['a8'] != Pieces.black_rook:
            bq = False

        return wk, wq, bk, bq

    @staticmethod
    def find_promotion(current, previous):
        difference = previous - current
        rules = Rules()
        rules.put(difference, en_passant=None, wk=True, wq=True, bk=True, bq=True)

        for piece, moves in zip(rules.pieces, rules.possible_moves):
            for move in moves:
                if piece.type == 'P':
                    if piece.is_promotion(move):
                        return current[move]
        return None
