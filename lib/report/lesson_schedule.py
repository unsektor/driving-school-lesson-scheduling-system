
import datetime
import itertools
import typing
from functools import lru_cache

import config.dto
import config.adapter

from date import DateTimeInterval
import date
from domain import Program, LessonType, Lesson, Student, Teacher, Group


# System
def cache_on(value):
    def decorator(func):
        cache_map = {}

        def wrapper(*args, **kwargs):
            arguments_hash = (args, kwargs)

            if arguments_hash in cache_map:
                return cache_map[arguments_hash]

            result = func(*args, **kwargs)

            if result == value:
                cache_map[arguments_hash] = result

        return wrapper
    return decorator


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
    ('06:00', '08:00'),  # WORK_HOUR_INTERVAL
    ('08:00', '10:00'),  # WORK_HOUR_INTERVAL
    ('10:00', '12:00'),  # WORK_HOUR_INTERVAL
    ('12:00', '14:00'),  # WORK_HOUR_INTERVAL
    ('14:00', '16:00'),  # WORK_HOUR_INTERVAL
    ('16:00', '18:00'),  # WORK_HOUR_INTERVAL
    ('18:00', '20:00'),  # WORK_HOUR_INTERVAL
    ('20:00', '22:00'),  # WORK_HOUR_INTERVAL
    ('22:00', '00:00'),  # WORK_HOUR_INTERVAL
]

program_lesson_count_map = {
    Program.MANUAL: 12,  # lessons count
    Program.AUTO: 11,
}


# @cache_on(value=True)
def has_finished_lessons_type(student: Student, lesson_type: int) -> bool:
    if lesson_type != LessonType.RING:
        return not (student.hours > 0 and has_finished_lessons_type(student=student, lesson_type=LessonType.RING))

    required_lessons = program_lesson_count_map[student.program]
    finished_lessons_count = 0

    for lesson in student.lessons_:
        if lesson.type == lesson_type:
            finished_lessons_count += 1

    return finished_lessons_count >= required_lessons


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


# @cache_on(value=False)
def may_drive(student: Student, lesson_datetime_interval: DateTimeInterval) -> bool:
    if student.hours <= 0:
        return False

    # Нет уже заплпнированного занятия в этот день
    # scalar_lesson_date_start = lesson_datetime_interval.start.strftime('%Y%m%d')

    a = (lesson_datetime_interval.start.year, lesson_datetime_interval.start.month, lesson_datetime_interval.start.day)
    for lesson in student.lessons_:
        b = (lesson.interval.start.year, lesson.interval.start.month, lesson.interval.start.day)
        if a == b:
            return False

    # Прошло 7 дней сначала обучения группы
    if student.group_ and (student.group_.start_date + datetime.timedelta(days=7)) > lesson_datetime_interval.start:
        # print(f'Group is not ready to drive')
        return False

    # Завершил все занятия на площадке
    lesson_type = get_lesson_type(interval=lesson_datetime_interval)
    if lesson_type == LessonType.CITY:
        if not has_finished_lessons_type(student=student, lesson_type=LessonType.RING):
            return False

    # Отсутствует пересечение с теоритическими занятиями
    for group_schedule in student.group_.schedule_list:
        if group_schedule.weekday != lesson_datetime_interval.start.weekday():
            continue

        lesson_time_interval = (lesson_datetime_interval.start, lesson_datetime_interval.end)

        group_time_interval_start = lesson_datetime_interval.start.replace(
            hour=group_schedule.interval.start_time.hour,
            minute=group_schedule.interval.start_time.minute,
        )

        group_time_interval_end = lesson_datetime_interval.start.replace(
            hour=group_schedule.interval.end_time.hour,
            minute=group_schedule.interval.end_time.minute,
        )

        group_time_interval = (
            group_time_interval_start,
            group_time_interval_end
        )

        if date.time_interval_intersects(lesson_time_interval, group_time_interval):
            return False
            # print(f'{student} can not drive on', lesson_time_interval, 'due to theory lesson')
        else:
            return True
    else:
        return True


def is_weekend(teacher: Teacher, datetime: datetime.datetime, weekend_list: typing.List[datetime.date]) -> bool:
    if datetime.day in [3, 8, 13, 18, 23, 28]:  # FIXME HARDCODE !  range(3, 31, 5))
        return True

    if datetime.date() in weekend_list:
        return True

    return False


def schedule_by_teacher(teacher: Teacher, config_: config.dto.Config) -> typing.Iterator[Lesson]:
    def get_first_study_month(student_list: typing.List[Student]) -> datetime.date:
        group_start_date_set = set()
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

    if not len(teacher.students_) > 0:
        return

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
        day_lessons_count = 0
        if is_weekend(teacher=teacher, datetime=cursor_date, weekend_list=config_.weekend.weekend_list):  # у преподавателя выходной ?
            cursor_date += datetime.timedelta(days=1)
            continue

        for lesson_datetime_interval in lesson_interval_generator(day_date=cursor_date):
            if day_lessons_count >= config_.teacher.max_lessons_per_day:
                break

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
                    day_lessons_count += 1
                    yield lesson
                    continue

            for student in get_students(teacher.students_, LessonType.CITY):
                if may_drive(student, lesson_datetime_interval):
                    day_lessons_count += 1
                    yield Lesson(
                        student=student,
                        teacher=teacher,
                        type_=lesson_type,
                        interval=lesson_datetime_interval
                    )
                    break
        cursor_date = cursor_date + datetime.timedelta(days=1)


def assign_students_on_teachers(group_list: typing.List[Group], teacher_list: typing.List[Teacher]):
    teacher_list_cycle = itertools.cycle(teacher_list)

    for group in group_list:  # round robin assign students to teachers
        for student in group:
            teacher = next(teacher_list_cycle)
            student.assign_teacher_(teacher=teacher)
