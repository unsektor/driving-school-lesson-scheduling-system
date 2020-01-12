const RequestBuilder = function() {
    function get_weekend_data(application_element) {
        let weekend_element = application_element.querySelector('.weekend');
        return weekend_element.value.split("\n");  // .filter()
    }

    function get_teacher_data(application_element) {
        let teacher_data = {};

        // 1.
        let teacher_count = application_element.querySelector('.teacher__count').value;
        teacher_data['count'] = parseInt(teacher_count);

        // 2.
        let max_lessons_per_day = application_element.querySelector('.teacher__max-lessons-per-day').value;
        teacher_data['max_lessons_per_day'] = parseInt(max_lessons_per_day);

        return teacher_data;
    }

    function get_group_students_data(group_element) {
        let group_students_data = {};

        group_students_data['manual'] = parseInt(group_element.querySelector('.group__student-manual-count').value);
        group_students_data['auto'] = parseInt(group_element.querySelector('.group__student-auto-count').value);

        return group_students_data;
    }

    function resolve_weekday(schedule_element) {
        for (let schedule_weekday_element of schedule_element.querySelectorAll('.group__schedule-weekday')) {
            if (schedule_weekday_element.checked) {
                return parseInt(schedule_weekday_element.value);
            }
        }

        return 0;
    }

    function get_group_schedule_data(schedule_element) {
        let schedule_data = {};

        schedule_data['weekday'] = resolve_weekday(schedule_element);
        schedule_data['interval'] = {
            "start_time": document.querySelector('.group__schedule-start-time').value,
            "end_time": document.querySelector('.group__schedule-end-time').value
        };

        return schedule_data;
    }

    function get_group_schedule_list_data(group_element) {
        let schedule_list = [];

        let schedule_element_list = group_element.querySelectorAll('.group__schedule');

        for (let schedule_element of schedule_element_list) {
            schedule_list.push(get_group_schedule_data(schedule_element));
        }

        return schedule_list;
    }

    function get_group_data(group_element) {
        let group_data = {};

        group_data['name'] = group_element.querySelector('.group__name').value;
        group_data['date_start'] = group_element.querySelector('.group__start-date').value;
        group_data['students'] = get_group_students_data(group_element);
        group_data['schedule'] = get_group_schedule_list_data(group_element);

        return group_data;
    }

    function get_groups_data(application_element) {
        let groups_data = [];

        let group_element_list = application_element.querySelectorAll('.group');

        for (let group_element of group_element_list) {
            groups_data.push(get_group_data(group_element));
        }

        return groups_data;
    }

    this.get_data = function(application_element) {
        let weekend_data = get_weekend_data(application_element);
        let teacher_data = get_teacher_data(application_element);
        let groups_data = get_groups_data(application_element);

        return {
            "weekend": weekend_data,
            "teacher": teacher_data,
            "groups": groups_data,
        };
    }
};
