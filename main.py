from browser import Browser
from game import FenGame, PgnGame, Game, Moves
from rules import Rules
from chessboard import Chessboard, Square, Pieces
from stockfish import Stockfish, DEFAULT_STOCKFISH_PARAMS
import time
import threading
from parsing import select_parser
from notation import AlgebraicNotation


class App:
    def __init__(self):
        self.browser = Browser()
        self.parser = None

        self.history = None
        self.fen_history = FenGame()
        self.pgn_history = PgnGame()
        self.notation = AlgebraicNotation()

        self.params = DEFAULT_STOCKFISH_PARAMS
        self.params['MultiPV'] = 3

        self.engine = None
        self.new_data = None
        self.last_data = None

        self.best_move = None
        self.best_lines = None
        self.scores = None

        self.new_analysis = False

        self.parser_lock = threading.Lock()
        self.stockfish_lock = threading.Lock()
        self.setup_stockfish()

    def run(self):
        self.run_browser()
        self.run_stockfish()
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
                    print(self.history.board.visual)
                    print(self.history.fen)
                    print(self.last_data)
                    self.stop_stockfish()
                    self.stockfish_lock.acquire()
                    self.new_analysis = True
                    self.stockfish_lock.release()

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

    def on_stockfish(self):
        while True:
            if self.new_analysis:
                self.stockfish_lock.acquire()
                self.new_analysis = False
                self.engine.set_fen_position(self.history.fen)
                board = self.history.board.copy()
                white_plays = self.history.white_to_play
                en_passant = self.history.en_passant

                best_move, best_lines, scores = self.engine.get_best_lines()
                best_lines = [' '.join(self.notation.pgn(board.copy(), line.split(), white_plays, en_passant)) for line
                              in best_lines]
                best_move = self.notation.pgn(board.copy(), [best_move], white_plays, en_passant)

                self.show_lines(best_move, best_lines, scores)
                self.stockfish_lock.release()

    def run_browser(self):
        self.browser.open()
        t = threading.Thread(target=self.on_data)
        t.start()

    def run_stockfish(self):
        t = threading.Thread(target=self.on_stockfish)
        t.start()

    def stop_stockfish(self):
        try:
            self.engine.stop()
        except BrokenPipeError:
            self.setup_stockfish()

    def setup_stockfish(self):
        self.engine = Stockfish('files/stockfish_20011801_x64', depth=15, parameters=self.params)
        self.new_analysis = False
        if self.stockfish_lock.locked():
            self.stockfish_lock.release()

    def show_lines(self, best_move, best_lines, scores):
        print(best_move)
        for score, line in zip(scores, best_lines):
            print("Score: {}, {}".format(score, line))
        print('Best move: ', best_move)


app = App()
app.run()
