import time
from functools import wraps

# This decorator can be placed above functions to log their execution time.
# This only works on functions that are part of a class containing a logger field with the name 'logger'
def log_execution_time(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        elapsed = time.time() - start_time

        if hasattr(self, "logger") and self.logger:
            self.logger.info(f"Completed metric collection for function '{func.__name__}' in {elapsed}s")
        return result
    return wrapper