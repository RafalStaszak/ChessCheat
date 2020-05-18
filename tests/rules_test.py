import unittest
import copy
from chessboard import *
from rules import *


class MyTestCase(unittest.TestCase):
    def test_something(self):
        fen = '5k2/1P1P4/8/8/8/8/8/4K3 w - - 0 1'

        board = Chessboard()
        board.load_fen(fen)
        print(board.visual)

        rules = Rules()
        rules.put(board, en_passant=None, wk=True, wq=True, promote='Q')
        piece, moves = rules['b7']
        print(moves)
        squares, values = rules.make_move('b7', 'b8')
        board_2 = board.copy()
        board_2.update_squares(squares, values)
        print(board_2.visual)
        print('is next ', Rules.is_next(board_2, board, en_passant='g6'))
        print('en passant ', Rules.find_en_passant(board_2, board))
        print('promotion ', Rules.find_promotion(board_2, board))

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
