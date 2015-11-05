import traceback
import datetime


def catch_exception(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            traceback.print_exc()
    return wrapper


def date_handler(obj):
    return obj.isoformat() if isinstance(obj, datetime.datetime) \
                              or isinstance(obj, datetime.date) \
        else None
