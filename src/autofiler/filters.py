from datetime import datetime
import re

from dateutil.relativedelta import relativedelta

from .helpers import assert_type
from .file import File

class filter:
    def __or__(self, other):
        try:
            assert_type(other, filter)
        except AssertionError:
            raise NotImplementedError
        return or_filter(self, other)
    
    def __xor__(self, other):
        try:
            assert_type(other, filter)
        except AssertionError:
            raise NotImplementedError
        return xor_filter(self, other)
    
    def __and__(self, other):
        try:
            assert_type(other, filter)
        except AssertionError:
            raise NotImplementedError
        return and_filter(self, other)

class _true_filter(filter):
    def __call__(self, file):
        return True

class _false_filter(filter):
    def __call__(self, file):
        return False

class comp_filter(filter):
    def __init__(self, *filters):
        for fltr in filters:
            assert_type(fltr, filter)
        self.filters = filters

class or_filter(comp_filter):
    def __call__(self, file):
        return any([f(file) for f in self.filters])

class and_filter(comp_filter):
    def __call__(self, file):
        return all([f(file) for f in self.filters])

class xor_filter(comp_filter):
    def __call__(self, file):
        return len([f for f in self.filters if f(file)]) == 1

class not_filter(comp_filter):
    def __call__(self, file):
        return not self.filters[0](file)

class name_filter(filter):
    def __init__(self, pattern):
        assert_type(pattern, str)
        self.pattern = re.compile(pattern)
    
    def __call__(self, file):
        assert_type(file, File)
        return bool(self.pattern.fullmatch(file.name))

class age_filter(filter):
    def __init__(self, equals=None, min=None, max=None):
        if equals != None:
            assert_type(equals, relativedelta)
        if min != None:
            assert_type(min, relativedelta)
        if max != None:
            assert_type(max, relativedelta)
        self.equals = equals
        self.min = min
        self.max = max
    
    def __call__(self, file):
        assert_type(file, File)
        now = datetime.now()
        if self.max and file.date_created + self.max < now:
            return False
        if self.min and file.date_created + self.min > now:
            return False
        if self.equals and self.equals != relativedelta(now, file.date_created):
            return False
        return True

class created_filter(filter):
    def __init__(self, equals=None, min=None, max=None):
        if equals != None:
            assert_type(equals, datetime)
        if min != None:
            assert_type(min, datetime)
        if max != None:
            assert_type(max, datetime)
        self.equals = equals
        self.min = min
        self.max = max
    
    def __call__(self, file):
        assert_type(file, File)
        if self.max and file.date_created > self.max:
            return False
        if self.min and file.date_created < self.min:
            return False
        if self.equals and self.equals != file.date_created:
            return False
        return True

class modified_filter(filter):
    def __init__(self, equals=None, min=None, max=None):
        if equals != None:
            assert_type(equals, datetime)
        if min != None:
            assert_type(min, datetime)
        if max != None:
            assert_type(max, datetime)
        self.equals = equals
        self.min = min
        self.max = max
    
    def __call__(self, file):
        assert_type(file, File)
        if self.max and file.date_modified > self.max:
            return False
        if self.min and file.date_modified < self.min:
            return False
        if self.equals and self.equals != file.date_modified:
            return False
        return True
    
class size_filter(filter):
    def __init__(self, equals=None, min=None, max=None):
        if equals != None:
            assert_type(equals, int)
        if min != None:
            assert_type(min, int)
        if max!= None:
            assert_type(max, int)
        self.equals = equals
        self.min = min
        self.max = max
    
    def __call__(self, file):
        assert_type(file, File)
        if self.min and file.size < self.min:
            return False
        if self.max and file.size > self.max:
            return False
        if self.equals and file.size != self.equals:
            return False
        return True

class type_filter(filter):
    def __init__(self, *types):
        for t in types:
            assert_type(t, str)
        self.types = [t.lower() for t in types]
    
    def __call__(self, file):
        assert_type(file, File)
        return file.ftype in self.types