from copy import deepcopy
from itertools import product


class SudokuBF:
    def __init__(self, side, order, field):
        self._side, self._order, self._field = \
            side, order, field

        self.X = {}
        self.Y = {}

    def solve(self):
        self._set_dicts()

        for i, row in enumerate(self._field):
            for j, n in enumerate(row):
                if n:
                    self._select((i, j, n))

        for solution in self._solve():
            field = deepcopy(self._field)
            for (r, c, n) in solution:
                field[r][c] = n
            yield field

    def _set_dicts(self):
        temp = ([("rc", rc) for rc in product(range(self._side), repeat=2)] +
                [("rn", rn) for rn in product(range(self._side),
                                              range(1, self._side + 1))] +
                [("cn", cn) for cn in product(range(self._side),
                                              range(1, self._side + 1))] +
                [("hn", bn) for bn in product(range(self._side),
                                              range(1, self._side + 1))])

        for row, column, num in product(range(self._side),
                                        range(self._side),
                                        range(1, self._side + 1)):
            house = (row // self._order) * \
                self._order + (column // self._order)
            self.Y[(row, column, num)] = [
                ("rc", (row, column)),
                ("rn", (row, num)),
                ("cn", (column, num)),
                ("hn", (house, num))]

        self.X = {_: set() for _ in temp}
        for value_guess, corresponding_pos in self.Y.items():
            for pos in corresponding_pos:
                self.X[pos].add(value_guess)

    def _solve(self, solution=list()):
        if not self.X:
            yield list(solution)
        else:
            c = min(self.X, key=lambda x: len(self.X[x]))
            for r in list(self.X[c]):
                solution.append(r)
                cols = self._select(r)
                for s in self._solve(solution):
                    yield s
                self._deselect(r, cols)
                solution.pop()

    def _select(self, r):
        cols = []
        for j in self.Y[r]:
            # удаляем из X все записи о соответствующей ячейке,
            # так как она считается заполненой
            for i in self.X[j]:
                for k in self.Y[i]:
                    if k != j:
                        self.X[k].remove(i)
            cols.append(self.X.pop(j))
        return cols

    def _deselect(self, r, cols):
        # возвращаем в Х записи о соответствующей ячейке,
        # так как считаем, что выбор неправильный
        for j in reversed(self.Y[r]):
            self.X[j] = cols.pop()
            for i in self.X[j]:
                for k in self.Y[i]:
                    if k != j:
                        self.X[k].add(i)
