import traceback


def catch_exception(f):
    def wrapper(*args, **kwargs):
        try:
            f()
        except:
            traceback.print_exc()
    return wrapper
