const ScheduleRender = function () {
    function transform_data(data) {
        let transformed_data = {};
        for (let lesson of data) {
            if (undefined === transformed_data[lesson['teacher']]) {
                transformed_data[lesson['teacher']] = {/* month */};
            }

            // console.log(data)

            let lesson_date_start = new Date(lesson.interval[0].replace(' ', 'T'));
            let lesson_date_end = new Date(lesson.interval[1].replace(' ', 'T'));


            let scalar_lesson_date_start =
                lesson_date_start.getFullYear() + '-' +
                (lesson_date_start.getMonth() + 1 + '').padStart(2, '0') + '-' +
                (lesson_date_start.getDate() + '').padStart(2, '0');

            let interval =
                (lesson_date_start.getHours() + '').padStart(2, '0') + ':' +
                (lesson_date_start.getMinutes() + '').padStart(2, '0') + '-' +
                (lesson_date_end.getHours() + '').padStart(2, '0') + ':' +
                (lesson_date_end.getMinutes() + '').padStart(2, '0');

            if (undefined === transformed_data[lesson['teacher']][scalar_lesson_date_start]) {
                transformed_data[lesson['teacher']][scalar_lesson_date_start] = {};
            }

            transformed_data[lesson['teacher']][scalar_lesson_date_start][interval] = {
                student: lesson.student,
                type: lesson.type
            };
        }

        return transformed_data
    }

    function render_month(year, month, interval_list, data) {
        let month_days_count = (new Date(year, month, 0).getDate());  // https://stackoverflow.com/a/1184359
        let html = `<h2>${year}-${month}</h2>`;

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

            for (let i = 1; i <= month_days_count; i++) {
                let index = year + '-' + month.toString().padStart(2, '0') + '-' + i.toString().padStart(2, '0');

                let value = '';
                let style = '';

                // console.log(data);
                if (index in data) {
                    // value = interval
                    if (interval in data[index]) {
                        value = data[index][interval].student;
                        style = (data[index][interval].type === 0) ? 'style="background: #ddd"' : '';
                    }
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
        let month_set = new Set();  // 1,70 * 75
        for (let lesson_date of Object.keys(teacher_data)) {
            month_set.add(new Date(lesson_date).getMonth() + 1);
        }

        let html = `<h1>Преподавтель #${teacher}</h1>`;
        for (let month of month_set.values()) {
            html += render_month(2019, month, metadata, teacher_data);
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
