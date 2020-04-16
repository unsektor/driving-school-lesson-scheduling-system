import unittest
import unittest.mock

import config.adapter


class StudentsAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.students_adapter = config.adapter.StudentsAdapter()

    def test_adapt(self):
        students = self.students_adapter.adapt(data={
            'manual': 42,
            'auto': 23,
        })

        self.assertEqual(students.manual, 42)
        self.assertEqual(students.auto, 23)


class GroupAdapterTest(unittest.TestCase):
    def test_adapt(self):
        data = {
            "name": "42x",
            "date_start": "2019-01-01",
            "date_start": "2019-01-02",
            "students": {},
            "schedule_list": [],
        }

        with unittest.mock.patch('config.adapter.StudentsAdapter') as StudentsAdapterMock, \
             unittest.mock.patch('config.adapter.ScheduleAdapter') as ScheduleAdapterMock:
            students_adapter = StudentsAdapterMock.return_value
            students_adapter.adapt.return_value = []

            schedule_adapter = ScheduleAdapterMock.return_value
            schedule_adapter.adapt.return_value = []

            group_adapter = config.adapter.GroupAdapter()
            group = group_adapter.adapt(data=data)

            self.assertEqual(group.name, "42x")
            self.assertEqual(group.date_start, "2019-01-01")
            self.assertEqual(group.examination_date, "2019-01-02")
            self.assertEqual(group.students, [])
            self.assertEqual(group.schedule_list, [])


if __name__ == '__main__':
    unittest.main()
