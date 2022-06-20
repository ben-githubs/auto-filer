from collections.abc import Iterable
from pathlib import Path

def assert_type(obj, dtype):
    # If the argument is actually a list/set of types, check them all.
    if isinstance(dtype, Iterable):
        assert any([isinstance(obj, dt) for dt in dtype]), f"Expected one of [{','.join(str(dt) for dt in dtype)}]; got {type(obj)}"
    else:
        assert isinstance(obj, dtype), f"Expected {dtype}; got {type(obj)}"

def is_valid_path(path):
    try:
        path = Path(path)
    except TypeError:
        return False
    if path.exists():
        return True
    try:
        path.touch()
        if path.is_file():
            path.unlink()
        else:
            path.rmdir()
    except OSError:
        return False
    return True
