// serializes DOM form to JSON & vice versa
const FormSerializer = function(groupFormBuilder) {
    const weekend = new function () {
        this.get = function(application_element) {
            let weekend_element = application_element.querySelector('.weekend');
            return weekend_element.value.split("\n")
                .filter(value => value !== '')
                .map(value => value.trim())
        };

        this.set = function(application_element, value) {
           let weekend_element = application_element.querySelector('.weekend');
           weekend_element.value = value.join("\n")
        };
    };

    function resolve_weekday(schedule_element) {
        for (let schedule_weekday_element of schedule_element.querySelectorAll('.group__schedule-weekday')) {
            if (schedule_weekday_element.checked) {
                return parseInt(schedule_weekday_element.value);
            }
        }

        return 0;
    }

    const group_schedule = new function () {
        this.get = function (schedule_element) {
            let schedule_data = {};

            schedule_data['weekday'] = resolve_weekday(schedule_element);
            schedule_data['interval'] = {
                "start_time": schedule_element.querySelector('.group__schedule-start-time').value.trim(),
                "end_time": schedule_element.querySelector('.group__schedule-end-time').value.trim()
            };

            return schedule_data;
        };

        this.set = function (schedule_element, value) {
            schedule_element.querySelector(`.group__schedule-weekday[value="${value['weekday']}"]`).checked = true;
            schedule_element.querySelector('.group__schedule-start-time').value = value['interval']['start_time'].trim();
            schedule_element.querySelector('.group__schedule-end-time').value = value['interval']['end_time'].trim();
        }
    };

    const group_schedules = new function () {
        this.get = function (group_element) {
            let schedule_list = [];

            let schedule_element_list = group_element.querySelectorAll('.group__schedule');

            for (let schedule_element of schedule_element_list) {
                schedule_list.push(group_schedule.get(schedule_element));
            }

            return schedule_list;
        };

        this.set = function (group_element, value) {
            const group_schedule_list = group_element.querySelector('.group__schedule-list');

            for (let schedule_ of value) {
                let schedule_element = groupFormBuilder.add_group_schedule(group_schedule_list);
                group_schedule.set(schedule_element, schedule_)
            }
        }
    };

    const group = new function () {
        this.get = function (group_element) {
            let group_data = {};

            group_data['name'] = group_element.querySelector('.group__name').value.trim();
            group_data['date_start'] = group_element.querySelector('.group__start-date').value.trim();
            group_data['lesson_count'] = group_element.querySelector('.group__lesson-count').value.trim();
            group_data['schedule'] = group_schedules.get(group_element);

            return group_data;
        };

        this.set = function (group_element, value) {
            group_element.querySelector('.group__name').value = value['name'];
            group_element.querySelector('.group__start-date').value = value['date_start'];
            group_element.querySelector('.group__lesson-count').value = value['lesson_count'];

            group_schedules.set(group_element, value['schedule']);
        }
    };

    const groups = new function () {
        this.get = function (application_element) {
            let groups_data = [];

            let group_element_list = application_element.querySelectorAll('.group');

            for (let group_element of group_element_list) {
                groups_data.push(group.get(group_element));
            }

            return groups_data;
        };

        this.set = function (application_element, value) {
            const group_container = application_element.querySelector('.group-container');

            for (let group_ of value) {
                let group_element = groupFormBuilder.add_group(group_container);
                group.set(group_element, group_)
            }
        };
    };

    this.get_data = function(application_element) {  // todo consider to rename to `serialize` / unserialize
        return {
            "weekend": weekend.get(application_element),
            "groups": groups.get(application_element),
        };
    };

    this.set_data = function(application_element, value) {
        weekend.set(application_element, value['weekend']);
        groups.set(application_element, value['groups']);
    };
};
