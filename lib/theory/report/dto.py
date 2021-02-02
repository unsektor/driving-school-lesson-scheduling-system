import typing

import date
import domain


class Markup:
    def __init__(self):
        self.city: typing.Dict[str, typing.List[date.DateTimeInterval]] = None
        self.ring: typing.Dict[str, typing.List[date.DateTimeInterval]] = None


class Schedule:
    def __init__(self):
        self.markup: Markup = None
        self.lesson_iterable: typing.Iterable[domain.Lesson] = None
