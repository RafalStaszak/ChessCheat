class IParser:

    @staticmethod
    def parsable(data):
        raise NotImplementedError

    @staticmethod
    def parse(data):
        raise NotImplementedError

