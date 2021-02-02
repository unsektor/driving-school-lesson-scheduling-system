import datetime
import typing

import theory.config.dto

from date import DateTimeInterval
import date


def create_for_group_list(config_: theory.config.dto.Config) -> typing.Iterable[dict]:
    group_list_sorted_by_start_date = sorted([group.date_start for group in config_.group_list])
    final_min_date = group_list_sorted_by_start_date[0]
    final_max_date = group_list_sorted_by_start_date[-1]

    # assert final_max_date > final_min_date  # will not work for 1 group

    # 2
    group_schedule_list_map = {}

    schedule_list = []

    for group in config_.group_list:
        group_schedule_list_map[group.name] = []
        for schedule_ in group.schedule_list:
            schedule = date.Schedule(
                day=schedule_.weekday,
                time_interval=date.TimeInterval(start=schedule_.start, end=schedule_.end)
            )
            group_schedule_list_map[group.name].append(schedule)
            schedule_list.append(schedule)

    # schedule_list = list(sorted(scheduфеьщяаle_list))

    # 3
    group_lesson_count_map = {group.name : 0 for group in config_.group_list}

    lesson_list = []

    date_cursor = datetime.datetime.strptime(final_min_date, '%Y-%m-%d').date()

    all_finished = False

    while not all_finished:
        if date_cursor in config_.weekend.weekend_list:
            date_cursor += datetime.timedelta(days=1)
            continue

        all_finished = True

        date_cursor_week_day = date_cursor.weekday()
        for group in config_.group_list:
            if group_lesson_count_map[group.name] >= group.lesson_count:
                continue

            all_finished = False

            if date_cursor < datetime.datetime.strptime(group.date_start, '%Y-%m-%d').date():
                continue

            for schedule in group_schedule_list_map[group.name]:
                schedule: date.Schedule

                if date_cursor_week_day != schedule.weekday:
                    continue

                lesson_list.append({
                    'group': group.name,
                    'interval': DateTimeInterval(
                        start=datetime.datetime(
                            year=date_cursor.year,
                            month=date_cursor.month,
                            day=date_cursor.day,
                            hour=schedule.time_interval.start_time.hour,
                            minute=schedule.time_interval.start_time.minute
                        ),
                        end=datetime.datetime(
                            year=date_cursor.year,
                            month=date_cursor.month,
                            day=date_cursor.day,
                            hour=schedule.time_interval.end_time.hour,
                            minute=schedule.time_interval.end_time.minute
                        )
                    )
                    # 'interval': [
                    #     date_cursor.strftime('%Y-%m-%d ') + schedule.interval.start_time.strftime('%H:%M:00'),
                    #     date_cursor.strftime('%Y-%m-%d ') + schedule.interval.end_time.strftime('%H:%M:00'),
                    # ]

                })

                group_lesson_count_map[group.name] += 1
        date_cursor += datetime.timedelta(days=1)
    return lesson_list
