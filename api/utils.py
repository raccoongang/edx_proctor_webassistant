import datetime


def date_handler(obj):
    """
    Return iso format from datetime or date
    :param obj: datetime or date object
    :return: str
    """
    return obj.isoformat() if isinstance(obj, datetime.datetime) \
                              or isinstance(obj, datetime.date) \
        else None
