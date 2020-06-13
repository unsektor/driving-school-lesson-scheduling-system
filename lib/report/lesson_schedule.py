
import datetime
import itertools
import sequence
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
    assert lesson_type in {LessonType.RING, LessonType.CITY}
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


def may_drive_group(group: Group, lesson_datetime_interval: DateTimeInterval) -> bool:
    # Прошло 7 дней сначала обучения группы
    if group.start_date + datetime.timedelta(days=7) >= lesson_datetime_interval.start:
        return False

    # Время занятие не за пределом даты экзамена
    if group.examination_date <= lesson_datetime_interval.start:
        return False

    # Отсутствует пересечение с теоритическими занятиями
    for group_schedule in group.schedule_list:
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


# @cache_on(value=False)
def may_drive(student: Student, lesson_datetime_interval: DateTimeInterval) -> bool:
    if student.hours <= 0:
        return False

    if not may_drive_group(group=student.group_, lesson_datetime_interval=lesson_datetime_interval):
        return False

    # Нет уже заплпнированного занятия в этот день
    # scalar_lesson_date_start = lesson_datetime_interval.start.strftime('%Y%m%d')

    a = (lesson_datetime_interval.start.year, lesson_datetime_interval.start.month, lesson_datetime_interval.start.day)
    for lesson in student.lessons_:
        b = (lesson.interval.start.year, lesson.interval.start.month, lesson.interval.start.day)
        if a == b:
            return False

    # Завершил все занятия на площадке
    lesson_type = get_lesson_type(interval=lesson_datetime_interval)
    if lesson_type == LessonType.CITY:
        if not has_finished_lessons_type(student=student, lesson_type=LessonType.RING):
            return False
    return True


def is_weekend(teacher: Teacher, datetime: datetime.datetime, weekend_list: typing.List[datetime.date]) -> bool:
    teacher_weekend_day_list = [3, 8, 13, 18, 23, 28]  # hardcode `range(3, 31, 5))`
    if datetime.day in teacher_weekend_day_list:
        return True

    if datetime.date() in weekend_list:
        return True

    return False


def lesson_interval_generator(day_date: datetime.datetime) -> typing.Iterator[DateTimeInterval]:  # per day
    for start_time, end_time in DAY_WORK_HOUR_INTERVAL_LIST:
        yield date.create_interval(day_date=day_date, start_time=start_time, end_time=end_time)


def group_student_cycle(student_list_: typing.List[Student]) -> typing.Iterator[Student]:
    all_finished = False
    while not all_finished:
        all_finished = True
        for student_ in student_list_:
            if student_.hours > 0:
                all_finished = False
                yield student_


class ConflictResolverInterface:
    def resolve(self, group_list: typing.List[Group]) -> Group:
        raise NotImplementedError


class BasicConflictResolver(ConflictResolverInterface):  # design: not service: not shared, stateful
    def __init__(self):
        self.state = {}

    def resolve(self, group_list: typing.List[Group]) -> Group:
        if len(group_list) > 2:
            if len(group_list) > 3:
                raise NotImplemented
            return group_list[2]

        group_a, group_b = group_list

        id_ = group_a.name + ':' + group_b.name
        if id_ not in self.state:
            self.state[id_] = 0

        if self.state[id_] == 0:
            self.state[id_] += 1
            return group_b

        if self.state[id_] == 2:
            self.state[id_] = 0
        else:
            self.state[id_] += 1

        return group_a


