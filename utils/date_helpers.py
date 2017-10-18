import datetime


def is_target_day(target_day):
    dt = datetime.datetime.utcnow()
    return target_day == dt.weekday()


def convert_seconds_to_dhms(seconds):
    '''Converts seconds to Days, Hours, Minutes and Seconds'''
    m, s = divmod(seconds, 60)
    h, m = map(int, divmod(m, 60))
    d, h = map(int, divmod(h, 24))
    return {'days': d, 'hours': h, 'minutes': m, 'seconds': s}
