import math
import os
from copy import deepcopy
from itertools import chain
from collections import Counter
import model.sudoku_exceptions as ex
from model.sudoku_gen import SudokuGen
from model.sudoku_solver_bf import SudokuBF
from model.utils import str_to_tuples


class Sudoku:
    def __init__(self, inp, first_cond=False, second_cond=False):
        if isinstance(inp, SudokuGen):
            self._side, self._order, self._field, self.second_colors = \
                inp.side, inp.order, deepcopy(inp.table), inp.second_colors
        elif isinstance(inp, str):
            read_lines = list(filter(None, inp.split('\n')))
            self._side, self._order, self._field, self.second_colors = \
                self._parse(read_lines)
        elif isinstance(inp, list):
            self._side, self._order, self._field, self.second_colors = \
                self._parse(inp)
        else:
            raise ex.SudokuWrongInputError('Input cannot be parsed')

        self._check_validity()

        self.first_cond = first_cond
        if first_cond and self._order % 2 == 0:
            raise ex.SudokuWrongInputError(
                'Sudoku should have odd order to be compatible '
                'with the first condition')

        self.second_cond = second_cond
        if self.second_cond:
            if not self.second_colors:
                raise ex.SudokuWrongInputError(
                    'Cell numbers for the second condition not found')

            if len(self.second_colors) > 4:
                raise ex.SudokuWrongInputError(
                    'More than 4 colors in the second condition')
            for tup in self.second_colors:
                if not all(-1 < val < self._side**2 for val in tup):
                    raise ex.SudokuWrongInputError(
                        'Cell numbers in the second condition '
                        'are out of range')
            self.second_cond = len(self.second_colors) > 1

    @classmethod
    def get_from_file(cls, file_path, first_cond=False):
        with open(os.path.abspath(file_path), 'rt') as f:
            s = Sudoku(f.read(), first_cond)
        return s

    @staticmethod
    def _parse(read_lines):
        field = []
        length = 0
        order = 0
        values = 0
        second_colors = None
        for i, l in enumerate(read_lines):
            line = l.strip()
            if line.startswith('#'):
                st = str_to_tuples(
                    line.strip('#').strip())
                if st:
                    second_colors = st
                continue

            splitline = line.split()
            if length == 0:
                length = len(splitline)
                order = int(math.sqrt(length))
                if length != order ** 2:
                    raise ex.SudokuWrongInputError(
                        "The input Sudoku has unusual row length "
                        "(expected {0}, got {1})".format(
                            order ** 2, length))
                values = tuple(range((order ** 2) + 1))
            elif length != len(splitline):
                raise ex.SudokuWrongInputError(
                    "The input Sudoku is not valid (line {0})".format(i))

            row = []
            for j, value in enumerate(splitline):
                if value.isdigit() and int(value):
                    if int(value) not in values:
                        raise ex.SudokuWrongInputError(
                            "The input Sudoku is not valid (line {0}, "
                            "value {1} should be not bigger than {2}".format(
                                i, value, length))
                    row.append(int(value))
                else:
                    row.append(0)
            field.append(row)
        if len(field) == 1:
            raise ex.SudokuWrongInputError(
                "The input Sudoku is not valid (too small)")
        if len(field) != length:
            raise ex.SudokuWrongInputError(
                "The input Sudoku has unusual size "
                "(expected {0}x{0} or {1}x{1})".format(
                    length, len(field)))
        return length, order, field, second_colors

    def _col(self, n):
        return [r[n] for r in self._iter_row()]

    def _row(self, n):
        return self._field[n]

    def _iter_col(self):
        for k in range(self._side):
            yield self._col(k)

    def _iter_row(self):
        for k in range(self._side):
            yield self._row(k)

    def _house(self, row, col):
        house = []
        house_i = (row // self._order) * self._order
        house_j = (col // self._order) * self._order
        for i in range(house_i, house_i + self._order):
            for j in range(house_j, house_j + self._order):
                house.append(self._field[i][j])
        return house

    def _house_iter(self):
        for i in range(self._order):
            for j in range(self._order):
                yield self._house(i * self._order, j * self._order)

    @staticmethod
    def _check_no_dups(values):
        unique = set()
        for num in values:
            if num != 0 and num in unique:
                return False
            unique.add(num)
        return True

    def _check_validity(self):
        if not all(map(Sudoku._check_no_dups,
                       chain(
                           self._iter_row(),
                           self._iter_col(),
                           self._house_iter()))):
            raise ex.SudokuWrongInputError(
                'Sudoku is not valid '
                '(there are equal values in rows/cols/houses)')

    @staticmethod
    def _check_first_cond(side, field):
        cen = side // 2
        a = list(range(cen + 1)) + list(reversed(range(cen)))
        b = list(reversed(range(cen, side))) + list(range(cen + 1, side))
        v = [field[i][j] for i, j in zip(a, range(side))]
        n = [field[i][j] for i, j in zip(b, range(side))]
        c_v, c_n = Counter(v), Counter(n)
        return Sudoku._check_corner(c_v) and Sudoku._check_corner(c_n)

    @staticmethod
    def _check_corner(corner):
        common = corner.most_common(2)
        return common[0][1] == 2 and common[1][1] < 2

    @staticmethod
    def _check_second_cond(field, colors):
        side = len(field)
        sums = [sum(value) for value in
                [[Sudoku._get_cell(num, field, side) for num in tup]
                 for tup in colors]]
        return all(x == sums[0] for x in sums)

    @staticmethod
    def _get_cell(num, field, side):
        return field[num // side][num % side]

    def solve(self):
        solutions = SudokuBF(self._side, self._order, self._field).solve()
        for solution in solutions:
            if (not self.first_cond
                or self._check_first_cond(self._side, solution)) \
                    and (not self.second_cond
                         or self._check_second_cond(
                             solution, self.second_colors)):
                yield solution
