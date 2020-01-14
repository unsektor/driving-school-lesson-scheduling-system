import datetime
import config.dto


class StudentsAdapter:
    def adapt(self, data: dict) -> config.dto.Students:
        return config.dto.Students(
            manual=data['manual'],
            auto=data['auto']
        )


class ScheduleAdapter:
    def adapt(self, data: dict) -> config.dto.Schedule:
        return config.dto.Schedule(
            weekday=data['weekday'],
            start=data['interval']['start_time'].replace('.', ':'),
            end=data['interval']['end_time'].replace('.', ':'),
        )


class GroupAdapter:  # (mapper)
    def __init__(self):  # todo inject members instead
        self.students_adapter = StudentsAdapter()
        self.schedule_adapter = ScheduleAdapter()

    def adapt(self, data: dict) -> config.dto.Group:
        return config.dto.Group(
            name=data['name'],
            date_start=data['date_start'],
            students=self.students_adapter.adapt(data['students']),
            schedule_list=[self.schedule_adapter.adapt(schedule) for schedule in data['schedule']]
        )


class TeacherAdapter:
    def adapt(self, data: dict) -> config.dto.Teacher:
        return config.dto.Teacher(
            count=data['count'],
            max_lessons_per_day=data['max_lessons_per_day']
        )


class WeekdayAdapter:
    def adapt(self, data: list) -> config.dto.Weekend:
        return config.dto.Weekend(
            weekend_list=[datetime.datetime.strptime(date, '%Y-%m-%d').date() for date in data]
        )


class ConfigAdapter:
    def __init__(self):  # todo inject members instead
        self.group_adapter = GroupAdapter()
        self.teacher_adapter = TeacherAdapter()
        self.weekday_adapter = WeekdayAdapter()

    def adapt(self, data: dict) -> config.dto.Config:
        return config.dto.Config(
            weekend=self.weekday_adapter.adapt(data=data['weekend']),
            teacher=self.teacher_adapter.adapt(data=data['teacher']),
            group_list=[self.group_adapter.adapt(data=group) for group in data['groups']]
        )
