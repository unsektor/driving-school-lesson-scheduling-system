
"""
- 1 день в неделю у инструктора выходной
- практика должна не пересекаться с теорией
- в праздники занятий нет
- автоматчики = 11 занятий площадки, механики = 12 занятий площадки
- в город только после площадки
- у ученика максимум одно занятие в день
- у преподавателя максимум 3 занятия в день
"""

# 150 * 75

import datetime
import typing
from functools import lru_cache
import json

import config
import config.dto
import config.adapter

from date import TimeInterval, Schedule, DateTimeInterval
import date
import view
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


def is_weekend(teacher: Teacher, date: datetime.date, weekend_list: typing.List[datetime.date]) -> bool:
    if date.day in [3, 8, 13, 18, 23, 28]:  # FIXME HARDCODE !
        return True

    if date in weekend_list:
        return True

    return False


def schedule_by_teacher(teacher: Teacher, config_: config.dto.Config):
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
        if is_weekend(teacher=teacher, date=cursor_date, weekend_list=config_.weekend.weekend_list):  # у преподавателя выходной ?
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
    def teacher_cycle(iterable: typing.Iterator):
        while True:
            for item in iterable:
                yield item

    teachers = teacher_cycle(teacher_list)
    print('- Assigning students on teachers')

    for group in group_list:
        for student in group:
            teacher = next(teachers)

            print(f'  - assign {student!r} on {teacher!r}')

            student.assign_teacher_(teacher=teacher)
        print()


def create_group(group_config: config.dto.Group) -> Group:
    group = Group(start_date=datetime.datetime.fromisoformat(group_config.date_start))

    # add schedule
    for schedule in group_config.schedule_list:
        group.add_schedule(Schedule(
            day=schedule.weekday,
            interval=TimeInterval(start=schedule.start, end=schedule.end)
        ))

    # populate with students
    for number in range(0, group_config.students.manual):
        student = Student(group_config.name + '_M_' + str(number + 1), program=Program.MANUAL)
        student.group_ = group
        group.append(student)

    for number in range(0, group_config.students.auto):
        student = Student(group_config.name + '_A_' + str(number + 1), program=Program.AUTO)
        student.group_ = group
        group.append(student)

    return group


def main():
    with open('../etc/schedule/test-data.json') as f:
        data = json.load(f)

    config_adapter = config.adapter.ConfigAdapter()
    config_ = config_adapter.adapt(data=data)

    # main
    teacher_list = [Teacher(name=str(i + 1)) for i in range(0, config_.teacher.count)]
    group_list = [create_group(group_config=group_config) for group_config in config_.group_list]

    assign_students_on_teachers(
        group_list=group_list,
        teacher_list=teacher_list,
    )

    def lesson_generator_():
        for teacher in teacher_list:
            yield from schedule_by_teacher(teacher=teacher, config_=config_)

    lesson_generator = lesson_generator_()

    # view
    view_builder = view.ViewBuilder()
    data = view_builder.build(lesson_generator)

    response = {
        "meta": {
            "day_schedule": [f'{start!s}-{end!s}' for start, end in DAY_WORK_HOUR_INTERVAL_LIST]
        },
        "data": data,
    }

    raw_response = json.dumps(response)
    print(raw_response)


if __name__ == '__main__':
    main()
