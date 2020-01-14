import datetime

import config.dto
import config.adapter

from date import TimeInterval, Schedule
from domain import Program, Student, Group


def create_group(group_config: config.dto.Group) -> Group:
    group = Group(
        name=group_config.name,
        start_date=datetime.datetime.strptime(group_config.date_start, '%Y-%m-%d'),
    )

    # add schedule
    for schedule in group_config.schedule_list:
        group.add_schedule(Schedule(
            day=schedule.weekday,
            interval=TimeInterval(start=schedule.start, end=schedule.end)
        ))

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
