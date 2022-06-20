from pathlib import Path
import yaml

from dateutil.relativedelta import relativedelta

from .core import test_fcn

from autofiler.file import File
from autofiler.filters import *
from autofiler.filters import _false_filter, _true_filter # leading underscore -> needs explicit import

p = Path(__file__).parent / Path('test_file.yaml')
f = File(**yaml.safe_load(p.open()).get('file').insert)

true_filter = test_fcn('filter.true', True, _true_filter())
false_filter = test_fcn('filter.false', False, _false_filter())
name_full_match = test_fcn('name.full_match', True, name_filter(r'test.*'), f)
name_partial_match = test_fcn('name.partial_match', False, name_filter(r'test'), f)

def run_tests():
    # Load test file
    p = Path(__file__).parent / Path('test_file.yaml')
    f = File(**yaml.load(p.open(), Loader=yaml.Loader)['file'])

    def test(name, fltr, expect, *args, **kwargs):
        fltr = fltr(*args, **kwargs)
        result = "OK" if fltr(f) == expect else "FAIL"
        print(f"{name:.<40}{result}")
    
    test('Baseline 1', _true_filter, True)
    test('Baseline 2', _false_filter, False)
    test('Name Filter Full Match', name_filter, True, r'test.*')
    test('Name Filter Part. Match', name_filter, False, r'test')
    test('Name Filter No Match', name_filter, False, r'dhd')
    test('Name Filter Univ Match', name_filter, True, r'.*')
    test('Age Filter Max 1', age_filter, True, max=relativedelta(years=1))
    test('Age Filter Max 2', age_filter, False, max=relativedelta(days=1))
    test('Age Filter Min 1', age_filter, True, min=relativedelta(days=1))
    test('Age Filter Min 2', age_filter, False, min=relativedelta(years=1))
    test('Age Filter Range 1', age_filter, False, min=relativedelta(days=1), max=relativedelta(months=1))
    test('Age Filter Range 2', age_filter, True, min=relativedelta(days=1), max=relativedelta(years=1))
    test('Age Filter Range 3', age_filter, False, min=relativedelta(months=11), max=relativedelta(years=1))
    test('File Type 1', type_filter, True, 'txt')
    test('File Type 2', type_filter, False, 'twxt')
    test('File Type 3', type_filter, False, 'txt.log')
    test('Size Range 1', size_filter, True, sz_min=102546, sz_max=985476)
    test('Size Range 2', size_filter, False, sz_min=102546, sz_max=254756)
    test('Size Range 3', size_filter, False, sz_min=785964, sz_max=985476)
    test('Or Filter 1', or_filter, False, _false_filter(), _false_filter())
    test('Or Filter 2', or_filter, True, _true_filter(), _false_filter())
    test('Or Filter 3', or_filter, True, _false_filter(), _true_filter())
    test('Or Filter 4', or_filter, True, _true_filter(), _true_filter())
    test('Exclusive Or Filter 1', xor_filter, False, _false_filter(), _false_filter())
    test('Exclusive Or Filter 2', xor_filter, True, _true_filter(), _false_filter())
    test('Exclusive Or Filter 3', xor_filter, True, _false_filter(), _true_filter())
    test('Exclusive Or Filter 4', xor_filter, False, _true_filter(), _true_filter())
    test('And Filter 1', and_filter, False, _false_filter(), _false_filter())
    test('And Filter 2', and_filter, False, _true_filter(), _false_filter())
    test('And Filter 3', and_filter, False, _false_filter(), _true_filter())
    test('And Filter 4', and_filter, True, _true_filter(), _true_filter())


if __name__ == "__main__":
    print(name_partial_match())