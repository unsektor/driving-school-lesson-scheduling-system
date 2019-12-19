import datetime
import typing


# DATE

def time_interval_intersects(time_interval_a: datetime.time, time_interval_b: datetime.time):
    time_start_a, time_end_a = time_interval_a
    time_start_b, time_end_b = time_interval_b

    return (time_start_a <= time_start_b <= time_end_a) or (time_start_b <= time_start_a <= time_end_b)


class DateTimeInterval:
    def __init__(self, start: datetime.datetime, end: datetime.datetime):
        self.start = start
        self.end = end

    def __repr__(self):
        return self.start.strftime('%Y-%m-%d (%H:%M-') + self.end.strftime('%H:%M)')


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


# Domain

class Teacher:
    def __init__(self, name: str):
        self.name = str
        self.students_ = []


class Student:
    def __init__(self, name: str, hours: int = 58):
        self.name = name
        self.hours = hours
        self.group_ = None

    def set_group(self, group: 'Group'):
        self.group_ = group

    def get_group(self) -> typing.Union['Group', None]:
        return self.group_

    def __repr__(self):
        return f'Student({self.name!s})'


class Group(list):
    def __init__(self):
        super().__init__()

        self.time_law_list: typing.List[TimeLaw] = []

    def add_time_law(self, time_law_list: typing.List[TimeLaw]):
        self.time_law_list.extend(time_law_list)



# 1. все интервалы времени - справедливые к закономерности относительно
# 2. (1.) + исключённые из-за праздничных дней
# 3. (2.) + исключённые из-за расписания занятий группы


def get_lesson_time_interval(examination_date: datetime.date, excluded_dates: typing.List[datetime.date]):
    def get_lesson_time_interval(cursor_datetime):
        day_law_list = [
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
            [
                TimeInterval('18:00', 120),
                TimeInterval('20:00', 120),
                TimeInterval('22:00', 120),
            ]
        ]

        while True:
            for day in reversed(day_law_list):
                if day is None:
                    cursor_datetime = cursor_datetime - datetime.timedelta(days=1)
                    continue

                for interval in reversed(day):
                    lesson_start_datetime = cursor_datetime.replace(hour=interval.start.hour,minute=interval.start.minute,)
                    lesson_end_datetime = lesson_start_datetime + datetime.timedelta(minutes=interval.duration)

                    yield DateTimeInterval(lesson_start_datetime, lesson_end_datetime)

                cursor_datetime = cursor_datetime - datetime.timedelta(days=1)

    cursor_datetime = datetime.datetime.combine(examination_date, datetime.time.min)
    cursor_datetime = cursor_datetime - datetime.timedelta(days=1)

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

    for group_time_law in group.time_law_list:
        if group_time_law.weekday != lesson_datetime_interval.start.weekday():
            return True

        lesson_time_interval = (lesson_datetime_interval.start, lesson_datetime_interval.end)

        group_time_interval_start = lesson_datetime_interval.start.replace(
            hour=group_time_law.interval.start.hour,
            minute=group_time_law.interval.start.minute,
        )

        group_time_interval = (group_time_interval_start, group_time_interval_start + datetime.timedelta(minutes=group_time_law.interval.duration))  # time

        return not time_interval_intersects(lesson_time_interval, group_time_interval)


def distribute(examination_date: datetime.date, group_list: typing.List[Group]):
    def cycle(x):
        while True:
            for i in x:
                yield i

    # # 1. prepare student list
    student_list: typing.List[Student] = []

    for group in reversed(group_list):
        student_list.extend(reversed(group))

    students_cycle = cycle(student_list)  # fixme

    # # 2. iterate over lesson time law
    for lesson_time_interval in get_lesson_time_interval(examination_date, []):
        bound = False

        for student in students_cycle:
            if may_drive(student, lesson_time_interval):
                student.hours -= 2  # fixme hardcode
                bound = True
                print( lesson_time_interval, student)  # fixme replace print to yield
                break
        else:
            break

        if bound:
            continue
        else:
            raise Exception('should never happen')


if __name__ == '__main__':
    def create_group(name: str, size: int) -> Group:
        group = Group()

        for number in range(1, size + 1):
            student = Student(name + '_' + str(number))
            student.set_group(group=group)
            group.append(student)

        return group


    # payload

    teacher_1 = Teacher(1)
    teacher_2 = Teacher(2)
    teacher_3 = Teacher(3)
    teacher_4 = Teacher(4)
    teacher_5 = Teacher(5)
    teacher_6 = Teacher(6)
    teacher_7 = Teacher(7)

    teacher_list = [
        teacher_1,
        teacher_2,
        teacher_3,
        teacher_4,
        teacher_5,
        teacher_6,
        teacher_7
    ]

    group_1 = create_group('A', 5)
    group_2 = create_group('B', 5)

    # group_1 = create_group('A', 11)
    # group_2 = create_group('B', 16)

    group_1.add_time_law([
        TimeLaw(Week.понедельник, TimeInterval('18:00', 120)),
        TimeLaw(Week.среда,TimeInterval('18:00', 120)),
    ])

    group_2.add_time_law([
        TimeLaw(Week.вторник, TimeInterval('19:30', 120)),
        TimeLaw(Week.четверг, TimeInterval('19:30', 120)),
    ])

    examination_date = datetime.date.fromisoformat('2019-09-21')

    distribute(
        examination_date=examination_date,
        group_list=[
            group_1,
            group_2
        ]
    )
