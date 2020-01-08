import datetime

import config.dto
import config.adapter

from date import TimeInterval, Schedule
from domain import Program, Student, Group


def create_group(group_config: config.dto.Group) -> Group:
    group = Group(
        name=group_config.name,
        start_date=datetime.datetime.fromisoformat(group_config.date_start),
    )

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