def markup_ring(
        config_: config.dto.Config,
        group_list: typing.List[Group],
        teacher: Teacher,
        group_hours_map: typing.Dict[str, int],
) -> typing.Dict[str, typing.Dict[str, dict]]:
    resolver = BasicConflictResolver()

    scheduled_hours = 0
    entry_dict = {}

    # 1. Поиск самой ранней даты начала обучения (теория)
    group_start_date_set = set()
    for group in group_list:
        group_start_date_set.add(group.start_date)

    min_date = sorted(group_start_date_set)[0]

    # 2. Вычисление даты первого занятия (первое теоритическое занятие первой группы)
    since_date = min_date + datetime.timedelta(days=7)

    # 3. Вычисление суммарного количества часов площадки (count total hours required to schedule)
    to_schedule_hours = 0
    for group_name, group_total_hours in group_hours_map.items():
        to_schedule_hours += group_total_hours

    cursor_date = since_date  # copy to mutate

    while scheduled_hours < to_schedule_hours:  # while not all finished  # TODO check not out of examination date
        if is_weekend(teacher=teacher, datetime=cursor_date, weekend_list=config_.weekend.weekend_list):  # у инструктора выходной ?
            cursor_date += datetime.timedelta(days=1)
            continue  # go to next day

        resolved_group = None
        scheduled_lessons = 0
        for lesson_interval in lesson_interval_generator(day_date=cursor_date):
            if scheduled_lessons >= config_.teacher.max_lessons_per_day:
                # Если для инструктора превышено максимальное количество занятий в день
                break  # go to next day

            # TODO consider to check day instead
            lesson_type = get_lesson_type(interval=lesson_interval)  # todo: reorder by condition check cost
            if lesson_type != LessonType.RING:
                continue  # go to next lesson in this day

            # make group list able to drive at this interval
            may_drive_group_list = []
            for group in group_list:  # for each group check is lesson possible, it's okay
                if group_hours_map[group.name] > 0:
                    if may_drive_group(group=group, lesson_datetime_interval=lesson_interval):
                        may_drive_group_list.append(group)

            # pick group for interval
            group_list_count = len(may_drive_group_list)

            if group_list_count == 0:
                continue  # go to next lesson in this day

            if resolved_group is None:
                if group_list_count == 1:
                    resolved_group = may_drive_group_list[0]
                else:  # > 1
                    resolved_group = resolver.resolve(group_list=may_drive_group_list)

            # schedule group for interval

            scalar_lesson_date = lesson_interval.start.strftime('%Y%m%d')
            if scalar_lesson_date not in entry_dict:
                entry_dict[scalar_lesson_date] = {}  # fixme - use list ?

            scalar_lesson_datetime = lesson_interval.start.strftime('%Y%m%d%H%M')
            entry_dict[scalar_lesson_date][scalar_lesson_datetime] = {
                'group': resolved_group,
                'interval': lesson_interval,
            }
            group_hours_map[resolved_group.name] -= 2
            scheduled_lessons += 1
            scheduled_hours += 2

        cursor_date += datetime.timedelta(days=1)
    return entry_dict


def schedule_ring(
    ring_entry_dict: dict,
    group_student_map: typing.Dict[str, typing.List[Student]],
    teacher: Teacher
) -> typing.Iterator[Lesson]:
    group_day_map = {}

    for day_date, datetime_lesson_map in ring_entry_dict.items():
        for lesson_datetime, info in datetime_lesson_map.items():
            group_name = info['group'].name

            if group_name not in group_day_map:
                group_day_map[group_name] = {}

            if day_date not in group_day_map[group_name]:
                group_day_map[group_name][day_date] = {}

            group_day_map[group_name][day_date][lesson_datetime] = info['interval']

    group_student_cycle_map = {}
    for group_name, student_list in group_student_map.items():
        group_student_cycle_map[group_name] = itertools.cycle(student_list)

    lesson_list = []

    for group_name, day_date_lesson_datetime_map in group_day_map.items():
        for day_date, lesson_m in day_date_lesson_datetime_map.items():
            for lesson_datetime, interval in lesson_m.items():
                lesson_list.append(Lesson(
                    student=next(group_student_cycle_map[group_name]),
                    teacher=teacher,
                    type_=LessonType.RING,
                    interval=interval
                ))

    return lesson_list


