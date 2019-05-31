class SudokuException(Exception):
    pass


class SudokuWrongInputError(SudokuException):
    pass


class SudokuGeneratorError(SudokuException):
    pass
