import datetime
import typing


# DATE

def time_interval_intersects(time_interval_a: datetime.time, time_interval_b: datetime.time):
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
    def __init__(self, start: str, duration: datetime.time):
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


# System

def cycle(iterable: typing.Iterator):
    while True:
        for item in iterable:
            yield item

# Domain


class Teacher:
    def __init__(self, name: str):
        self.name = name
        self.students_ = []

    def __repr__(self):
        return f'Teacher({self.name!s})'

    def add_student(self, student: 'Student'):
        self.students_.append(student)


class Student:
    def __init__(self, name: str, hours: int = 12):
        self.name = name
        self.hours = hours
        self.group_ = None
        self.teacher_ = None

    def assign_teacher(self, teacher: Teacher):
        self.teacher_ = teacher
        teacher.add_student(self)

    def set_group(self, group: 'Group'):
        self.group_ = group

    def get_group(self) -> typing.Union['Group', None]:
        return self.group_

    def __repr__(self):
        # return f'Student({self.name!r}, hours_left={self.hours!r})'
        return f'Student({self.name!r})'


class Group(list):
    def __init__(self, start_date: datetime.datetime):
        super().__init__()

        self.start_date = start_date
        self.time_law_list: typing.List[TimeLaw] = []

    def add_time_law(self, time_law_list: typing.List[TimeLaw]):
        self.time_law_list.extend(time_law_list)


class Lesson:
    def __init__(
            self,
            student: Student,
            teacher: Teacher,
            interval: DateTimeInterval
    ):
        self.student: Student = student
        self.teacher: Teacher = teacher
        self.interval: DateTimeInterval = interval

    def __repr__(self):
        return f'Lesson(student={self.student!r}, teacher={self.teacher!r}, interval={self.interval!r})'


# 1. все интервалы времени - справедливые к закономерности относительно
# 2. (1.) + исключённые из-за праздничных дней
# 3. (2.) + исключённые из-за расписания занятий группы


def get_lesson_time_interval(examination_date: datetime.date, excluded_dates: typing.List[datetime.date]) -> typing.Iterator[DateTimeInterval]:
    def get_lesson_time_interval(cursor_datetime: datetime.date) -> typing.Iterator[DateTimeInterval]:
        day_law_list = [
            [
                TimeInterval('18:00', 120),
                TimeInterval('20:00', 120),
                TimeInterval('22:00', 120),
            ],
            None,
            None,
            [
                TimeInterval('06:00', 120),
                TimeInterval('08:00', 120),
                TimeInterval('10:00', 120),
            ],
            [
                TimeInterval('12:00', 120),
                TimeInterval('14:00', 120),
                TimeInterval('16:00', 120),
            ],
        ]

        while True:
            index = (cursor_datetime.day-1) % len(day_law_list)
            day = day_law_list[index]

            if day is None:
                cursor_datetime = cursor_datetime + datetime.timedelta(days=1)
                continue

            for interval in day:
                lesson_start_datetime = cursor_datetime.replace(hour=interval.start.hour,minute=interval.start.minute,)
                lesson_end_datetime = lesson_start_datetime + datetime.timedelta(minutes=interval.duration)

                yield DateTimeInterval(lesson_start_datetime, lesson_end_datetime)

            cursor_datetime = cursor_datetime + datetime.timedelta(days=1)

    cursor_datetime = datetime.datetime.combine(examination_date, datetime.time.min)
    cursor_datetime = cursor_datetime + datetime.timedelta(days=7)

    lesson_time_interval_generator = get_lesson_time_interval(cursor_datetime)

    while True:
        for lesson_time_interval in lesson_time_interval_generator:
            yield lesson_time_interval


def may_drive(student: Student, lesson_datetime_interval: DateTimeInterval) -> bool:
    if student.hours <= 0:
        return False

    group = student.get_group()

    if group is None:
        return True

    if (group.start_date + datetime.timedelta(days=7)) > lesson_datetime_interval.start:
        # print(f'Group is not ready to drive')
        return False

    for group_time_law in group.time_law_list:
        if group_time_law.weekday != lesson_datetime_interval.start.weekday():
            return True

        lesson_time_interval = (lesson_datetime_interval.start, lesson_datetime_interval.end)

        group_time_interval_start = lesson_datetime_interval.start.replace(
            hour=group_time_law.interval.start.hour,
            minute=group_time_law.interval.start.minute,
        )

        group_time_interval = (
            group_time_interval_start,
            group_time_interval_start + datetime.timedelta(minutes=int(group_time_law.interval.duration))
        )  # time

        if time_interval_intersects(lesson_time_interval, group_time_interval):
            return False
            # print(f'{student} can not drive on', lesson_time_interval, 'due to theory lesson')
        else:
            return True


def distribute_by_teachers(start_date: datetime.date, teacher_list: typing.List[Teacher]):
    for teacher in teacher_list:
        yield from distribute(
            start_date=start_date,
            student_list=teacher.students_,
        )


def distribute(start_date: datetime.date, student_list: typing.List[Student]):
    def cycle_over_group(group: typing.List[Student]):
        expired = False
        while True:
            for student_ in group:
                expired = False
                if student_.hours <= 0:
                    expired = True
                    continue
                yield student_
            else:
                if expired:
                    break

    if len(student_list) == 0:
        return None

    # # 1. prepare student list
    students_cycle = cycle_over_group(student_list)

    # # 2. iterate over lesson time law
    for lesson_time_interval in get_lesson_time_interval(start_date, []):
        checks = []

        for student in students_cycle:
            check = (student, lesson_time_interval)

            if check in checks:
                break

            if may_drive(student, lesson_time_interval):
                student.hours -= 2  # fixme hardcode

                yield Lesson(
                    student=student,
                    teacher=student.teacher_,
                    interval=lesson_time_interval,
                )

                break

            checks.append(check)
        else:
            break


