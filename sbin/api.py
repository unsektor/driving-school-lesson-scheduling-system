#!/usr/bin/env python3

import typing
import json

import bottle

from domain import Lesson, Teacher
import view

# practice
import practice.sandbox
import practice.report.lesson_schedule
import practice.config.adapter


def _create_lesson_schedule(data: dict):
    # model
    config_adapter = practice.config.adapter.ConfigAdapter()
    config_ = config_adapter.adapt(data=data)

    teacher_list = [Teacher(name=str(i + 1)) for i in range(0, config_.teacher.count)]
    group_list = [practice.sandbox.create_group(group_config=group_config) for group_config in config_.group_list]

    practice.report.lesson_schedule.assign_students_on_teachers(
        group_list=group_list,
        teacher_list=teacher_list,
    )

    def lesson_generator_() -> typing.Iterator[Lesson]:
        for teacher in teacher_list:
            # if teacher.name != '5': continue  # FIXME !!!!!!!!!!!

            dto = practice.report.lesson_schedule.schedule_by_teacher(teacher=teacher, config_=config_)
            yield from dto.lesson_iterable

    lesson_generator = lesson_generator_()

    # view
    view_builder = view.ViewBuilder()
    data_view = view_builder.build(lesson_generator)

    day_schedule = [f'{start!s}-{end!s}' for start, end in practice.report.lesson_schedule.DAY_WORK_HOUR_INTERVAL_LIST]
    return {
        "meta": {
            "day_schedule": day_schedule,
            "weekend_list": [weekend.strftime('%Y-%m-%d') for weekend in config_.weekend.weekend_list]
        },
        "data": data_view,
    }


@bottle.post('/api/report/lesson-schedule')
def report_lesson_schedule():  # controller
    try:
        data = json.load(bottle.request.body)
    except json.JSONDecodeError:
        bottle.response.status = 400
        return

    bottle.response.content_type = 'application/json; charset=utf8'
    return json.dumps(_create_lesson_schedule(data))


if __name__ == '__main__':
    bottle.run(host='localhost', port=8080, debug=True, reloader=True)
else:
    bottle.debug(True)
    app = application = bottle.default_app()
