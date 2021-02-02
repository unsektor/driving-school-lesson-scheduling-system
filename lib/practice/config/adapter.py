import datetime
import practice.config.dto

import re

# datetime_interval_re = re.compile(r'^(?P<date>\d{4}-\d{2}-\d{2}):(?P=date)$')
datetime_interval_re = re.compile(r'^(?P<start_date>\d{4}-\d{2}-\d{2}):(?P<end_date>\d{4}-\d{2}-\d{2})$')


class StudentsAdapter:
    def adapt(self, data: dict) -> practice.config.dto.Students:
        return practice.config.dto.Students(
            manual=data['manual'],
            auto=data['auto']
        )


class ScheduleAdapter:
    def adapt(self, data: dict) -> practice.config.dto.Schedule:
        return practice.config.dto.Schedule(
            weekday=data['weekday'],
            start=data['interval']['start_time'].replace('.', ':'),
            end=data['interval']['end_time'].replace('.', ':'),
            start_date=data['interval']['start_date'],
            end_date=data['interval']['end_date'],
        )


class GroupAdapter:  # (mapper)
    def __init__(self):  # todo inject members instead
        self.students_adapter = StudentsAdapter()
        self.schedule_adapter = ScheduleAdapter()

    def adapt(self, data: dict) -> practice.config.dto.Group:
        return practice.config.dto.Group(
            name=data['name'],
            date_start=data['date_start'],
            examination_date=data['examination_date'],
            students=self.students_adapter.adapt(data['students']),
            schedule_list=[self.schedule_adapter.adapt(schedule) for schedule in data['schedule']]
        )


class TeacherAdapter:
    def adapt(self, data: dict) -> practice.config.dto.Teacher:
        return practice.config.dto.Teacher(
            count=data['count'],
            max_lessons_per_day=data['max_lessons_per_day']
        )


class WeekdayAdapter:
    def adapt(self, data: list) -> practice.config.dto.Weekend:

        weekend_list = []

        for date in data:
            date_interval_match = datetime_interval_re.match(date)

            if not date_interval_match:
                weekend_list.append(datetime.datetime.strptime(date, '%Y-%m-%d').date())
                continue

            date_interval_match_dict = date_interval_match.groupdict()

            start_date = date_interval_match_dict['start_date']
            end_date = date_interval_match_dict['end_date']

            cursor = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

            while True:
                weekend_list.append(cursor)

                if cursor.strftime('%Y-%m-%d') == end_date:  # FIXME !!!
                    break

                cursor += datetime.timedelta(days=1)

        return practice.config.dto.Weekend(weekend_list=weekend_list)


class ConfigAdapter:
    def __init__(self):  # todo inject members instead
        self.group_adapter = GroupAdapter()
        self.teacher_adapter = TeacherAdapter()
        self.weekday_adapter = WeekdayAdapter()

    def adapt(self, data: dict) -> practice.config.dto.Config:
        return practice.config.dto.Config(
            weekend=self.weekday_adapter.adapt(data=data['weekend']),
            teacher=self.teacher_adapter.adapt(data=data['teacher']),
            group_list=[self.group_adapter.adapt(data=group) for group in data['groups']]
        )
