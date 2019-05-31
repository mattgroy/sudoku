import os
import sys
import pytest
from itertools import islice

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from model.sudoku_solver import Sudoku
from model.sudoku_exceptions import SudokuWrongInputError
from model.sudoku_gen import SudokuGen
from model.utils import str_to_tuples, tuples_to_str

_test_dir = os.path.dirname(os.path.abspath(__file__))


def test_str_to_tuples():
    assert str_to_tuples('1,2_23_56,65') == ((1, 2), (23,), (56, 65))
    assert str_to_tuples('') == ((-1,),)


def test_str_to_tuples_missing():
    assert str_to_tuples('1,2__23,3') == ((1, 2), (23, 3))


def test_str_to_tuples_wrong():
    assert str_to_tuples('_1,2_3,4') is None
    assert str_to_tuples('1,2_3,4_5,6_7,8_9,10_11,12') == \
        ((1, 2), (3, 4), (5, 6), (7, 8))


def test_tuples_to_str():
    assert tuples_to_str(((1, 2), (23,), (56, 65))) == '1,2_23_56,65'


def test_solve_easy_sudoku():
    s = Sudoku.get_from_file(os.path.join(_test_dir, 'easy.txt')).solve()
    correct_solution = Sudoku.get_from_file(
        os.path.join(_test_dir, 'easy_sol.txt')).solve()
    a = list(s)
    b = list(correct_solution)
    assert a == b


def test_solve_easy_sudoku_multiple_solutions():
    s = Sudoku.get_from_file(
        os.path.join(_test_dir, 'easy_multiple.txt')).solve()
    a = list(s)
    assert len(a) == 2


def test_solve_medium_sudoku():
    s = Sudoku.get_from_file(os.path.join(_test_dir, 'medium.txt')).solve()
    correct_solution = Sudoku.get_from_file(
        os.path.join(_test_dir, 'medium_sol.txt')).solve()
    a = list(s)
    b = list(correct_solution)
    assert a == b


def test_solve_hard_sudoku():
    s = Sudoku.get_from_file(os.path.join(_test_dir, 'hard.txt')).solve()
    correct_solution = Sudoku.get_from_file(
        os.path.join(_test_dir, 'hard_sol.txt')).solve()
    assert list(s) == list(correct_solution)


def test_solve_very_hard():
    s = Sudoku.get_from_file(os.path.join(_test_dir, 'very_hard.txt')).solve()
    correct_solution = Sudoku.get_from_file(
        os.path.join(_test_dir, 'very_hard_sol.txt')).solve()
    assert list(s) == list(correct_solution)


def test_4x4_sudoku():
    s = Sudoku.get_from_file(os.path.join(_test_dir, '4x4.txt')).solve()
    correct_solution = Sudoku.get_from_file(
        os.path.join(_test_dir, '4x4_sol.txt')).solve()
    assert list(s) == list(correct_solution)


def test_16x16_sudoku():
    s = Sudoku.get_from_file(os.path.join(_test_dir, '16x16.txt')).solve()
    correct_solution = Sudoku.get_from_file(
        os.path.join(_test_dir, '16x16_sol.txt')).solve()
    assert list(s) == list(correct_solution)


def test_unsolvable_value_not_fit():
    with pytest.raises(SudokuWrongInputError):
        s = Sudoku.get_from_file(os.path.join(
            _test_dir,
            'invalid_input.txt')).solve()


def test_invalid_input_1():
    with pytest.raises(SudokuWrongInputError):
        s = Sudoku.get_from_file(
            os.path.join(
                _test_dir,
                'invalid_input2.txt')).solve()


def test_invalid_input_2():
    with pytest.raises(SudokuWrongInputError):
        s = Sudoku("# 1x1 sudoku\n yeah ").solve()


def test_invalid_input_3():
    with pytest.raises(SudokuWrongInputError):
        s = Sudoku("# 2x2 sudoku\n"
                   "l 2\n"
                   "1 o\n").solve()


def test_invalid_input_4():
    with pytest.raises(SudokuWrongInputError):
        s = Sudoku("# 9x3 sudoku\n"
                   "1 2 3 4 5 6 7 8 9\n"
                   "o l g 1 3 r d 6 9\n"
                   "o ' d i m m g 0 d").solve()


def test_solve_generated():
    gen = SudokuGen(3, 35)
    s = Sudoku(gen).solve()
    assert gen.ref_table in list(s)


def test_solve_generated_first_cond():
    gen = SudokuGen(3, 35, True)
    s = Sudoku(gen, True).solve()
    assert gen.ref_table in list(s)


def test_solve_generated_second_cond_random():
    t = ((-1,),)
    gen = SudokuGen(3, 40, False, t)
    s = Sudoku(gen, False, True).solve()
    s = list(s)
    assert any(gen.ref_table == sol for sol in s)


def test_solve_generated_second_cond():
    t = ((1, 2), (0, 3, 4))
    gen = SudokuGen(3, 40, False, t)
    s = Sudoku(gen, False, True).solve()
    assert any(gen.ref_table == sol for sol in s)


def test_solve_dont_show_same():
    gen = SudokuGen(3, 30)
    s = Sudoku(gen).solve()
    first_15 = list(islice(s, 15))
    seen = []
    assert not any(i in seen or seen.append(i) for i in first_15)


if __name__ == '__main__':
    pytest.main()
