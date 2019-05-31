import model.sudoku_exceptions as ex


class SudokuSimple:
    def __init__(self, side, order, values, field):
        self._side, self._order, self._values, self._field = \
            side, order, values, field

        self._poss_rows = {}
        self._poss_cols = {}
        self._poss_house = {}
        self._possibles = {}

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

    def solve(self):
        while not self._is_solved():
            self._update()
            singles_found = False or self._find_naked_singles() or \
                self._find_hidden_singles()
            if not singles_found:
                raise ex.SudokuNoSolutionError(
                    "The Sudoku cannot be solved (no singles found)")
        yield self._field

    def _set_cell(self, i, j, value):
        bool_tests = [
            value in self._possibles[i][j],
            value in self._poss_rows[i],
            value in self._poss_cols[j],
            value in self._poss_house[(i // self._order) * self._order +
                                      (j // self._order)],
            value not in self._row(i),
            value not in self._col(j),
            value not in self._house(i, j)
        ]
        if all(bool_tests):
            self._field[i][j] = value
        else:
            raise ex.SudokuNoSolutionError(
                "Value {0} cannot be set in ({1}, {2})".format(
                    value, i, j))

    def _is_solved(self):
        return all([(0 not in row) for row in self._iter_row()])

    def _update(self):
        for i, (row, col, house) in enumerate(
                zip(self._iter_row(), self._iter_col(), self._house_iter())):
            self._poss_rows[i] = set(self._values).difference(set(row))
            self._poss_cols[i] = set(self._values).difference(set(col))
            self._poss_house[i] = set(self._values).difference(set(house))

        for i in range(self._side):
            self._possibles[i] = {}
            for j in range(self._side):
                self._possibles[i][j] = set()
                if self._field[i][j] > 0:
                    continue
                this_house_index = ((i // self._order) *
                                    self._order) + (j // self._order)
                self._possibles[i][j] = self._poss_rows[i].intersection(
                    self._poss_cols[j]).intersection(
                    self._poss_house[this_house_index])

    def _find_naked_singles(self):
        simple_found = False
        for i in range(self._side):
            for j in range(self._side):
                if self._field[i][j] > 0:
                    continue
                p = self._possibles[i][j]
                if len(p) == 1:
                    self._set_cell(i, j, list(p)[0])
                    simple_found = True
                elif len(p) == 0:
                    raise ex.SudokuNoSolutionError(
                        "The Sudoku cannot be solved "
                        "(no possible value for ({0},{1}))".format(
                            i, j))
        return simple_found

    def _find_hidden_singles(self):
        for i in range(self._side):
            house_i = (i // self._order) * self._order
            for j in range(self._side):
                house_j = (j // self._order) * self._order
                if self._field[i][j] > 0:
                    continue

                # rows
                p = self._possibles[i][j]
                for c in range(self._side):
                    if c == j:
                        continue
                    p = p.difference(self._possibles[i][c])
                if len(p) == 1:
                    self._set_cell(i, j, p.pop())
                    return True

                # columns
                p = self._possibles[i][j]
                for r in range(self._side):
                    if r == i:
                        continue
                    p = p.difference(self._possibles[r][j])
                if len(p) == 1:
                    self._set_cell(i, j, p.pop())
                    return True

                # house
                p = self._possibles[i][j]
                for rr in range(house_i, house_i + self._order):
                    for cc in range(house_j, house_j + self._order):
                        if rr == i and cc == j:
                            continue
                        p = p.difference(self._possibles[rr][cc])
                if len(p) == 1:
                    self._set_cell(i, j, p.pop())
                    return True

        return False
