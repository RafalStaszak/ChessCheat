from . import ChessComBoardOnlineParser, ChessComBoardOfflineParser, ChessComMovesOnlineParser, ChessComMovesOfflineParser


def select_parser(data: list):
    for d in data:
        if ChessComMovesOnlineParser.parsable(d):
            return ChessComMovesOnlineParser

        if ChessComMovesOfflineParser.parsable(d):
            return ChessComMovesOfflineParser

    return None
