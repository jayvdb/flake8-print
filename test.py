from textwrap import dedent

from pep8 import BaseReport, Checker, StyleGuide
from flake8_print import print_usage
from nose.tools import assert_equal, assert_true


class CaptureReport(BaseReport):
    """Collect the results of the checks."""

    def __init__(self, options):
        self._results = []
        super(CaptureReport, self).__init__(options)

    def error(self, line_number, offset, text, check):
        """Store each error."""
        code = super(CaptureReport, self).error(line_number, offset,
                                                text, check)
        if code:
            record = {
                'line': line_number,
                'col': offset,
                'message': '{0} {1}'.format(code, text[5:]),
            }
            self._results.append(record)
        return code


class PrintTestStyleGuide(StyleGuide):

    logical_checks = [
        ('print_usage', print_usage, ['logical_line', 'noqa']),
    ]
    physical_checks = []
    ast_checks = []
    max_line_length = None
    hang_closing = False
    verbose = False
    benchmark_keys = {'files': 0, 'physical lines': 0, 'logical lines': 0}


_print_test_style = PrintTestStyleGuide()


def check_code_for_print_statements(code):
    """Process code using pep8 Checker and return all errors."""
    report = CaptureReport(options=_print_test_style)
    lines = [line + '\n' for line in code.split('\n')]
    checker = Checker(lines=lines, options=_print_test_style, report=report)
    checker.check_all()
    return report._results


class Flake8PrintTestCases(object):
    pass


class TestGenericCases(Flake8PrintTestCases):
    def test_skips_noqa(self):
        result = check_code_for_print_statements('print(4) # noqa')
        assert_equal(result, list())

    def test_skips_noqa_multiline(self):
        result = check_code_for_print_statements(dedent("""
            print("a"
                  "b")  # noqa
        """))
        assert_equal(result, list())

    def test_skips_noqa_inside_multiline(self):
        result = check_code_for_print_statements(dedent("""
            print("a"  # noqa
                  "b")
        """))
        assert_equal(result, list())

    def test_skips_noqa_line_only(self):
        result = check_code_for_print_statements('print(4); # noqa\nprint(5)\n# noqa')
        assert_equal(result, [{'col': 0, 'line': 2, 'message': 'T001 print function found.'}])

    def test_catches_multiline_print(self):
        result = check_code_for_print_statements(dedent("""
            print("a"
                  "b")
        """))
        assert_equal(result, [{'col': 0, 'line': 2, 'message': 'T001 print function found.'}])

    def test_catches_simple_print_python2(self):
        result = check_code_for_print_statements('print 4')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': 'T001 print statement found.'}])

    def test_catches_simple_print_python3(self):
        result = check_code_for_print_statements('print(4)')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': 'T001 print function found.'}])

    def test_print_invocation_in_lambda(self):
        result = check_code_for_print_statements('x = lambda a: print(a)')
        assert_equal(result, [{'col': 14, 'line': 1, 'message': 'T001 print function found.'}])


class TestComments(Flake8PrintTestCases):
    def test_print_in_inline_comment_is_not_a_false_positive(self):
        result = check_code_for_print_statements('# what should I print ?')
        assert_equal(result, list())

    def test_print_same_line_as_comment(self):
        result = check_code_for_print_statements('print(5) # what should I do with 5 ?')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': 'T001 print function found.'}])


class TestSingleQuotes(Flake8PrintTestCases):
    def test_print_in_one_single_quote_single_line_string_not_false_positive(self):
        result = check_code_for_print_statements('a(\'print the things\', 25)')
        assert_equal(result, list())

    def test_print_in_three_single_quote_single_line_string_not_false_positive(self):
        result = check_code_for_print_statements('a(\'\'\'print the things\'\'\', 25)')
        assert_equal(result, list())


class TestDoubleQuotes(Flake8PrintTestCases):
    def test_print_in_one_double_quote_single_line_string_not_false_positive(self):
        result = check_code_for_print_statements('a("print the things", 25)')
        assert_equal(result, list())

    def test_print_in_three_double_quote_single_line_string_not_false_positive(self):
        result = check_code_for_print_statements('a("""print the things""", 25)')
        assert_equal(result, list())


class TestMultilineFalsePositive(Flake8PrintTestCases):
    def test_print_in_one_double_quote_single_line_string_not_false_positive(self):
        result = check_code_for_print_statements('hello="""there is a \nprint on\n the next line"""')
        assert_equal(result, list())

    def test_print_in_three_double_quote_single_line_string_not_false_positive(self):
        result = check_code_for_print_statements('a("""print the things""", 25)')
        assert_equal(result, list())


class TestPython3NameFalsePositive(Flake8PrintTestCases):
    def test_redefine_print_function(self):
        result = check_code_for_print_statements('def print(): pass')
        assert_equal(result, [{'col': 4, 'line': 1, 'message': 'T101 Python 2.x reserved word print used.'}])

    def test_print_method(self):
        result = check_code_for_print_statements('class Foo: def print(self): pass')
        assert_equal(result, [{'col': 15, 'line': 1, 'message': 'T101 Python 2.x reserved word print used.'}])

    def test_print_arg(self):
        result = check_code_for_print_statements('def foo(print): pass')
        assert_equal(result, [{'col': 8, 'line': 1, 'message': 'T101 Python 2.x reserved word print used.'}])

    def test_print_assignment(self):
        result = check_code_for_print_statements('print = 1')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': 'T101 Python 2.x reserved word print used.'}])

    def test_print_assignment_value(self):
        result = check_code_for_print_statements('x = print')
        assert_equal(result, [{'col': 4, 'line': 1, 'message': 'T101 Python 2.x reserved word print used.'}])

    def test_print_assignment_value_or(self):
        result = check_code_for_print_statements('x = print or 1')
        assert_equal(result, [{'col': 4, 'line': 1, 'message': 'T101 Python 2.x reserved word print used.'}])

    def test_print_assignment_value_else(self):
        result = check_code_for_print_statements('x = print if True else 1')
        assert_equal(result, [{'col': 4, 'line': 1, 'message': 'T101 Python 2.x reserved word print used.'}])

    def test_print_in_lambda(self):
        result = check_code_for_print_statements('x = lambda a: print')
        assert_equal(result, [{'col': 14, 'line': 1, 'message': 'T101 Python 2.x reserved word print used.'}])
