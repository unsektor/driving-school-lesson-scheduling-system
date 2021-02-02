import datetime
import typing

import date
import uuid


class Program:
    MANUAL = 0
    AUTO = 1


class Student:
    def __init__(self, name: str, program: int):
        self.name = name

        if program == Program.MANUAL:
            self.hours = 58  # (12 + 16 + 1) * 2
        elif program == Program.AUTO:
            self.hours = 56  # (11 + 16 + 1) * 2

        self.program = program

        self.group_: typing.Union[Group, None] = None
        self.teacher_ = None
        self.lessons_: typing.List[Lesson] = []  # planned drive lessons

        self.uuid_ = self.name + '__' + str(uuid.uuid4())  # DEBUG ONLY

    def assign_teacher_(self, teacher: 'Teacher') -> None:
        self.teacher_ = teacher
        teacher.add_student(self)

    def __repr__(self) -> str:
        return f'Student({self.name!r})'


class Group(list):
    def __init__(self, name: str, start_date: datetime.datetime, examination_date: datetime.datetime):
        super().__init__()

        self.name = name
        self.start_date = start_date
        self.examination_date = examination_date
        self.schedule_list: typing.List[date.Schedule] = []

    def add_schedule(self, schedule: date.Schedule) -> None:
        self.schedule_list.append(schedule)

    def __hash__(self) -> int:
        return int(self.name)  # FIXME !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def __repr__(self) -> str:
        return self.name + f'({len(self)})'


class Teacher:
    def __init__(self, name: str):
        self.name = name
        self.students_: typing.List[Student] = []

    def __repr__(self):
        return f'Teacher({self.name!s})'

    def add_student(self, student: 'Student'):
        self.students_.append(student)


class LessonType:
    RING = 0  # площадка
    CITY = 1  # город
    INTERNAL_EXAMINATION = 2  # внутренний экзамен


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

    def __repr__(self) -> str:
        return f'Lesson(student={self.student!r}, teacher={self.teacher!r}, interval={self.interval!r}, type={self.type!r})'
