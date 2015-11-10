"""Extension for flake8 that finds usage of print."""
import re

__version__ = '2.0.0'

PRINT_ERROR_CODE = 'T001'
PRINT_ERROR_MESSAGE = 'print statement found.'


def flake8ext(f):
    """Decorate flake8 extension function."""
    f.name = 'flake8-print'
    f.version = __version__
    return f


RE_PRINT_STATEMENT = re.compile(r"(?<![=\s])\s*print\s+[^(=]", re.MULTILINE)
RE_PRINT_FUNCTION = re.compile(r"(?<!def\s)print\s*\([^)]*\)", re.MULTILINE)

@flake8ext
def print_usage(logical_line, noqa=None):
    if noqa:
        return
    m = RE_PRINT_STATEMENT.search(logical_line)
    if m:
        yield m.start(), '{0} {1}'.format(
            PRINT_ERROR_CODE, PRINT_ERROR_MESSAGE)
        return

    m = RE_PRINT_FUNCTION.search(logical_line)
    if m:
        yield m.start(), '{0} {1}'.format(
            PRINT_ERROR_CODE, 'print function found.')
        return

    pos = logical_line.find('print')
    if pos != -1:
        yield pos, 'T101 Python 2.x reserved word print used.'
