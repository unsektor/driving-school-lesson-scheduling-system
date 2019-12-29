import typing


class Students:
    def __init__(self, manual: int, auto: int):
        self.manual: int = manual
        self.auto: int = auto


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
            students: Students,
            schedule_list:  typing.List[Schedule]
    ):
        self.name: str = name
        self.date_start: str = date_start
        self.students: Students = students
        self.schedule_list: typing.List[Schedule] = schedule_list


class Teacher:
    def __init__(self, count: int):
        self.count = count


class Config:
    def __init__(self, weekend_list: typing.List[str], teacher: Teacher, group_list: typing.List[Group]):
        self.weekend_list = weekend_list
        self.teacher: Teacher = teacher
        self.group_list: typing.List[Group] = group_list
