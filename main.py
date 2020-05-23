from browser import Browser
from game import FenGame, PgnGame, Game, Moves
from rules import Rules
from chessboard import Chessboard, Square, Pieces
from engine import Engine, DEFAULT_STOCKFISH_PARAMS, DEFAULT_LEELA_PARAMS
import time
import threading
from parsing import select_parser
from notation import AlgebraicNotation
from os import name, system


class App:
    def __init__(self):
        self.browser = Browser()
        self.parser = None

        self.history = None
        self.fen_history = FenGame()
        self.pgn_history = PgnGame()
        self.notation = AlgebraicNotation()

        self.params = DEFAULT_LEELA_PARAMS
        self.params['MultiPV'] = 3

        self.engine = None
        self.new_data = None
        self.last_data = None

        self.best_move = list()
        self.best_lines = list()
        self.scores = list()

        self.new_analysis = False

        self.parser_lock = threading.Lock()
        self.engine_lock = threading.Lock()
        self.setup_engine()

    def run(self):
        self.run_browser()
        self.run_engine()
        self.run_input()
        while True:
            if self.new_data is not None:

                self.parser_lock.acquire()
                if isinstance(self.new_data, Moves):
                    self.history = self.pgn_history
                else:
                    self.history = self.fen_history

                self.history.put(self.new_data)
                if self.new_data != self.last_data:
                    self.last_data = self.new_data
                    self.show()
                    self.stop_engine()
                    self.engine_lock.acquire()
                    self.new_analysis = True
                    self.engine_lock.release()

                self.new_data = None
                self.parser_lock.release()

    def on_data(self):
        while True:
            data = self.browser.get_data(self.browser.url)
            self.parser = select_parser(data)
            if self.parser is not None:
                parsed_data = self.parser.parse(data[0])
                if data != self.last_data:
                    self.parser_lock.acquire()
                    self.new_data = parsed_data
                    self.parser_lock.release()

    def on_input(self):
        while True:
            message = input()
            if message == 's':
                self.engine.stop()

    def on_stockfish(self):
        while True:
            if self.new_analysis:
                self.engine_lock.acquire()
                self.new_analysis = False
                self.engine.set_fen_position(self.history.fen)
                board = self.history.board.copy()
                white_plays = self.history.white_to_play
                en_passant = self.history.en_passant

                best_move, best_lines, scores = self.engine.get_best_lines()
                best_lines = [' '.join(self.notation.pgn(board.copy(), line.split(), white_plays, en_passant)) for line
                              in best_lines]
                best_move = self.notation.pgn(board.copy(), [best_move], white_plays, en_passant)

                self.best_move = best_move
                self.scores = scores
                self.best_lines = best_lines

                self.show()
                self.engine_lock.release()

    def run_browser(self):
        self.browser.open()
        t = threading.Thread(target=self.on_data)
        t.start()

    def run_engine(self):
        t = threading.Thread(target=self.on_stockfish)
        t.start()

    def run_input(self):
        t = threading.Thread(target=self.on_input)
        t.start()

    def stop_engine(self):
        try:
            self.engine.stop()
        except BrokenPipeError:
            self.setup_engine()

    def setup_engine(self):
        # path = 'files/stockfish_20011801_x64'
        path = 'files/lc0 --multipv={}'.format(8, self.params['MultiPV'])
        self.engine = Engine(path, depth=20, parameters=self.params)
        self.new_analysis = False
        if self.engine_lock.locked():
            self.engine_lock.release()

    def show(self):
        self.clear()
        print(self.history.board.visual)
        print(self.history.fen)
        print(self.last_data)

        if self.best_lines is not None:
            for score, line in zip(self.scores, self.best_lines):
                print("Score: {}, {}".format(score, line))
            print('Best move: ', self.best_move)

    def clear(self):
        if name == 'nt':
            _ = system('cls')

        else:
            _ = system('clear')


app = App()
app.run()
