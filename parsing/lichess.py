from . import IParser
from chessboard import Chessboard, Pieces, Square
from game import Moves
import lxml.html as html
import re
from lxml.etree import ParserError


class LichessParser(IParser):
    @staticmethod
    def parsable(data):
        if type(data) == str:
            try:
                root = html.fromstring(data)
                elements = root.xpath(r'//div[@class="moves"]/m2/text()')
                if len(elements) > 0:
                    return True
            except (KeyError, ParserError):
                pass
        return False

    @staticmethod
    def parse(data):

        root = html.fromstring(data)
        elements = root.xpath(r'//div[@class="moves"]/m2/text()')

        moves = list()

        for e in elements:
            e = e.strip()
            if e != '':
                moves.append(e)

        return Moves(moves)
