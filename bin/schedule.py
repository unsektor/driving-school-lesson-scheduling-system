
"""
- 1 день в неделю у инструктора выходной
- практика должна не пересекаться с теорией
- в праздники занятий нет
- автоматчики = 11 занятий площадки, механики = 12 занятий площадки
- в город только после площадки
- у ученика максимум одно занятие в день
"""


import datetime
import typing
from functools import lru_cache


# DATE

def time_interval_intersects(
        time_interval_a: typing.Tuple[datetime.datetime, datetime.datetime],
        time_interval_b: typing.Tuple[datetime.datetime, datetime.datetime]
):
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


# System

def cycle(iterable: typing.Iterator):
    while True:
        for item in iterable:
            yield item

# Domain


AGREEMENT_RING_LESSON_LAW_TIME_INTERVAL_LIST = [
    [
        ('18:00', '20:00'),
        ('20:00', '22:00'),
        ('22:00', '00:00'),
    ],
    None,
    None,
    [
        ('06:00', '08:00'),
        ('08:00', '10:00'),
        ('10:00', '12:00'),
    ],
    [
        ('12:00', '14:00'),
        ('14:00', '16:00'),
        ('16:00', '18:00'),
    ],
]

DAY_WORK_HOUR_INTERVAL_LIST = [
    ("06:00", "08:00"),  # WORK_HOUR_INTERVAL
    ("08:00", "10:00"),  # WORK_HOUR_INTERVAL
    ("10:00", "12:00"),  # WORK_HOUR_INTERVAL
    ("12:00", "14:00"),  # WORK_HOUR_INTERVAL
    ("14:00", "16:00"),  # WORK_HOUR_INTERVAL
    ("16:00", "18:00"),  # WORK_HOUR_INTERVAL
    ("18:00", "20:00"),  # WORK_HOUR_INTERVAL
    ("20:00", "22:00"),  # WORK_HOUR_INTERVAL
    ("22:00", "00:00"),  # WORK_HOUR_INTERVAL
]


class Teacher:
    def __init__(self, name: str):
        self.name = name
        self.students_ = []

    def __repr__(self):
        return f'Teacher({self.name!s})'

    def add_student(self, student: 'Student'):
        self.students_.append(student)


class Program:
    MANUAL = 0
    AUTO = 1


program_lesson_count_map = {
    Program.MANUAL: 12,  # lessons count
    Program.AUTO: 11,
}


class Student:
    def __init__(self, name: str, program: int):
        self.name = name
        self.hours = 58  # / 2 = 29
        self.program = program

        self.group_ = None
        self.teacher_ = None
        self.lessons_ = []  # planned drive lessons

    def assign_teacher(self, teacher: Teacher):
        self.teacher_ = teacher
        teacher.add_student(self)

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
            interval: DateTimeInterval
    ):
        self.student: Student = student
        self.teacher: Teacher = teacher
        self.type: int = type_
        self.interval: DateTimeInterval = interval

        student.hours -= self.HOURS_DURATION
        student.lessons_.append(self)

    def __repr__(self):
        return f'Lesson(student={self.student!r}, teacher={self.teacher!r}, interval={self.interval!r})'


def has_finished_lessons_type(student: Student, lesson_type: int):
    if lesson_type != LessonType.RING:
        return not (has_finished_lessons_type(student=student, lesson_type=LessonType.RING) and student.hours > 0)

    required_lessons = program_lesson_count_map[student.program]
    finished_lessons_count = 0

    for lesson in student.lessons_:
        if lesson.type == lesson_type:
            finished_lessons_count += 1

    return finished_lessons_count >= required_lessons


# 1. все интервалы времени - справедливые к закономерности относительно
# 2. (1.) + исключённые из-за праздничных дней
# 3. (2.) + исключённые из-за расписания занятий группы


