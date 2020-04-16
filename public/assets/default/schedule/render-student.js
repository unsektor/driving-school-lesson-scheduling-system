const StudentScheduleRender = function () {
    function transform_data(data) {
        let transformed_data = {};
        for (let lesson of data) {
            if (undefined === transformed_data[lesson['student']]) {
                transformed_data[lesson['student']] = [];
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

            transformed_data[lesson['student']].push({
                date: lesson_date,
                interval: lesson_interval,
                teacher: lesson.teacher,
                type: lesson.type
            });
        }

        return transformed_data
    }

    function render_student(student, lesson_list) {
        let html = `<h1>Ученик #${student}</h1>`;

        // <table>
        html += '<table class="">';

        // <thead>
        html += '<thead><tr>';
        html += '<td>#</td>';
        html += '<td>Дата</td>';
        html += '<td>Интервал</td>';
        html += '<td>Тип</td>';
        html += '</tr></thead>'
        // </thead>

        // <tbody>
        html += '<tbody>';

        const day_of_week = 'TBD'

        let i = 0;
        for (let lesson of lesson_list) {
            let style = '';


            if (lesson.type === 0) {
                style = 'style="background: #ddd"';
            } else if (lesson.type === 2) {
                style = 'style="background: #900"; color: #fff';
            }

            html += '<tr>';
            html += `<td>${++i}</td>`;
            html += `<td ${style}>${lesson.date.year}.${lesson.date.month+1}.${lesson.date.day} (${day_of_week})</td>`;
            html += `<td ${style}>${lesson.interval}</td>`;

            let type;
            if (lesson.type === 0) {
                type = 'площадка';
            } else if (lesson.type === 1) {
                type = 'город';
            } else if (lesson.type === 2) {
                type = 'внутренний экзамен';
            }

            html += `<td>${type}</td>`;
            html += '</tr>';
        }
        html += '</tbody>';
        // </tbody>

        html += '</table>';
        // </table>

        return html;
    }

    this.render = function (data) {
        const transformed_data = transform_data(data['data']);

        let html = '';
        for (let student of Object.keys(transformed_data)) {
            html += render_student(student, transformed_data[student]);
        }

        return html;
    };
};
