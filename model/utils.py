import re

reg = re.compile(
    r'(\d+(?:,\d+)*)_?(\d+(?:,\d+)*)?_?(\d+(?:,\d+)*)?_?(\d+(?:,\d+)*)?')


def str_to_tuples(s):
    if not s or s.isspace():
        return (-1,),
    r = reg.match(s)
    if not r:
        return None
    t = [x for x in r.groups() if x is not None]
    res = tuple(map(lambda x: tuple(map(int, x.split(','))), t))
    # t = tuple(s.split('_'))
    # res = tuple(map(lambda x: tuple(map(int, x.split(','))), t))
    return res


def tuples_to_str(t):
    res = ''
    for tup in t:
        for n in tup:
            res += '{},'.format(n)
        res = res[:-1] + '_'
    return res[:-1]
