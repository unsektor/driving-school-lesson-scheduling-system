import datetime
import itertools
import sequence
import typing
import functools

import date

from domain import Program, LessonType, Lesson, Student, Teacher, Group
import practice.config.dto
import practice.config.adapter
import practice.report.dto


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

program_ring_lesson_count_map = {
    Program.MANUAL: 12,  # lessons count
    Program.AUTO: 11,
}


class BalanceError(Exception):
    def __init__(self, lesson_list: typing.List[Lesson]):
        self.lesson_list: typing.List[Lesson] = lesson_list

    # @staticmethod
    # def with_lesson_list(lesson_list: typing.List[Lesson]) -> 'BalanceError':
    #     return BalanceError(lesson_list=lesson_list)


# @cache_on(value=True)
def has_finished_lessons_type(student: Student, lesson_type: int) -> bool:
    assert lesson_type in {LessonType.RING, LessonType.CITY}
    if lesson_type != LessonType.RING:
        return not (student.hours > 0 and has_finished_lessons_type(student=student, lesson_type=LessonType.RING))

    required_lessons = program_ring_lesson_count_map[student.program]
    finished_lessons_count = 0

    for lesson in student.lessons_:
        if lesson.type == lesson_type:
            finished_lessons_count += 1

    return finished_lessons_count >= required_lessons


@functools.lru_cache()
def get_lesson_type(interval: date.DateTimeInterval) -> int:
    index = (interval.start.day - 1) % len(AGREEMENT_RING_LESSON_LAW_TIME_INTERVAL_LIST)
    day_interval_list = AGREEMENT_RING_LESSON_LAW_TIME_INTERVAL_LIST[index]

    if day_interval_list is None:
        return LessonType.CITY

    for interval_ in day_interval_list:
        if (interval_[0],  interval_[1]) == (interval.start.strftime('%H:%M'), interval.end.strftime('%H:%M')):
            return LessonType.RING

    return LessonType.CITY