def markup_city(
    config_: config.dto.Config,
    group_list: typing.List[Group],
    teacher: Teacher,
    # group_hours_map: dict,
    ring_entry_dict: dict,
    group_city_lesson_date_interval_map: dict
) -> typing.Dict[str, typing.Dict[str, DateTimeInterval]]:
    group_city_lesson_date_interval_list = group_city_lesson_date_interval_map.values()

    final_min_date = sorted([interval['start'] for interval in group_city_lesson_date_interval_list])[0]
    final_max_date = sorted([interval['end'] for interval in group_city_lesson_date_interval_list])[-1]

    since_date = final_min_date + datetime.timedelta(days=1)
    entry_dict = {group.name: {} for group in group_list}

    cursor_date = datetime.datetime.combine(since_date, datetime.datetime.min.time())  # copy to mutate

    while cursor_date < final_max_date:  # while not all finished
        # todo `is_examination_date`
        if is_weekend(teacher=teacher, datetime=cursor_date, weekend_list=config_.weekend.weekend_list):  # у инструктора выходной ?
            cursor_date += datetime.timedelta(days=1)
            continue  # go to next day

        scalar_cursor_date = cursor_date.strftime('%Y%m%d')

        if scalar_cursor_date in ring_entry_dict:
            cursor_date += datetime.timedelta(days=1)
            continue  # TODO 1: разрешить совмещать в один день уроки по вождению в городе и на площадке
            if len(ring_entry_dict[scalar_cursor_date].items()) >= config_.teacher.max_lessons_per_day:
                continue  # go to next day

        scheduled_lessons = 0
        for lesson_interval in lesson_interval_generator(day_date=cursor_date):
            if scheduled_lessons >= config_.teacher.max_lessons_per_day:  # для инструктора не превышено максимальное количество занятий в день
                break  # go to next day

            # todo 2: по завершению (todo 1) добавить проверку на отсутствстие в этот интервал времени занятия на площадке

            # make group list able to drive at this interval
            may_drive_group_list = []
            for group in group_list:  # for each group check is lesson possible, it's okay
                if may_drive_group(group=group, lesson_datetime_interval=lesson_interval):
                    may_drive_group_list.append(group)

            if len(may_drive_group_list) == 0:
                continue  # go to next lesson in this day

            scalar_lesson_datetime = lesson_interval.start.strftime('%Y%m%d%H%M')

            for group in may_drive_group_list:
                entry_dict[group.name][scalar_lesson_datetime] = lesson_interval

            scheduled_lessons += 1

        cursor_date += datetime.timedelta(days=1)
    return entry_dict


def schedule_city(
    city_entry_dict: dict,
    group_student_map: typing.Dict[str, typing.List[Student]],
    teacher: Teacher
) -> typing.Iterable[Lesson]:
    # lesson_datetime_interval_list

    lesson_list = []

    lesson_datetime_interval_set = set()

    for group_name, student_list in group_student_map.items():
        group_city_interval_list = list(city_entry_dict[group_name].values())
        lesson_datetime_interval_generator = sequence.distribute2(list(group_city_interval_list), chunk_count=3)

        for student in group_student_cycle(student_list):
            lesson_datetime_interval = next(lesson_datetime_interval_generator)
            while lesson_datetime_interval in lesson_datetime_interval_set:
                lesson_datetime_interval = next(lesson_datetime_interval_generator)

            lesson_list.append(Lesson(
                student=student,
                teacher=teacher,
                type_=LessonType.CITY,
                interval=lesson_datetime_interval
            ))

            lesson_datetime_interval_set.add(lesson_datetime_interval)

    return lesson_list


