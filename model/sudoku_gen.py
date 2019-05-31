from random import randrange
from copy import deepcopy
from collections import Counter
from model.sudoku_exceptions import SudokuGeneratorError


class SudokuGen:
    def __init__(self, order=3, percent=30,
                 first_cond=False, second_colors=None):
        if order < 2:
            raise SudokuGeneratorError(
                'Size cannot be less than 2')
        self.order = order
        self.side = order ** 2
        self.percent = percent

        if first_cond and self.order % 2 == 0:
            raise SudokuGeneratorError('Sudoku should have odd size to be '
                                       'compatible with the first condition')
        self.first_cond = first_cond

        if second_colors:
            if len(second_colors) > 4:
                raise SudokuGeneratorError(
                    'More than 4 colors in the second condition')
            if second_colors == ((-1, ),):
                second_colors = tuple(
                    [tuple(n) for n in [[randrange(self.side**2)
                                         for _ in range(randrange(1, 5))]
                                        for _ in range(randrange(2, 5))]])
            else:
                for tup in second_colors:
                    if not all(-1 < val < self.side**2 for val in tup):
                        raise SudokuGeneratorError(
                            'Cell numbers in the second condition '
                            'are out of range')
            self.second_cond = len(second_colors) > 1
        else:
            self.second_cond = False
        self.second_colors = second_colors

        self.table = [[((i * order + i // order + j) % self.side + 1)
                       for j in range(self.side)]
                      for i in range(self.side)]
        self._mix()
        self.ref_table = deepcopy(self.table)
        self._create()

    def _transpose(self):
        self.table = list(map(list, zip(*self.table)))

    def _swap_rows_in_house(self):
        area = randrange(self.order)
        line1 = randrange(self.order)
        line2 = randrange(self.order)
        while line1 == line2:
            line2 = randrange(self.order)

        n1 = area * self.order + line1
        n2 = area * self.order + line2
        self.table[n1], self.table[n2] = self.table[n2], self.table[n1]

    def _swap_columns_in_house(self):
        self._transpose()
        self._swap_rows_in_house()
        self._transpose()

    def _swap_rows_houses(self):
        house1 = randrange(self.order)
        house2 = randrange(self.order)
        while house1 == house2:
            house2 = randrange(self.order)

        for i in range(self.order):
            n1, n2 = house1 * self.order + i, house2 * self.order + i
            self.table[n1], self.table[n2] = self.table[n2], self.table[n1]

    def _swap_columns_area(self):
        SudokuGen._transpose(self)
        SudokuGen._swap_rows_houses(self)
        SudokuGen._transpose(self)

    def _check_v_n(self):
        cen = self.side // 2
        a = list(range(cen + 1)) + list(reversed(range(cen)))
        b = list(reversed(range(cen, self.side))) + \
            list(range(cen + 1, self.side))
        v = [self.table[i][j] for i, j in zip(a, range(self.side))]
        n = [self.table[i][j] for i, j in zip(b, range(self.side))]
        c_v = Counter(v)
        c_n = Counter(n)
        return self._check_corner(c_v) and self._check_corner(c_n)

    @staticmethod
    def _check_corner(corner):
        common = corner.most_common(2)
        return common[0][1] == 2 and common[1][1] < 2

    def _check_second_cond(self):
        side = len(self.table)
        sums = [sum(value) for value in
                [[SudokuGen._get_cell(num, self.table, side) for num in tup]
                 for tup in self.second_colors]]
        return all(x == sums[0] for x in sums)

    @staticmethod
    def _get_cell(num, field, side):
        return field[num // side][num % side]

    def _mix(self):
        mix_func = [self._transpose, self._swap_rows_in_house,
                    self._swap_columns_in_house, self._swap_rows_houses,
                    self._swap_columns_area]
        for i in range(100):
            id_func = randrange(len(mix_func))
            mix_func[id_func]()
        while not ((not self.first_cond or self._check_v_n())
                   and (not self.second_cond or self._check_second_cond())):
            id_func = randrange(len(mix_func))
            mix_func[id_func]()

    def _create(self):
        num = self.side * self.side
        i = round(num / 100 * (100 - self.percent))
        for _ in range(i):
            a, b = randrange(self.side), randrange(self.side)
            while self.table[a][b] == 0:
                a, b = randrange(self.side), randrange(self.side)
            self.table[a][b] = 0
