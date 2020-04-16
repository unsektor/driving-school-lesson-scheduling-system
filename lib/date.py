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
        return self.start.strftime('%Y-%m-%d (%H:%M-') + self.end.strftime('%H:%M)')


class TimeInterval:
    def __init__(self, start: str, end: str):
        self.start_time = datetime.datetime.strptime(start, '%H:%M')
        self.end_time = datetime.datetime.strptime(end, '%H:%M')


class Schedule:
    def __init__(self, day: int, interval: TimeInterval):
        self.weekday: int = day
        self.interval: TimeInterval = interval


def create_interval(day_date: datetime.datetime, start_time: str, end_time: str) -> DateTimeInterval:
    start_time_ = datetime.datetime.strptime(start_time, '%H:%M')
    end_time_ = datetime.datetime.strptime(end_time, '%H:%M')

    lesson_start_datetime = day_date.replace(
        hour=start_time_.hour,
        minute=start_time_.minute,
    )

    lesson_end_datetime = day_date.replace(
        hour=end_time_.hour,
        minute=end_time_.minute,
    )

    if end_time == '00:00':
        lesson_end_datetime += datetime.timedelta(days=1)

    return DateTimeInterval(start=lesson_start_datetime, end=lesson_end_datetime)
