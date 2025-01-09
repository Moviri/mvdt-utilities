import time
from functools import wraps



def debug_execution_time(func):
    """
    This decorator can be placed above functions to log their execution time.
    This only works on functions that are part of a class containing a logger field with the name 'logger'
    """
    # Ex:
    # class Test:
    #   @log_execution_time
    #   def testing(self):
    #       pass
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        elapsed = time.time() - start_time

        if hasattr(self, "logger") and self.logger:
            self.logger.debug(f"Completed metric collection for function '{func.__name__}' in {elapsed}s")
        return result
    return wrapper