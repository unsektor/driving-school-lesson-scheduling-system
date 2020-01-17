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
                type: lesson.type
            });
        }

        return transformed_data
    }

    function render_month(year, month, interval_list, lesson_map) {
        let month_days_count = (new Date(year, month, 0).getDate());  // https://stackoverflow.com/a/1184359
        let html = `<h2>${year}-${(month+1).toString().padStart(2, '0')}</h2>`;

        // <table>
        html += '<table class="schedule__month">';

        // <thead>
        html += '<thead><tr><td></td>'
        for (var i = 1; i <= month_days_count; i++) {
            html += '<td>' + i + '</td>'
        }
        html += '</tr></thead>'
        // </thead>

        // <tbody>
        html += '<tbody>';
        for (let interval of interval_list) {
            html += '<tr>';
            html += `<td>${interval}</td>`;

            for (let day = 1; day <= month_days_count; day++) {
                let value = '';
                let style = '';

                if (day+interval in lesson_map) {
                    value = lesson_map[day+interval].student;
                    style = (lesson_map[day+interval].type === 0) ? 'style="background: #ddd"' : '';
                }

                html += `<td ${style}>${value}</td>`
            }
            html += '</tr>';
        }
        html += '</tbody>';
        // </tbody>

        html += '</table>';
        // </table>

        return html;
    }

    function render_teacher(teacher, teacher_data, metadata) {
        let month_set = {};
        for (let lesson of teacher_data) {
            let key = lesson.date.year+'-'+lesson.date.month.toString().padStart(2, '0');

            if (undefined === month_set[key]) {
                month_set[key] = {
                    year: lesson.date.year,
                    month: lesson.date.month,
                    lessons: {}
                };
            }

            month_set[key].lessons[lesson.date.day + lesson.interval] = lesson
        }

        let html = `<h1>Преподавтель #${teacher}</h1>`;
        for (let key of Object.keys(month_set).sort()) {
            html += render_month(month_set[key].year, month_set[key].month, metadata, month_set[key].lessons);
        }

        return html;
    }

    this.render = function (data) {
        const transformed_data = transform_data(data['data']);

        let html = '';
        for (let teacher of Object.keys(transformed_data)) {
            html += render_teacher(teacher, transformed_data[teacher], data['meta']['day_schedule']);
        }

        return html;
    };
};
