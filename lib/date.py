import datetime
import typing


def time_interval_intersects(
        time_interval_a: typing.Tuple[datetime.datetime, datetime.datetime],
        time_interval_b: typing.Tuple[datetime.datetime, datetime.datetime]
) -> bool:
    time_start_a, time_end_a = time_interval_a
    time_start_b, time_end_b = time_interval_b

    return (time_start_a < time_start_b < time_end_a) or (time_start_b < time_start_a < time_end_b)  # todo test


class DateInterval:
    def __init__(self, start: datetime.date, end: datetime.date):
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return self.start.strftime('%Y-%m-%d - ') + self.end.strftime('%Y-%m-%d')


class DateTimeInterval:
    def __init__(self, start: datetime.datetime, end: datetime.datetime):
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return self.start.strftime('%Y-%m-%d (%H:%M-') + self.end.strftime('%H:%M)')


class TimeInterval:
    def __init__(self, start: str, end: str):
        self.start_time = datetime.datetime.strptime(start, '%H:%M')
        self.end_time = datetime.datetime.strptime(end, '%H:%M')

    def __repr__(self) -> str:
        return f'TimeInterval(start_time={self.start_time.strftime("%H:%M")!r}, end_time={self.end_time.strftime("%H:%M")!r})'


class Schedule:
    def __init__(self, day: int, time_interval: TimeInterval, date_interval: DateInterval):
        self.weekday: int = day
        self.time_interval: TimeInterval = time_interval

        # Date interval when this schedule should be respected
        self.date_interval: DateInterval = date_interval

    def __repr__(self) -> str:
        return f'Schedule(weekday={self.weekday!r}, time_interval={self.time_interval!r}, date_interval={self.date_interval!r})'


def create_interval(day_date: datetime.datetime, start_time: str, end_time: str) -> DateTimeInterval:
    start_time_ = datetime.datetime.strptime(start_time, '%H:%M')
    end_time_ = datetime.datetime.strptime(end_time, '%H:%M')

    start_datetime = day_date.replace(hour=start_time_.hour, minute=start_time_.minute)
    end_datetime = day_date.replace(hour=end_time_.hour, minute=end_time_.minute)

    if end_time == '00:00':
        end_datetime += datetime.timedelta(days=1)

    return DateTimeInterval(start=start_datetime, end=end_datetime)
