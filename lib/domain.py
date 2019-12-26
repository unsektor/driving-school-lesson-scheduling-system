import datetime
import typing

import date


class Program:
    MANUAL = 0
    AUTO = 1


class Student:
    def __init__(self, name: str, program: int):
        self.name = name
        self.hours = 58  # / 2 = 29
        self.program = program

        self.group_ = None
        self.teacher_ = None
        self.lessons_ = []  # planned drive lessons

    def assign_teacher_(self, teacher: 'Teacher') -> None:
        self.teacher_ = teacher
        teacher.add_student(self)

    def __repr__(self) -> str:
        return f'Student({self.name!r})'


class Group(list):
    def __init__(self, start_date: datetime.datetime):
        super().__init__()

        self.start_date = start_date
        self.time_law_list: typing.List[date.TimeLaw] = []

    def add_time_law(self, time_law_list: typing.List[date.TimeLaw]):
        self.time_law_list.extend(time_law_list)


class Teacher:
    def __init__(self, name: str):
        self.name = name
        self.students_ = []

    def __repr__(self):
        return f'Teacher({self.name!s})'

    def add_student(self, student: 'Student'):
        self.students_.append(student)


class LessonType:
    RING = 0  # площадка
    CITY = 1  # город


class Lesson:
    HOURS_DURATION = 2

    def __init__(
            self,
            student: Student,
            teacher: Teacher,
            type_: int,
            interval: date.DateTimeInterval
    ):
        self.student: Student = student
        self.teacher: Teacher = teacher
        self.type: int = type_
        self.interval: date.DateTimeInterval = interval

        student.hours -= self.HOURS_DURATION
        student.lessons_.append(self)

    def __repr__(self):
        return f'Lesson(student={self.student!r}, teacher={self.teacher!r}, interval={self.interval!r})'
