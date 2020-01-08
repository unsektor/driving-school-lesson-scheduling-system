import json
import typing

import config
import config.dto
import config.adapter

import sandbox
import report.lesson_schedule
import view
from domain import Teacher, Lesson


def main():
    with open('../etc/schedule/test-data.json') as f:
        data = json.load(f)

    config_adapter = config.adapter.ConfigAdapter()
    config_ = config_adapter.adapt(data=data)

    # main
    teacher_list = [Teacher(name=str(i + 1)) for i in range(0, config_.teacher.count)]
    group_list = [sandbox.create_group(group_config=group_config) for group_config in config_.group_list]

    report.lesson_schedule.assign_students_on_teachers(
        group_list=group_list,
        teacher_list=teacher_list,
    )

    def lesson_generator_() -> typing.Iterator[Lesson]:
        for teacher in teacher_list:
            yield from report.lesson_schedule.schedule_by_teacher(teacher=teacher, config_=config_)

    lesson_generator = lesson_generator_()

    # view
    view_builder = view.ViewBuilder()
    data = view_builder.build(lesson_generator)

    response = {
        "meta": {
            "day_schedule": [f'{start!s}-{end!s}' for start, end in report.lesson_schedule.DAY_WORK_HOUR_INTERVAL_LIST]
        },
        "data": data,
    }

    raw_response = json.dumps(response)
    print(raw_response)


if __name__ == '__main__':
    main()
