import datetime
import typing


class Schedule:
    def __init__(self, weekday: int, start: str, end: str):
        self.weekday = weekday
        self.start = start
        self.end = end


class Group:
    def __init__(
            self,
            name: str,
            date_start: str,
            lesson_count: int,
            schedule_list:  typing.List[Schedule]
    ):
        self.name: str = name
        self.date_start: str = date_start
        self.lesson_count: int = lesson_count
        self.schedule_list: typing.List[Schedule] = schedule_list


class Weekend:
    def __init__(self, weekend_list: typing.List[datetime.date]):
        self.weekend_list: typing.List[datetime.date] = weekend_list


class Config:
    def __init__(self, weekend: Weekend, group_list: typing.List[Group]):
        self.weekend: Weekend = weekend
        self.group_list: typing.List[Group] = group_list