def get_lesson_time_interval(examination_date: datetime.date, excluded_dates: typing.List[datetime.date]) -> typing.Iterator[DateTimeInterval]:
    def get_lesson_time_interval(cursor_datetime: datetime.date) -> typing.Iterator[DateTimeInterval]:
        while True:
            index = (cursor_datetime.day-1) % len(AGREEMENT_RING_LESSON_LAW_TIME_INTERVAL_LIST)
            day = AGREEMENT_RING_LESSON_LAW_TIME_INTERVAL_LIST[index]

            is_weekend = cursor_datetime.day % 7 == 0
            if is_weekend or (day is None):
                if is_weekend:
                    # print('day is weekend')
                    pass
                cursor_datetime = cursor_datetime + datetime.timedelta(days=1)
                continue

            for interval in day:
                lesson_start_datetime = cursor_datetime.replace(hour=interval.start.hour, minute=interval.start.minute,)
                lesson_end_datetime = lesson_start_datetime + datetime.timedelta(minutes=interval.duration)

                yield DateTimeInterval(lesson_start_datetime, lesson_end_datetime)

            cursor_datetime = cursor_datetime + datetime.timedelta(days=1)

    cursor_datetime = datetime.datetime.combine(examination_date, datetime.time.min)
    cursor_datetime = cursor_datetime + datetime.timedelta(days=7)

    lesson_time_interval_generator = get_lesson_time_interval(cursor_datetime)

    while True:
        for lesson_time_interval in lesson_time_interval_generator:
            yield lesson_time_interval


@lru_cache()
def get_lesson_type(interval: DateTimeInterval) -> int:
    index = (interval.start.day - 1) % len(AGREEMENT_RING_LESSON_LAW_TIME_INTERVAL_LIST)
    day_interval_list = AGREEMENT_RING_LESSON_LAW_TIME_INTERVAL_LIST[index]

    if day_interval_list is None:
        return LessonType.CITY

    for interval_ in day_interval_list:
        if (interval_[0],  interval_[1]) == (interval.start.strftime('%H:%M'), interval.end.strftime('%H:%M')):
            return LessonType.RING

    return LessonType.CITY


def may_drive(student: Student, lesson_datetime_interval: DateTimeInterval) -> bool:
    if student.hours <= 0:
        return False

    # Нет уже заплпнированного занятия в этот день
    scalar_lesson_date_start = lesson_datetime_interval.start.strftime('%Y%m%d')
    for lesson in student.lessons_:
        if lesson.interval.start.strftime('%Y%m%d') == scalar_lesson_date_start:
            return False

    # Прошло 7 дней с начала обучения группы
    if student.group_ and (student.group_.start_date + datetime.timedelta(days=7)) > lesson_datetime_interval.start:
        # print(f'Group is not ready to drive')
        return False

    # Завершил все занятия на площадке
    lesson_type = get_lesson_type(interval=lesson_datetime_interval)
    if lesson_type == LessonType.CITY:
        if not has_finished_lessons_type(student=student, lesson_type=LessonType.RING):
            return False

    # Отсутствует пересечение с теоритическими занятиями
    for group_time_law in student.group_.time_law_list:
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


def is_weekend(teacher: Teacher, date: datetime.date):
    return date.day in [3, 8, 13, 18, 23, 28]  # FIXME HARDCODE !


def di_teacher(teacher: Teacher):
    def get_first_study_month(student_list: typing.List[Student]) -> datetime.date:
        group_start_date_set = set()  # fixme use set instead
        for student in student_list:
            group_start_date_set.add(student.group_.start_date)

        group_start_date_list = sorted(group_start_date_set)
        return group_start_date_list[0]

    def all_finished(student_list: typing.List[Student]) -> bool:
        for student in student_list:
            if student.hours > 0:
                return False
        return True

    def lesson_interval_generator(day_date: datetime.datetime) -> typing.Iterator[DateTimeInterval]:  # per day
        cursor_datetime__ = day_date
        for start_time, end_time in DAY_WORK_HOUR_INTERVAL_LIST:
            start_time_ = datetime.datetime.strptime(start_time, '%H:%M')
            end_time_ = datetime.datetime.strptime(end_time, '%H:%M')

            lesson_start_datetime = cursor_datetime__.replace(
                hour=start_time_.hour,
                minute=start_time_.minute,
            )

            lesson_end_datetime = cursor_datetime__.replace(
                hour=end_time_.hour,
                minute=end_time_.minute,
            )

            if end_time == '00:00':
                lesson_end_datetime += datetime.timedelta(days=1)

            yield DateTimeInterval(lesson_start_datetime, lesson_end_datetime)

    date_start_from = get_first_study_month(student_list=teacher.students_)

    cursor_date = date_start_from + datetime.timedelta(days=7)

    def get_students(student_list: typing.List[Student], lesson_type: int):
        ring_student_list = []
        for student in student_list:
            if not has_finished_lessons_type(student=student, lesson_type=lesson_type):
                ring_student_list.append(student)
        return sorted(ring_student_list, key=lambda student: student.hours, reverse=True)

    # пока у преподавателя не все студенты завершили все часы вождения
    while not all_finished(student_list=teacher.students_):
        if is_weekend(teacher=teacher, date=cursor_date):  # у преподавателя выходной ?
            cursor_date += datetime.timedelta(days=1)
            continue

        for lesson_datetime_interval in lesson_interval_generator(day_date=cursor_date):
            lesson_type = get_lesson_type(interval=lesson_datetime_interval)
            # print ('lesson type : ', lesson_type)
            if lesson_type == LessonType.RING:
                lesson = None

                for student in get_students(teacher.students_, LessonType.RING):
                    if may_drive(student, lesson_datetime_interval):
                        lesson = Lesson(
                            student=student,
                            teacher=teacher,
                            type_=lesson_type,
                            interval=lesson_datetime_interval
                        )
                        break

                if lesson:
                    yield lesson
                    continue

            for student in get_students(teacher.students_, LessonType.CITY):
                if may_drive(student, lesson_datetime_interval):
                    yield Lesson(
                        student=student,
                        teacher=teacher,
                        type_=lesson_type,
                        interval=lesson_datetime_interval
                    )
                    break
        cursor_date = cursor_date + datetime.timedelta(days=1)


