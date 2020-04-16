import datetime
import typing


class Students:
    def __init__(self, manual: typing.List[str], auto: typing.List[str]):
        self.manual: typing.List[str] = manual
        self.auto: typing.List[str] = auto


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
            examination_date: str,
            students: Students,
            schedule_list:  typing.List[Schedule]
    ):
        self.name: str = name
        self.date_start: str = date_start
        self.examination_date: str = examination_date
        self.students: Students = students
        self.schedule_list: typing.List[Schedule] = schedule_list


class Teacher:
    def __init__(self, count: int, max_lessons_per_day: int):
        self.count = count
        self.max_lessons_per_day = max_lessons_per_day


class Weekend:
    def __init__(self, weekend_list: typing.List[datetime.date]):
        self.weekend_list: typing.List[datetime.date] = weekend_list


class Config:
    def __init__(self, weekend: Weekend, teacher: Teacher, group_list: typing.List[Group]):
        self.weekend: Weekend = weekend
        self.teacher: Teacher = teacher
        self.group_list: typing.List[Group] = group_list