def may_drive_group(group: Group, lesson_datetime_interval: date.DateTimeInterval) -> bool:
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

        if group_schedule.date_interval.start > lesson_datetime_interval.start.date():
            # Расписание ещё не вступило в силу
            continue

        if group_schedule.date_interval.end < lesson_datetime_interval.start.date():
            # Расписание просрочено
            continue

        lesson_time_interval = (lesson_datetime_interval.start, lesson_datetime_interval.end)

        group_time_interval_start = lesson_datetime_interval.start.replace(
            hour=group_schedule.time_interval.start_time.hour,
            minute=group_schedule.time_interval.start_time.minute,
        )

        group_time_interval_end = lesson_datetime_interval.start.replace(
            hour=group_schedule.time_interval.end_time.hour,
            minute=group_schedule.time_interval.end_time.minute,
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
def may_drive_city(student: Student, lesson_datetime_interval: date.DateTimeInterval) -> bool:
    if student.hours <= 0:
        return False

    if not may_drive_group(group=student.group_, lesson_datetime_interval=lesson_datetime_interval):
        return False

    # Нет уже запланированного занятия в этот день
    # scalar_lesson_date_start = lesson_datetime_interval.start.strftime('%Y%m%d')

    a = (lesson_datetime_interval.start.year, lesson_datetime_interval.start.month, lesson_datetime_interval.start.day)
    for lesson in student.lessons_:
        b = (lesson.interval.start.year, lesson.interval.start.month, lesson.interval.start.day)
        if a == b:
            return False

    return True


def is_weekend(teacher: Teacher, datetime: datetime.datetime, weekend_list: typing.List[datetime.date]) -> bool:
    teacher_weekend_day_list = [3, 8, 13, 18, 23, 28]  # hardcode `range(3, 31, 5))`
    if datetime.day in teacher_weekend_day_list:
        return True

    if datetime.date() in weekend_list:
        return True

    return False


# todo: consider to use LRU cache
def is_examination_day(datetime: datetime.datetime, group_list: typing.List[Group]) -> bool:
    for group in group_list:
        if datetime == group.examination_date:
            return True
    return False


def lesson_interval_generator(day_date: datetime.datetime) -> typing.Iterator[date.DateTimeInterval]:  # per day
    for start_time, end_time in DAY_WORK_HOUR_INTERVAL_LIST:
        yield date.create_interval(day_date=day_date, start_time=start_time, end_time=end_time)


def group_student_cycle(student_list_: typing.List[Student], threshold: int = 0) -> typing.Iterator[Student]:
    assert threshold >= 0

    all_finished = False
    while not all_finished:
        all_finished = True
        for student_ in student_list_:
            if student_.hours > threshold:
                all_finished = False
                yield student_


class BalancerInterface:
    def balance(self, group_list: typing.List[Group]) -> Group:
        raise NotImplementedError


class BasicBalancer(BalancerInterface):  # design: not service: not shared, stateful
    def __init__(self):
        self.state: typing.Dict[str, typing.Iterator] = {}

    def balance(self, group_list: typing.List[Group]) -> Group:
        if len(group_list) == 1:
            return group_list[0]

        # 1. hash
        group_name_list = list(map(lambda group: group.name, group_list))
        group_list_hash = ':'.join(group_name_list)

        if group_list_hash not in self.state:
            sorted_group_list = list(sorted(group_list, key=lambda x: x.name))

            # (-) A, B, C -> B, C, A, A
            # (+) A, B, C -> A, A, B, C
            resolution_group_list = ([sorted_group_list[0]] * 2) + sorted_group_list[1:]

            self.state[group_list_hash] = itertools.cycle(resolution_group_list)

        return next(self.state[group_list_hash])


def markup_ring(teacher: Teacher, config_: practice.config.dto.Config) -> typing.Dict[str, typing.Dict[str, dict]]:
    # Подсчёт количество занятий по группам
    group_list = []
    group_hours_map = {}

    for student in teacher.students_:
        group = student.group_

        if group not in group_list:
            group_list.append(group)
            group_hours_map[group.name] = 0
        group_hours_map[group.name] += program_ring_lesson_count_map[student.program] * 2

    # Сортировка групп по дате начала обучения
    group_list_sorted_by_date_start = sorted(group_list, key=lambda group: group.start_date)

    # 1. Поиск самой ранней даты начала обучения (теория)
    min_date = group_list_sorted_by_date_start[0].start_date
    latest_lesson_date = group_list_sorted_by_date_start[-1].examination_date

    # 2. Вычисление даты первого занятия (первое теоритическое занятие первой группы)
    since_date = min_date + datetime.timedelta(days=7)

    # 3. Вычисление количества закреплённых за инструктором учеников по группам (необходимо для ограничения занятий в день)
    group_max_lessons_per_day_map = {}
    for student in teacher.students_:
        if student.group_.name not in group_max_lessons_per_day_map:
            group_max_lessons_per_day_map[student.group_.name] = 0
        group_max_lessons_per_day_map[student.group_.name] += 1

    resolver = BasicBalancer()

    # 4. ....
    scheduled_hours = 0
    to_schedule_hours = sum(group_hours_map.values())
    # to_schedule_hours *= 2  # FIXME DIRTY AD-HOC

    entry_dict = {}
    cursor_date = since_date  # copy to mutate

    while scheduled_hours < to_schedule_hours:  # while not all finished  # TODO check not out of examination date
        if cursor_date > latest_lesson_date:
            raise BalanceError('Unable to schedule all theory lessons hours: out of latest lesson date')

        group_student_count_map = {}  # (см. 4)

        if is_weekend(teacher=teacher, datetime=cursor_date, weekend_list=config_.weekend.weekend_list) \
           or is_examination_day(datetime=cursor_date, group_list=group_list):
            # если у инструктора выходной или у группы экзаменационный день
            cursor_date += datetime.timedelta(days=1)
            continue  # go to next day

        scheduled_lessons_today = 0
        for lesson_interval in lesson_interval_generator(day_date=cursor_date):
            if scheduled_lessons_today >= config_.teacher.max_lessons_per_day:
                # Если для инструктора превышено максимальное количество занятий в день
                break  # go to next day

            # TODO consider to check day instead
            lesson_type = get_lesson_type(interval=lesson_interval)  # todo: reorder by condition check cost
            if lesson_type != LessonType.RING:
                continue  # go to next lesson in this day

            # make group list that able to drive at this interval
            may_drive_group_list = []
            for group in group_list:  # for each group check is lesson possible, it's okay
                if group_hours_map[group.name] <= 0:
                    continue  # group has no not scheduled lessons

                if may_drive_group(group=group, lesson_datetime_interval=lesson_interval):
                    if group.name not in group_student_count_map:
                        group_student_count_map[group.name] = 0

                    if group_student_count_map[group.name] >= group_max_lessons_per_day_map[group.name]:
                        continue

                    group_student_count_map[group.name] += 1
                    may_drive_group_list.append(group)

            # pick group for interval
            if len(may_drive_group_list) == 0:
                continue  # go to next lesson in this day

            resolved_group = resolver.balance(group_list=may_drive_group_list)

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
            assert group_hours_map[resolved_group.name] >= 0

            scheduled_lessons_today += 1
            scheduled_hours += 2

        cursor_date += datetime.timedelta(days=1)
    return entry_dict


def schedule_ring(teacher: Teacher, ring_entry_dict: typing.Dict[str, dict]) -> typing.Iterator[Lesson]:
    # 1. Index student by group name
    group_student_map: typing.Dict[str, typing.List[Student]] = {}

    for student in teacher.students_:
        group = student.group_

        if group.name not in group_student_map:
            group_student_map[group.name] = []

        group_student_map[group.name].append(student)

    # 2.
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

    for group_name, day_date_lesson_datetime_map in group_day_map.items():
        for day_date, lesson_datetime_interval_index in day_date_lesson_datetime_map.items():
            day_to_student_map = {day_date: set()}
            student_set = set()

            for lesson_datetime, interval in lesson_datetime_interval_index.items():
                # (1) этот блок контроллирует что у ученика может быть только одно занятие в день
                while True:
                    student = next(group_student_cycle_map[group_name])

                    if student in student_set:
                        student = None
                        break

                    student_set.add(student)

                    if student in day_to_student_map[day_date]:
                        continue

                    day_to_student_map[day_date].add(student)
                    break

                if student is None:
                    break
                # (1) end

                yield Lesson(
                    student=student,
                    teacher=teacher,
                    type_=LessonType.RING,
                    interval=interval
                )


def markup_city(config_: practice.config.dto.Config, teacher: Teacher, ring_entry_dict: dict) -> typing.Dict[
    str,
    typing.Dict[str, date.DateTimeInterval]
]:
    student_city_first_lesson_date_map = {}
    group_map = {}

    # ASSERT every student finished ring type lessons & RESOLVE student first possible city type lesson date
    for student in teacher.students_:
        if student.group_.name not in group_map:
            group_map[student.group_.name] = student.group_

        assert len(student.lessons_) == program_ring_lesson_count_map[student.program], \
            'Student should have scheduled all ring lessons'

        student_latest_lesson = student.lessons_[-1]  # assume lesson list sorted by date start
        student_city_first_lesson_date_map[student.uuid_] = {
            # student can not has ring & city lessons same day (or 2 lessons per day), just pick next day
            'date': (student_latest_lesson.interval.start + datetime.timedelta(days=1)).date(),
            'student': student,
        }

    group_list = list(group_map.values())  # internals

    # determine min date
    sorted_student_city_first_lesson_date_list = sorted(student_city_first_lesson_date_map.values(), key=lambda x: x['date'])
    final_min_date = sorted_student_city_first_lesson_date_list[0]['date']

    # determine max date
    sorted_student_city_last_lesson_date_list = sorted([group.examination_date for group in group_map.values()])
    final_max_date = sorted_student_city_last_lesson_date_list[-1]

    entry_dict = {}  # initialize result map
    cursor_date = datetime.datetime.combine(final_min_date, datetime.datetime.min.time())

    while cursor_date < final_max_date:  # while not all finished
        if is_weekend(
                teacher=teacher,
                datetime=cursor_date,
                weekend_list=config_.weekend.weekend_list
        ) or is_examination_day(datetime=cursor_date, group_list=group_list):
            cursor_date += datetime.timedelta(days=1)
            continue  # go to next day

        scalar_cursor_date = cursor_date.strftime('%Y%m%d')

        if scalar_cursor_date in ring_entry_dict:  # all day lessons scheduled (probably for ring type lessons)
            if len(ring_entry_dict[scalar_cursor_date].items()) >= config_.teacher.max_lessons_per_day:
                cursor_date += datetime.timedelta(days=1)
                continue  # go to next day

        for lesson_interval in lesson_interval_generator(day_date=cursor_date):
            scalar_day_date = lesson_interval.start.strftime('%Y%m%d%H%M')

            # is this lesson interval scheduled for ring type lesson ?
            if scalar_cursor_date in ring_entry_dict and scalar_day_date in ring_entry_dict[scalar_cursor_date]:
                continue  # go to next interval

            # save
            student_list = []
            for student_ in teacher.students_:
                if student_city_first_lesson_date_map[student_.uuid_]['date'] < cursor_date.date():
                    if may_drive_city(student=student_, lesson_datetime_interval=lesson_interval):
                        student_list.append(student_)

            if len(student_list) == 0:
                continue

            if scalar_cursor_date not in entry_dict:
                entry_dict[scalar_cursor_date] = {}

            entry_dict[scalar_cursor_date][scalar_day_date] = {
                'student_list': student_list,
                'interval': lesson_interval,
            }

        cursor_date += datetime.timedelta(days=1)
    return entry_dict


def schedule_city(ring_lesson_list: typing.List[Lesson], city_entry_dict: dict, teacher: Teacher) -> typing.Iterable[Lesson]:
    lesson_list = []

    # 1. List all teacher students groups
    group_list = []
    for student in teacher.students_:
        if student.group_ not in group_list:
            group_list.append(student.group_)

    # 2. Schedule internal examination lessons for each student
    group_internal_examination_lesson_interval_generator_map = {
        group.name: lesson_interval_generator(group.examination_date) for group in group_list
    }

    for student in teacher.students_:
        try:
            interval = next(group_internal_examination_lesson_interval_generator_map[student.group_.name])
        except StopIteration as e:
            raise BalanceError(lesson_list=lesson_list)

        lesson_list.append(Lesson(
            student=student,
            teacher=teacher,
            type_=LessonType.INTERNAL_EXAMINATION,
            interval=interval
        ))

    # 3.
    student_lesson_map = {}
    interval_map = {}  # todo optimize wtf

    # 1. group lesson datetime interval by student
    for scalar_lesson_date, lesson_datetime_data_map in city_entry_dict.items():
        for scalar_lesson_datetime, data in lesson_datetime_data_map.items():
            interval_map[scalar_lesson_datetime] = data['interval']

            for student in data['student_list']:
                if student.uuid_ not in student_lesson_map:
                    student_lesson_map[student.uuid_] = []
                student_lesson_map[student.uuid_].append(scalar_lesson_datetime)

    assert len(set(student_lesson_map.keys()).difference([student.uuid_ for student in teacher.students_])) == 0, \
        'Each assigned student should have scheduled city lesson'

    lesson_to_schedule_left = 0  # (2)
    scheduled_city_lesson_index = {}

    # index all ring lessons
    scheduled_ring_lesson_index = {}
    for lesson in ring_lesson_list:
        scalar_lesson_datetime = lesson.interval.start.strftime('%Y%m%d%H%M')
        scalar_lesson_day_date = scalar_lesson_datetime[0:8]

        if scalar_lesson_day_date not in scheduled_ring_lesson_index:
            scheduled_ring_lesson_index[scalar_lesson_day_date] = {}

        scheduled_ring_lesson_index[scalar_lesson_day_date][scalar_lesson_datetime] = None  # `None` for prod, `lesson` for dev (maybe)

    city_lesson_index = {student.uuid_: {} for student in teacher.students_}
    for student in teacher.students_:
        for scalar_lesson_datetime in student_lesson_map[student.uuid_]:
            scalar_lesson_day_date = scalar_lesson_datetime[0:8]

            if scalar_lesson_day_date not in city_lesson_index[student.uuid_]:
                city_lesson_index[student.uuid_][scalar_lesson_day_date] = {}

            city_lesson_index[student.uuid_][scalar_lesson_day_date][scalar_lesson_datetime] = None

    student_lesson_to_schedule_count_map = {}  # DEBUG
    student_lesson_scheduled_count_map = {}  # DEBUG

    student_to_city_lesson_interval_generator_map = {}  # (1)
    for student in teacher.students_:
        # (1)
        student_to_city_lesson_interval_generator_map[student.uuid_] = itertools.cycle(
            sequence.distribute2(
                list_=list(city_lesson_index[student.uuid_].items()),
                chunk_count=3
            )
        )

        student_lesson_scheduled_count_map[student.uuid_] = 0

        # (2)
        if student.program == Program.AUTO:
            # количество занятий только в городе, 1 занятие — экзаминационное
            student_lesson_to_schedule_count_map[student.uuid_] = 17 - 1
            lesson_to_schedule_left += 17 - 1
        elif student.program == Program.MANUAL:
            # количество занятий только в городе, 1 занятие — экзаминационное
            student_lesson_to_schedule_count_map[student.uuid_] = 17 - 1
            lesson_to_schedule_left += 17 - 1
        else:
            assert False, 'Should never happen'

    finished_student_set = set()

    def cycle__():
        student_set = set(teacher.students_)
        while student_set != finished_student_set:
            for student_ in teacher.students_:
                if student_ in finished_student_set:
                    continue

                # print(
                #     student_lesson_scheduled_count_map[student_.uuid_],
                #     student_lesson_to_schedule_count_map[student_.uuid_],
                #     student_lesson_scheduled_count_map[student_.uuid_] >= student_lesson_to_schedule_count_map[student_.uuid_]
                # )

                if student_lesson_scheduled_count_map[student_.uuid_] >= student_lesson_to_schedule_count_map[student_.uuid_]:
                    print(f'{teacher.name!s} / {student_!r} finished')
                    finished_student_set.add(student_)
                    continue

                yield student_

    student_cycle = cycle__()
    scheduled_day_date_cache_set = set()
    student_scalar_lesson_interval_set_map = {student.uuid_: set() for student in teacher.students_}

    for _ in range(lesson_to_schedule_left):  # for each lesson
        try:
            student = next(student_cycle)
        except StopIteration as e:
            raise BalanceError(lesson_list=lesson_list) from e  # Unable to pick student, but no all lessons scheduled

        city_lesson_interval = None
        finished_student_set_ = set()
        while True:  # Iterate over student city lesson days
            city_day_date, city_lesson_interval_datetime_dict = next(student_to_city_lesson_interval_generator_map[student.uuid_])  # FIXME WEAK

            # if city_day_date in scheduled_day_date_cache_set:  # CACHE THINGS
            #     continue  # all entries for this day scheduled, go to next

            # Process picked day
            day_lessons_count = 0

            for city_lesson_interval in city_lesson_interval_datetime_dict.keys():
                if city_lesson_interval in student_scalar_lesson_interval_set_map[student.uuid_]:
                    finished_student_set_.add(student)
                    break

                student_scalar_lesson_interval_set_map[student.uuid_].add(city_lesson_interval)

                if city_day_date in scheduled_day_date_cache_set:  # CACHE THINGS
                    # FIXME: DIRTY! `continue 2` required
                    continue  # all entries for this day scheduled, rewind to next day

                if city_day_date in scheduled_city_lesson_index:  # has teacher city lesson in asked lesson interval day ?
                    if city_lesson_interval in scheduled_city_lesson_index[city_day_date]:  # is city lesson interval already bound ?
                        continue  # go to next interval this day

                    day_lessons_count += len(scheduled_city_lesson_index[city_day_date])  # weak: useless if continue below performed

                if city_day_date in scheduled_ring_lesson_index:  # has teacher ring lesson in asked lesson interval day ?
                    if city_lesson_interval in scheduled_ring_lesson_index[city_day_date]:  # is city lesson interval already bound ?
                        continue

                    day_lessons_count += len(scheduled_ring_lesson_index[city_day_date])

                if day_lessons_count >= 3:  # FIXME use config value instead
                    scheduled_day_date_cache_set.add(city_day_date)
                    continue
                break
            else:  # fixme ban this day for this student
                continue  # `for` cycle was not stopped (no interval was picked), so continue `while` loop and go to the next day
            break  # `for` cycle was stopped (interval was picked, consequently day picked)

        if student in finished_student_set_:  # DIRTY !!!
            continue

        assert city_lesson_interval is not None

        student_lesson_scheduled_count_map[student.uuid_] += 1

        lesson_list.append(Lesson(
            student=student,
            teacher=teacher,
            type_=LessonType.CITY,
            interval=interval_map[city_lesson_interval]
        ))

        if city_day_date not in scheduled_city_lesson_index:  # CACHE THINGS (probably, `set` is okay)
            scheduled_city_lesson_index[city_day_date] = {}
        scheduled_city_lesson_index[city_day_date][city_lesson_interval] = None

    return lesson_list


def schedule_by_teacher(teacher: Teacher, config_: practice.config.dto.Config) -> practice.report.dto.Schedule:
    # 1. Разметка расписания площадки
    ring_entry_dict = markup_ring(teacher=teacher, config_=config_)

    # 2. Планирование расписания площадки (без него невозожно выполнить разметку расписания города)
    ring_lesson_list = list(schedule_ring(teacher=teacher, ring_entry_dict=ring_entry_dict))

    # 3. Разметки расписания города
    city_entry_dict = markup_city(config_=config_, teacher=teacher, ring_entry_dict=ring_entry_dict)

    # 4. Планирование расписания города
    try:
        city_lesson_schedule = schedule_city(
            ring_lesson_list=ring_lesson_list,
            city_entry_dict=city_entry_dict,
            teacher=teacher,
        )
    except BalanceError as e:
        city_lesson_schedule = e.lesson_list

    # 5. Отчёт
    dto = practice.report.dto.Schedule()
    dto.lesson_iterable = itertools.chain(ring_lesson_list, city_lesson_schedule)
    dto.markup = practice.report.dto.Markup()
    return dto


def assign_students_on_teachers(group_list: typing.List[Group], teacher_list: typing.List[Teacher]):
    auto_teacher_list = teacher_list[0:2]
    manual_teacher_list = teacher_list[2:]

    auto_teacher_list_cycle = itertools.cycle(auto_teacher_list)
    manual_teacher_list_cycle = itertools.cycle(manual_teacher_list)

    if True:
        for group in group_list:  # round robin assign students to teachers
            for student in group:
                student: Student

                if student.program == Program.AUTO:
                    teacher = next(auto_teacher_list_cycle)
                elif student.program == Program.MANUAL:
                    teacher = next(manual_teacher_list_cycle)
                else:
                    assert False

                student.assign_teacher_(teacher=teacher)
    else:
        for i, group in enumerate(group_list):  # round robin assign students to teachers
            for student in group:
                student: Student

                if student.program == Program.AUTO:
                    teacher = auto_teacher_list[i % 2]
                elif student.program == Program.MANUAL:
                    teacher = next(manual_teacher_list_cycle)
                else:
                    assert False

                student.assign_teacher_(teacher=teacher)

    # assert
    def teacher_assigned_students_count(teacher_list: typing.List[Teacher]) -> bool:
        for teacher in teacher_list:
            if len(teacher.students_) >= practice.config.dto.Teacher.MAX_STUDENTS:
                return False
        return True

    assert True or teacher_assigned_students_count(teacher_list=teacher_list)  # FIXME !
