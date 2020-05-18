from . import IParser
from chessboard import Chessboard, Pieces, Square
from game import Moves
import lxml.html as html
import re
from lxml.etree import ParserError


class ChessComMovesOnlineParser(IParser):
    @staticmethod
    def parsable(data):
        if type(data) == str:
            try:
                root = html.fromstring(data)
                elements = root.xpath(".//span[contains(@class, 'move-text-component')]")
                if len(elements) > 0:
                    return True
            except (KeyError, ParserError):
                pass
        return False

    @staticmethod
    def parse(data):

        root = html.fromstring(data)
        elements = root.xpath(".//span[contains(@class, 'move-text-component')]/text()")

        moves = list()

        for e in elements:
            e = e.strip()
            if e != '':
                moves.append(e)

        return Moves(moves)


class ChessComMovesOfflineParser(IParser):
    @staticmethod
    def parsable(data):
        if type(data) == str:
            try:
                root = html.fromstring(data)
                elements = root.xpath(".//a[contains(@class, 'gotomove')]")
                if len(elements) > 0:
                    return True
                elements = root.xpath(".//span[contains(@class, 'gotomove')]")

            except (KeyError, ParserError):
                pass
        return False

    @staticmethod
    def parse(data):

        root = html.fromstring(data)
        elements = root.xpath(".//a[contains(@class, 'gotomove')]/text()")

        moves = list()

        for e in elements:
            e = e.strip()
            if e != '':
                moves.append(e)

        return Moves(moves)


class ChessComBoardOnlineParser(IParser):

    @staticmethod
    def parsable(data):
        if type(data) == str:
            try:
                root = html.fromstring(data)
                root.get_element_by_id("game-board")
                return True
            except (KeyError, ParserError):
                pass
        return False

    @staticmethod
    def parse(data):
        def _url_to_piece(url: str):
            line = url.split('/')[-1]
            line = re.sub(r'\.\S+', '', line)
            return Pieces.get(line[1], True if line[0] == 'w' else False)

        chessboard = Chessboard()
        pattern_url = re.compile(r'url\("([^)]+)"\)')
        pattern_square = re.compile("square-(\d+)")
        root = html.fromstring(data)
        element = root.get_element_by_id("game-board")
        pieces_element = element.find_class('pieces')[0]

        squares, pieces = list(), list()

        for p in pieces_element:
            coords = pattern_square.search(p.get('class')).group(1)
            style = p.get('style')
            url = pattern_url.search(style).group(1)
            square = Square.index_to_square(int(coords[-2:]) - 1, int(coords[:2]) - 1)
            piece = _url_to_piece(url)
            squares.append(square)
            pieces.append(piece)

        chessboard.update_squares(squares, pieces)

        return chessboard


class ChessComBoardOfflineParser(IParser):

    @staticmethod
    def parsable(data):
        if type(data) == str:
            root = html.fromstring(data)
            try:
                element = root.get_element_by_id("chessboard_boardarea")
                classes = element.find_class('chess_com_piece')

                for cls in classes:
                    if 'dragging' in cls.get('class'):
                        return False
                return True
            except (KeyError, ParserError):
                pass
        return False

    @staticmethod
    def parse(data):
        def _url_to_piece(url: str):
            line = url.split('/')[-1]
            line = re.sub(r'\.\S+', '', line)
            return Pieces.get(line[1], True if line[0] == 'w' else False)

        def _get_translation(line):
            translate_match = pattern.search(line)
            if translate_match is not None:
                x = int(translate_match.group(1))
                y = int(translate_match.group(2))
                return x, y

            else:
                return -1, -1

        chessboard = Chessboard()
        pattern = re.compile(r'translate\((\d+)px,\s*(\d+)px\)')

        root = html.fromstring(data)
        element = root.get_element_by_id("chessboard_boardarea")
        classes = element.find_class('chess_com_piece')

        squares, pieces = list(), list()

        for cls in classes:
            w = int(cls.get('width'))
            h = int(cls.get('height'))
            style = cls.get('style')
            src = cls.get('src')
            x, y = _get_translation(style)
            if x == -1 or y == -1:
                return None
            row, col = 7 - y / h, x / w
            if not row.is_integer() or not col.is_integer():
                return None
            square = Square.index_to_square(int(row), int(col))
            piece = _url_to_piece(src)

            squares.append(square)
            pieces.append(piece)

        chessboard.update_squares(squares, pieces)

        return chessboard
