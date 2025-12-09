from functools import wraps
from time import time


def timeit(f):
    """Utility wrapper that times functions and displays input variables."""
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(
            "func:%r args:[%r, %r] took: %2.4f sec" %
            (f.__name__, args, kw, te - ts),
            flush=True
        )
        return result

    return wrap
