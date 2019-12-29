import config.dto


class StudentsAdapter:
    def adapt(self, data: dict) -> config.dto.Students:
        students = config.dto.Students(
            manual=data['manual'],
            auto=data['auto']
        )
        return students


class ScheduleAdapter:
    def adapt(self, data: dict) -> config.dto.Schedule:
        schedule = config.dto.Schedule(
            weekday=data['weekday'],
            start=data['interval']['start_time'].replace('.', ':'),
            end=data['interval']['end_time'].replace('.', ':'),
        )
        return schedule


class GroupAdapter:  # (mapper)
    def __init__(self):
        self.students_adapter = StudentsAdapter()
        self.schedule_adapter = ScheduleAdapter()

    def adapt(self, data: dict) -> config.dto.Group:
        group = config.dto.Group(
            name=data['name'],
            date_start=data['date_start'],
            students=self.students_adapter.adapt(data['students']),
            schedule_list=[self.schedule_adapter.adapt(schedule) for schedule in data['schedule']]
        )
        return group


class TeacherAdapter:
    def adapt(self, data: dict) -> config.dto.Teacher:
        return config.dto.Teacher(count=data['count'])


class ConfigAdapter:
    def __init__(self):
        self.group_adapter = GroupAdapter()
        self.teacher_adapter = TeacherAdapter()

    def adapt(self, data: dict) -> config.dto.Config:
        return config.dto.Config(
            weekend_list=data['weekend'],
            teacher=self.teacher_adapter.adapt(data=data['teacher']),
            group_list=[self.group_adapter.adapt(data=group) for group in data['groups']]
        )
