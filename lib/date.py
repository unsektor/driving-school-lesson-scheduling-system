import datetime
import typing


def time_interval_intersects(
        time_interval_a: typing.Tuple[datetime.datetime, datetime.datetime],
        time_interval_b: typing.Tuple[datetime.datetime, datetime.datetime]
) -> bool:
    time_start_a, time_end_a = time_interval_a
    time_start_b, time_end_b = time_interval_b

    return (time_start_a < time_start_b < time_end_a) or (time_start_b < time_start_a < time_end_b)  # todo test


class DateTimeInterval:
    def __init__(self, start: datetime.datetime, end: datetime.datetime):
        self.start = start
        self.end = end

    def __repr__(self):
        return '["' + self.start.strftime('%Y-%m-%d %H:%M') + '", "' + self.end.strftime('%Y-%m-%d %H:%M') + '"]'  # fixme
        # return self.start.strftime('%Y-%m-%d (%H:%M-') + self.end.strftime('%H:%M)')


class TimeInterval:
    def __init__(self, start: str, duration: int):
        self.start = datetime.time.fromisoformat(start)
        self.duration = duration


class Week:
    понедельник = 0
    вторник = 1
    среда = 2
    четверг = 3
    пятница = 4
    суббота = 5
    воскресение = 6


class TimeLaw:
    def __init__(self, day: int, interval: TimeInterval):
        self.weekday = day
        self.interval: TimeInterval = interval