def assign_students_on_teachers(group_list: typing.List[Group], teacher_list: typing.List[Teacher]):
    teachers = cycle(list(teacher_list))  # fixme
    # groups = reversed(group_list)  # fixme
    groups = group_list  # fixme: temporary

    print('- Assigning students on teachers')

    for group in groups:
        for student in group:
            teacher = next(teachers)

            print(f'  - assign {student!r} on {teacher!r}')

            student.assign_teacher(teacher=teacher)
        print()


import json

class ViewBuilder:
    def build(self, lesson_iterator: typing.Iterator[Lesson]):
        lesson_list = []

        for lesson in lesson_generator:
            lesson_list.append({
                'teacher': lesson.teacher.name,
                'student': lesson.student.name,
                'interval': [
                    lesson.interval.start.strftime('%Y-%m-%d %H:%M:00'),
                    lesson.interval.end.strftime('%Y-%m-%d %H:%M:00')
                ]
            })

        return lesson_list


if __name__ == '__main__':
    def create_group(name: str, size: int, start_date: str) -> Group:
        group = Group(start_date=datetime.datetime.fromisoformat(start_date))

        for number in range(1, size + 1):
            student = Student(name + '_' + str(number))
            student.set_group(group=group)
            group.append(student)

        return group


    # payload

    # teachers:
    teacher_1 = Teacher('1')
    teacher_2 = Teacher('2')
    teacher_3 = Teacher('3')
    teacher_4 = Teacher('4')
    teacher_5 = Teacher('5')
    teacher_6 = Teacher('6')
    teacher_7 = Teacher('7')

    teacher_list = [
        teacher_1,
        teacher_2,
        teacher_3,
        teacher_4,
        teacher_5,
        teacher_6,
        teacher_7
    ]

    # groups
    # group_1 = create_group('13B', 2, '2019-06-25')
    # group_2 = create_group('14B', 2, '2019-07-25')

    group_1 = create_group('13B', 17, '2019-06-25')
    group_2 = create_group('14B', 16, '2019-07-25')
    group_3 = create_group('15B', 14, '2019-09-04')
    group_4 = create_group('16B', 18, '2019-10-12')
    group_5 = create_group('17B', 12, '2019-11-09')

    group_list = [
        group_1,
        group_2,
        group_3,
        group_4,
        group_5,
    ]

    group_1.add_time_law([
        TimeLaw(Week.вторник, TimeInterval('08:00', 195)),  # 8.00-11.15 : 3h15m = 3 * 60 + 15
        TimeLaw(Week.четверг, TimeInterval('08:00', 195)),
        TimeLaw(Week.суббота, TimeInterval('08:00', 195)),
    ])

    group_2.add_time_law([
        TimeLaw(Week.вторник, TimeInterval('11:30', 195)),  # 11.30-14.45 : 3h15m = 3 * 60 + 15
        TimeLaw(Week.четверг, TimeInterval('11:30', 195)),
        TimeLaw(Week.суббота, TimeInterval('11:30', 195)),
    ])

    group_3.add_time_law([
        TimeLaw(Week.понедельник, TimeInterval('15:00', 195)),  # 15.00-18.15 : 3h15m = 3 * 60 + 15
        TimeLaw(Week.среда, TimeInterval('15:00', 195)),
        TimeLaw(Week.пятница, TimeInterval('15:00', 195)),
    ])

    group_4.add_time_law([
        TimeLaw(Week.понедельник, TimeInterval('18:30', 195)),  # 18.30-21.45 : 3h15m = 3 * 60 + 15
        TimeLaw(Week.среда, TimeInterval('18:30', 195)),
        TimeLaw(Week.пятница, TimeInterval('18:30', 195)),
    ])

    group_5.add_time_law([
        TimeLaw(Week.вторник, TimeInterval('19:30', 195)),  # 15.00-18.15 : 3h15m = 3 * 60 + 15
        TimeLaw(Week.четверг, TimeInterval('19:30', 195)),
        TimeLaw(Week.суббота, TimeInterval('19:30', 195)),
        TimeLaw(Week.воскресение, TimeInterval('19:30', 195)),
    ])

    # main
    start_date = datetime.date.fromisoformat('2019-06-26')

    assign_students_on_teachers(
        group_list=group_list,
        teacher_list=teacher_list,
    )

    lesson_generator = distribute_by_teachers(
        start_date=start_date,
        teacher_list=teacher_list,
    )

    view_builder = ViewBuilder()
    data = view_builder.build(lesson_generator)

    response = {
        "meta": {
            "day_schedule": [
                "06.00-08.00",
                "08.00-10.00",
                "10.00-12.00",
                "12.00-14.00",
                "14.00-16.00",
                "16.00-18.00",
                "18.00-20.00",
                "20.00-22.00",
                "22.00-00.00",
            ]
        },
        "data": data,
    }

    raw_response = json.dumps(response)
    print(raw_response)

    # for lesson in lesson_generator:
    #     print(lesson)

    # print(group_list)