def assign_students_on_teachers(group_list: typing.List[Group], teacher_list: typing.List[Teacher]):
    teachers = cycle(list(teacher_list))  # fixme
    print('- Assigning students on teachers')

    for group in group_list:
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
    def create_group(
            name: str,
            manual_size: int,
            auto_size: int,
            start_date: str
    ) -> Group:
        group = Group(
            start_date=datetime.datetime.fromisoformat(start_date)
        )

        for number in range(1, manual_size + 1):
            student = Student(name + '_M_' + str(number), program=Program.MANUAL)
            student.group_ = group
            group.append(student)

        for number in range(1, auto_size + 1):
            student = Student(name + '_A_' + str(number), program=Program.AUTO)
            student.group_ = group
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
    group_1 = create_group('13B', 14, 3, '2019-06-25')  # 3 автомат: 17-3 = 14
    group_2 = create_group('14B', 12, 4, '2019-07-25')  # 4 автомат: 16-4 = 12
    group_3 = create_group('15B', 11, 3, '2019-09-04')  # 3 автомат: 14-3 = 11
    group_4 = create_group('16B', 12, 6, '2019-10-12')  # 6 автомат: 18-6 = 12
    group_5 = create_group('17B', 10, 2, '2019-11-09')  # 2 автомат: 12-2 = 10

    group_list = [
        group_1,
        group_2,
        group_3,
        group_4,
        group_5,
    ]

    group_1.add_time_law([
        # 8.00-11.15 : 3h15m = 3 * 60 + 15
        TimeLaw(Week.вторник, TimeInterval('08:00', 195)),
        TimeLaw(Week.четверг, TimeInterval('08:00', 195)),
        TimeLaw(Week.суббота, TimeInterval('08:00', 195)),
    ])

    group_2.add_time_law([
        # 11.30-14.45 : 3h15m = 3 * 60 + 15
        TimeLaw(Week.вторник, TimeInterval('11:30', 195)),
        TimeLaw(Week.четверг, TimeInterval('11:30', 195)),
        TimeLaw(Week.суббота, TimeInterval('11:30', 195)),
    ])

    group_3.add_time_law([
        # 15.00-18.15 : 3h15m = 3 * 60 + 15
        TimeLaw(Week.понедельник, TimeInterval('15:00', 195)),
        TimeLaw(Week.среда, TimeInterval('15:00', 195)),
        TimeLaw(Week.пятница, TimeInterval('15:00', 195)),
    ])

    group_4.add_time_law([
        # 18.30-21.45 : 3h15m = 3 * 60 + 15
        TimeLaw(Week.понедельник, TimeInterval('18:30', 195)),
        TimeLaw(Week.среда, TimeInterval('18:30', 195)),
        TimeLaw(Week.пятница, TimeInterval('18:30', 195)),
    ])

    group_5.add_time_law([
        # 15.00-18.15 : 3h15m = 3 * 60 + 15
        TimeLaw(Week.вторник, TimeInterval('19:30', 195)),
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

    def lesson_generator_():
        for teacher in teacher_list:
            yield from di_teacher(teacher=teacher)

    lesson_generator = lesson_generator_()

    view_builder = ViewBuilder()
    data = view_builder.build(lesson_generator)

    response = {
        "meta": {
            # "day_schedule": DAY_WORK_HOUR_INTERVAL_LIST  # fixme
        },
        "data": data,
    }

    raw_response = json.dumps(response)
    print(raw_response)
