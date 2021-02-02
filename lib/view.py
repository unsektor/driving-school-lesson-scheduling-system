import typing
import domain


class Lesson(dict):
    pass


class ViewBuilderInterface:
    def build(self, lesson_generator: typing.Iterator[domain.Lesson]):
        raise NotImplementedError


class ViewBuilder(ViewBuilderInterface):
    def build(self, lesson_generator: typing.Iterator[domain.Lesson]):
        lesson_list = []

        for lesson in lesson_generator:
            lesson_list.append(Lesson({
                'teacher': lesson.teacher.name,
                'student': lesson.student.name,
                'interval': [
                    lesson.interval.start.strftime('%Y-%m-%d %H:%M:00'),
                    lesson.interval.end.strftime('%Y-%m-%d %H:%M:00')
                ],
                'type': lesson.type,
                'group': lesson.student.group_.name,
            }))

        return lesson_list