def schedule_by_teacher(teacher: Teacher, config_: config.dto.Config) -> typing.Iterator[Lesson]:
    group_dict = {
        'ring.hours': {},
        'city.hours': {},
    }

    # 1. Выполнение подсчёта количества часов на площадке (по группам учеников за учителем)
    group_student_map: typing.Dict[str, typing.List[Student]] = {}

    group_list = []
    for student in teacher.students_:
        group = student.group_

        if group.name not in group_student_map:
            group_student_map[group.name] = []

        group_student_map[group.name].append(student)

        if group.name not in group_dict['ring.hours']:
            group_list.append(student.group_)
            group_dict['ring.hours'][group.name] = 0
            group_dict['city.hours'][group.name] = 0

        ring_total_hours = program_lesson_count_map[student.program] * 2

        group_dict['ring.hours'][group.name] += ring_total_hours
        group_dict['city.hours'][group.name] += 58 - ring_total_hours

    # 2. Сортировка списка групп по дате начала обучения
    group_list.sort(key=lambda group_: group_.start_date)

    # 3. Выполнение разметки расписания площадки
    ring_entry_dict = markup_ring(
        config_=config_,
        group_list=group_list,
        teacher=teacher,
        group_hours_map=group_dict['ring.hours']
    )

    # 3.1. Выполнение проверки, что в день площадки урок возможен только для одной группы
    # (далее, это будет использовано для планирования занятия для одного ученика этой группы)
    def one_group_per_day(ring_entry_dict_: typing.Dict[str, dict]) -> bool:
        for day_date, day_lesson_dict in ring_entry_dict_.items():
            day_group = None
            for lesson_date, lesson_group in day_lesson_dict.items():
                if day_group is None:
                    day_group = lesson_group['group']
                elif day_group is not lesson_group['group']:
                    return False
        return True

    assert one_group_per_day(ring_entry_dict)

    # 4. Планирование расписания площадки (без него невозожно выполнить разметку расписания города)
    ring_lesson_schedule = schedule_ring(ring_entry_dict, group_student_map, teacher)

    # function 1
    group_student_latest_ring_lesson_date_map = {}
    for lesson in ring_lesson_schedule:
        group_name = lesson.student.group_.name
        if group_name not in group_student_latest_ring_lesson_date_map:
            group_student_latest_ring_lesson_date_map[group_name] = {}

        group_student_latest_ring_lesson_date_map[group_name][lesson.student.uuid_] = lesson.interval.start.date()

    group_first_ring_lesson_finish_date_map = {}
    for group_name, data in group_student_latest_ring_lesson_date_map.items():
        group_first_ring_lesson_finish_date_map[group_name] = sorted(data.values())[0]
    # function 1 : end

    group_city_lesson_date_interval_map = {}
    for group in group_list:
        group_city_lesson_date_interval_map[group.name] = {
            'start': group_first_ring_lesson_finish_date_map[group.name],
            'end': group.examination_date
        }

    # 5. Выполнение разметки расписания города
    city_entry_dict = markup_city(
        config_=config_,
        group_list=group_list,
        teacher=teacher,
        # group_hours_map=group_dict['city.hours'],
        ring_entry_dict=ring_entry_dict,
        group_city_lesson_date_interval_map=group_city_lesson_date_interval_map
    )

    # 5. Планирование расписания города
    city_lesson_schedule = schedule_city(city_entry_dict, group_student_map, teacher)

    yield from ring_lesson_schedule
    yield from city_lesson_schedule


def assign_students_on_teachers(group_list: typing.List[Group], teacher_list: typing.List[Teacher]):
    teacher_list_cycle = itertools.cycle(teacher_list)

    for group in group_list:  # round robin assign students to teachers
        for student in group:
            teacher = next(teacher_list_cycle)
            student.assign_teacher_(teacher=teacher)

    # assert
    def teacher_assigned_students_count(teacher_list: typing.List[Teacher]) -> bool:
        for teacher in teacher_list:
            if len(teacher.students_) >= config.dto.Teacher.MAX_STUDENTS:
                return False
        return True

    assert True or teacher_assigned_students_count(teacher_list=teacher_list)  # FIXME !
