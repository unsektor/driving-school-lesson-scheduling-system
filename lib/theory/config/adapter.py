import datetime
import theory.config.dto


class ScheduleAdapter:
    def adapt(self, data: dict) -> theory.config.dto.Schedule:
        return theory.config.dto.Schedule(
            weekday=data['weekday'],
            start=data['interval']['start_time'].replace('.', ':'),
            end=data['interval']['end_time'].replace('.', ':'),
        )


class GroupAdapter:  # (mapper)
    def __init__(self):  # todo inject members instead
        self.schedule_adapter = ScheduleAdapter()

    def adapt(self, data: dict) -> theory.config.dto.Group:
        return theory.config.dto.Group(
            name=data['name'],
            date_start=data['date_start'],
            lesson_count=int(data['lesson_count']),
            schedule_list=[self.schedule_adapter.adapt(schedule) for schedule in data['schedule']]
        )


class WeekdayAdapter:
    def adapt(self, data: list) -> theory.config.dto.Weekend:
        return theory.config.dto.Weekend(
            weekend_list=[datetime.datetime.strptime(date, '%Y-%m-%d').date() for date in data]
        )


class ConfigAdapter:
    def __init__(self):  # todo inject members instead
        self.group_adapter = GroupAdapter()
        self.weekday_adapter = WeekdayAdapter()

    def adapt(self, data: dict) -> theory.config.dto.Config:
        return theory.config.dto.Config(
            weekend=self.weekday_adapter.adapt(data=data['weekend']),
            group_list=[self.group_adapter.adapt(data=group) for group in data['groups']]
        )
