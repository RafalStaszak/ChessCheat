from game import PgnGame
from parsing import ChessComMovesOnlineParser
from game import PgnGame, Moves
from chessboard import *
import re
import time
from rules import Rules
from notation import *

board = Chessboard().from_fen('1k6/4p3/8/3P4/2p1Pp2/8/3P4/1K6 b - e3 0 1')
moves = 'f4e3 e7e5 d5e6 b8b7 d2d4 c4d3'.split()
print(board.visual)
notation = AlgebraicNotation()

out = notation.pgn(board, moves, white_plays=True, en_passant='e3')
print(out)
