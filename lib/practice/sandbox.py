import datetime

import config.dto
import config.adapter

from date import DateInterval, TimeInterval, Schedule
from domain import Program, Student, Group


def create_group(group_config: config.dto.Group) -> Group:
    group_start_date = datetime.datetime.strptime(group_config.date_start, '%Y-%m-%d')
    examination_date = datetime.datetime.strptime(group_config.examination_date, '%Y-%m-%d')
    group = Group(
        name=group_config.name,
        start_date=group_start_date,
        examination_date=examination_date,
    )

    # add schedule
    for schedule in group_config.schedule_list:
        # schedule date start
        date_start = group_start_date
        if schedule.start_date:
            date_start = datetime.datetime.strptime(schedule.start_date, '%Y-%m-%d')

        # schedule date start
        date_end = examination_date
        if schedule.end_date:
            date_end = datetime.datetime.strptime(schedule.end_date, '%Y-%m-%d')

        s = Schedule(
            day=schedule.weekday,
            time_interval=TimeInterval(start=schedule.start, end=schedule.end),
             date_interval=DateInterval(start=date_start.date(), end=date_end.date())
        )
        group.add_schedule(s)

    # populate with students
    for student_ in group_config.students.manual:
        student = Student(student_, program=Program.MANUAL)
        student.group_ = group
        group.append(student)

    for student_ in group_config.students.auto:
        student = Student(student_, program=Program.AUTO)
        student.group_ = group
        group.append(student)

    return group
