const RING_LESSON_TYPE = 0;
const CITY_LESSON_TYPE = 1;
const INTERNAL_EXAMINATION_LESSON_TYPE = 2;

// colorizes student lesson with color assigned to group
let _group_css_class_map = {}
function get_group_class(group_name) {
    let assigned_css_class_group_count = Object.keys(_group_css_class_map).length

    if (undefined === _group_css_class_map[group_name]) {
        _group_css_class_map[group_name] = 'group_number_' + assigned_css_class_group_count
    }

    return _group_css_class_map[group_name];
}

const TeacherScheduleRender = function () {
    function transform_data(data) {
        let transformed_data = {};
        for (let lesson of data) {
            if (undefined === transformed_data[lesson['teacher']]) {
                transformed_data[lesson['teacher']] = [];
            }

            let lesson_date_start = new Date(lesson.interval[0].replace(' ', 'T'));
            let lesson_date_end = new Date(lesson.interval[1].replace(' ', 'T'));

            let lesson_date = {
                year: lesson_date_start.getFullYear(),
                month: lesson_date_start.getMonth(),
                day: lesson_date_start.getDate(),
            };

            let lesson_interval =
                (lesson_date_start.getHours() + '').padStart(2, '0') + ':' +
                (lesson_date_start.getMinutes() + '').padStart(2, '0') + '-' +
                (lesson_date_end.getHours() + '').padStart(2, '0') + ':' +
                (lesson_date_end.getMinutes() + '').padStart(2, '0');

            transformed_data[lesson['teacher']].push({
                date: lesson_date,
                interval: lesson_interval,
                student: lesson.student,
                type: lesson.type,
                group: lesson.group
            });
        }

        return transformed_data
    }

    function render_month(year, month, metadata, lesson_map) {
        let month_days_count = (new Date(year, month, 0).getDate());  // https://stackoverflow.com/a/1184359
        let html = `<h2>${year}-${(month+1).toString().padStart(2, '0')}</h2>`;

        // <table>
        html += '<table class="schedule__month">';

        // <thead>
        html += '<thead><tr><td></td>'
        for (let day = 1; day <= month_days_count; day++) {
            html += `<td>${day}</td>`
        }
        html += '</tr></thead>'
        // </thead>

        // <tbody>
        html += '<tbody>';

        for (let interval of metadata['day_schedule']) {
            html += '<tr>';
            html += `<td class="schedule__date-interval">${interval}</td>`;

            for (let day = 1; day <= month_days_count; day++) {
                let scalar_lesson_day_date = year + '-' + (month + 1).toString().padStart(2, '0') + '-' + day.toString().padStart(2, '0');

                if (metadata['weekend_list'].includes(scalar_lesson_day_date)) {
                    html += '<td class="schedule__weekend"></td>'
                    continue;
                }

                if (day + interval in lesson_map) {
                    let lesson = lesson_map[day + interval];

                    let class_ = 'lesson ';
                    if (lesson.type === RING_LESSON_TYPE) {
                        class_ += ' lesson_type_ring ';
                    } else if (lesson.type === CITY_LESSON_TYPE) {
                        class_ += ' lesson_type_city ';
                    } else if (lesson.type === INTERNAL_EXAMINATION_LESSON_TYPE) {
                        class_ += ' lesson_type_internal_examination '
                    }

                    class_ += get_group_class(lesson.group)

                    html += `<td><div class="group_ ${class_}">${lesson.student}</div></td>`;
                    continue;
                }

                html += '<td></td>'

            }
            html += '</tr>';
        }
        html += '</tbody>';
        // </tbody>

        html += '</table>';
        // </table>

        return html;
    }

    function render_teacher(teacher, lesson_list, metadata) {
        let month_map = {};
        for (let lesson of lesson_list) {
            let key = lesson.date.year + '-' + lesson.date.month.toString().padStart(2, '0');

            if (undefined === month_map[key]) {
                month_map[key] = {
                    year: lesson.date.year,
                    month: lesson.date.month,
                    lessons: {}
                };
            }

            month_map[key].lessons[lesson.date.day + lesson.interval] = lesson
        }

        let html = `<h1>Преподавтель #${teacher}</h1>`;
        for (let key of Object.keys(month_map).sort()) {
            html += render_month(
                month_map[key].year,
                month_map[key].month,
                metadata,
                month_map[key].lessons,
            );
        }

        return html;
    }

    this.render = function (data) {
        const teacher_lesson_map = transform_data(data['data']);

        let html = '';
        for (let teacher of Object.keys(teacher_lesson_map)) {
            html += render_teacher(teacher, teacher_lesson_map[teacher], data['meta']);
        }

        return html;
    };
};
