import argparse
import sys
from itertools import islice
from model.sudoku_solver import Sudoku, SudokuGen
from model.utils import str_to_tuples, tuples_to_str
import model.sudoku_exceptions as ex


def main():
    parser = argparse.ArgumentParser(
        prog='sudoku',
        description='This program can solve and generate Sudoku ',
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(
        title='Commands',
        metavar='s|g',
        description='Solve or Generate a Sudoku',
        help='For using this program in solving mode use "s"\n'
             'For using this program in generator mode use "g"\n\n'
             'Use --help for each mode to see more'
    )
    parser_solver = subparsers.add_parser('s')
    solver_params = parser_solver.add_argument_group(title='Parameters')
    solver_params.add_argument(
        '-n', '--solution-number',
        type=int,
        default=1,
        help='Number of solutions to find and print '
             '(-1 to show all solutions)',
        metavar='NUM'
    )
    solver_params.add_argument(
        '-f', '--first',
        action='store_true',
        help='Find solutions that matches the first condition'
    )
    solver_params.add_argument(
        '-s', '--second',
        help="""Find solutions that matches the second condition,
        cell numbers must be stated like this: # 3,45,10_4,70_11,69,80""",
        action='store_true'
    )
    solver_params.add_argument(
        'filename',
        nargs='?',
        type=argparse.FileType(),
        help='File with unsolved Sudoku '
             '(if not stated, solve a Sudoku from stdin)'
    )
    parser_generator = subparsers.add_parser('g')
    generator_params = parser_generator.add_argument_group(title='Parameters')
    generator_params.add_argument(
        '-p', '--print-solution',
        action='store_true',
        help='Print one solution of a generated Sudoku'
    )
    generator_params.add_argument(
        '-f', '--first',
        action='store_true',
        help='Generate a Sudoku with at least one solution '
             'that matches the first condition'
    )
    generator_params.add_argument(
        '-s', '--second',
        help="""Numbers of cells with the same color.
        Will generate random numbers if CELLS are not stated.
        Example: 3,45,10_4,70_11,69,80""",
        action='store_true'
    )
    generator_params.add_argument(
        'size',
        type=int,
        help="Size of a Sudoku to generate\n"
             "(will be SIZE^2 x SIZE^2, cannot be less than 2)",
        metavar='SIZE'
    )
    generator_params.add_argument(
        'percent',
        type=int,
        help='How much of a Sudoku will be filled',
        metavar='PERCENT'
    )
    generator_params.add_argument(
        'filepath',
        nargs='?',
        type=argparse.FileType('w'),
        help='Use to store generated field to a file'
             '(creates one if not exists)'
    )

    args = parser.parse_args()
    if 'size' not in args:
        num = args.solution_number
        f_rule = args.first
        s_rule = args.second
        file = args.filename
        num = None if num == -1 else num
        try:
            if file:
                sudoku = Sudoku(file.read(), f_rule, s_rule).solve()
            else:
                print('Please enter Sudoku:')
                inp = sys.stdin.readlines()
                sudoku = Sudoku(inp, f_rule, s_rule).solve()
            any_sols = False
            for i, sol in enumerate(islice(sudoku, num)):
                any_sols = True
                print('Solution {}:'.format(i + 1))
                print(p_sol(sol))
            if not any_sols:
                print('No solutions')
        except ex.SudokuException as e:
            print(e, file=sys.stderr)
            sys.exit(1)

    if 'solution_number' not in args:
        p_gen_sol = args.print_solution
        f_rule = args.first
        s_rule = None
        if args.second:
            try:
                s_rule = str_to_tuples(
                    input('Enter numbers of cells with the same color. '
                          'Example: 3,45,10_4,70_11,69,80: \n'))
            except ValueError:
                print('Wrong argument. Example: 1,2,3_45,69_56,11,13',
                      file=sys.stderr)
                sys.exit(2)
        size = args.size
        percent = args.percent
        file = args.filepath

        try:
            gen = SudokuGen(size, percent, f_rule, s_rule)
        except ex.SudokuGeneratorError as e:
            print(e, file=sys.stderr)
            sys.exit(2)
        to_print = p_sol(gen.table)
        if gen.second_colors:
            to_print += '# ' + tuples_to_str(gen.second_colors) + '\n'
        if file:
            file.write(to_print)
        else:
            print(to_print)
        if p_gen_sol:
            print(p_sol(gen.ref_table))


def p_sol(sol):
    max_size = len(str(len(sol))) + 2
    sudoku = ''
    for row in sol:
        for v in row:
            sudoku += '{0:{1}}'.format(v, max_size)
        sudoku += '\n'
    return sudoku


if __name__ == "__main__":
    main()
