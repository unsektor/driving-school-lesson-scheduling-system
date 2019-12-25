function transform_data(data) {
    let transformed_data = {};
    for (let lesson of data) {
        if (undefined === transformed_data[lesson['teacher']]) {
            transformed_data[lesson['teacher']] = {/* month */};
        }

        let lesson_date_start = new Date(lesson.interval[0]);
        let lesson_date_end = new Date(lesson.interval[1]);

        let scalar_lesson_date_start =
            lesson_date_start.getFullYear() + '-' +
            (lesson_date_start.getMonth() + 1 + '').padStart(2, '0') + '-' +
            (lesson_date_start.getDate() + '').padStart(2, '0')
        ;

        let interval =
            (lesson_date_start.getHours() + '').padStart(2, '0') + ':' +
            (lesson_date_start.getMinutes() + '').padStart(2, '0') + '-' +
            (lesson_date_end.getHours() + '').padStart(2, '0') + ':' +
            (lesson_date_end.getMinutes() + '').padStart(2, '0');

        if (undefined === transformed_data[lesson['teacher']][scalar_lesson_date_start]) {
            transformed_data[lesson['teacher']][scalar_lesson_date_start] = {};
        }

        transformed_data[lesson['teacher']][scalar_lesson_date_start][interval] = lesson.student;
    }

    return transformed_data
}

function render_month(year, month, interval_list, data) {
    let month_days_count = (new Date(year, month, 0).getDate());  // https://stackoverflow.com/a/1184359
    let html = `<h2>${year}-${month+1}</h2>`;


    // <table>
    html += '<table>';

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

            // console.log(data);
            if (index in data) {
                // value = interval
                if (interval in data[index]) {
                    value = data[index][interval];
                }
            }

            html += '<td>' + value + '</td>'
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
    let month_set= new Set();  // 1,70 * 75
    for (let lesson_date of Object.keys(teacher_data)) {
        month_set.add(new Date(lesson_date).getMonth() + 1);
    }

    let html = `<h1>Преподавтель #${teacher}</h1>`;
    for (let month of month_set.values()) {
        html += render_month(2019, month, metadata, teacher_data);
    }

    return html;
}

let Application = function () {
    this.main = function (data) {
        const transformed_data = transform_data(data['data']);
        console.log(transformed_data);  // debug
        // let month_html = render_month(2019, 7, data['meta']['day_schedule'], transformed_data[1]);  // debug

        let html = '';
        for (let teacher of Object.keys(transformed_data)) {
            html += render_teacher(teacher, transformed_data[teacher], data['meta']['day_schedule']);
        }

        document.querySelector('#application').innerHTML += html;
    };
};

window.addEventListener('DOMContentLoaded', function (e) {
    const data = {
        "meta": {
            "day_schedule": [
                "06:00-08:00",
                "08:00-10:00",
                "10:00-12:00",
                "12:00-14:00",
                "14:00-16:00",
                "16:00-18:00",
                "18:00-20:00",
                "20:00-22:00",
                "22:00-00:00"
            ]
        },
        "data": [
            {
                "teacher": "1",
                "student": "13B_1",
                "interval": [
                    "2019-07-04 06:00:00",
                    "2019-07-04 08:00:00"
                ]
            },
            {
                "teacher": "1",
                "student": "13B_8",
                "interval": [
                    "2019-07-04 08:00:00",
                    "2019-07-04 10:00:00"
                ]
            }
        ]
    };

    let application = new Application();
    application.main(data);
});