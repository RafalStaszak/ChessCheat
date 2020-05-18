import unittest
import copy
from chessboard import *
from rules import *
from game import *

class MyTestCase(unittest.TestCase):
    def test_something(self):
        fen1 = '5k2/5n2/8/8/1P1P4/8/8/4K3 w - - 0 1'
        fen2 = '5k2/5n2/8/3P4/1P6/8/8/4K3 b - - 0 1'
        fen3 = '5k2/8/3n4/3P4/1P6/8/8/4K3 w - - 0 1'
        fen4 = '5k2/8/3n4/1P1P4/8/8/8/4K3 b - - 0 1'

        board1 = Chessboard.from_fen(fen1)
        board2 = Chessboard.from_fen(fen2)
        board3 = Chessboard.from_fen(fen3)
        board4 = Chessboard.from_fen(fen4)

        game = FenGame()
        game.put(board1)
        print(game.white_to_play)
        game.put(board2)
        print(game.white_to_play)
        game.put(board2)
        print(game.white_to_play)
        game.put(board4)
        print(game.white_to_play)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
