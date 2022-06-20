class test_fcn:
    def __init__(self, title, expected, fcn, *args, **kwargs):
        self.title = title
        if type(expected) != list:
            expected = [expected]
        self.expected = expected
        self.fcn = lambda: fcn(*args, **kwargs)
    
    def __call__(self):
        try:
            result = self.fcn()
            return result in self.expected
        except Exception as e:
            return type(e) in self.expected
