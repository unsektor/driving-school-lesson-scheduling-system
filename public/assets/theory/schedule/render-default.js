var state___  = {}

function get_group_class(group_name) {
    let i = Object.keys(state___).length

    if (undefined === state___[group_name]) {
        state___[group_name] = 'group_number_' + i
    }

    return state___[group_name];
}


let counter = {};
const weekday_shortname_list = ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс'];


const DefaultScheduleRender = function () {
    function transform_data(data) {
        let transformed_data = {};
        for (let lesson of data) {
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

            if (undefined === transformed_data[lesson_interval]) {
                transformed_data[lesson_interval] = []
            }

            transformed_data[lesson_interval].push({
                group: lesson.group,
                date: lesson_date,
                interval: lesson_interval,
            });
        }

        return transformed_data
    }

    function render_month(year, month, interval_list, lesson_map) {
        console.log(lesson_map)

        let month_days_count = (new Date(year, month+1, 0).getDate());  // https://stackoverflow.com/a/1184359
        let html = `<h2>${year}-${(month+1).toString().padStart(2, '0')}</h2>`;

        // <table>
        html += '<table class="schedule__month">';

        // <tbody>
	    html += '<thead><tr><td></td>';

        for (let i = 1; i <= month_days_count; i++) {
            let day_of_week = new Date(year, month, i).getDay();

            html += '<td>' + i + ' (' + weekday_shortname_list[day_of_week] + ')</td>'
        }
        html += '</tr></thead>'
        // </thead>

        // <tbody>
        html += '<tbody>';
        // let counter = {}
        for (let interval of interval_list) {
            html += '<tr>';
            html += `<td class="schedule__date-interval">${interval}</td>`;

            for (let day = 1; day <= month_days_count; day++) {
                let class_ = '';
                let data = '';

                if (day+interval in lesson_map) {
                    let lesson_list = lesson_map[day+interval];


                    for (let lesson of lesson_list) {
                        if (undefined === counter[lesson.group]) {
                            counter[lesson.group] = 0;
                        }

                        counter[lesson.group] += 1;

                        // let lesson_type = lesson_list.type;

                        class_ += ' lesson ';
                        class_ += get_group_class(lesson.group)
                        data += `<div class="group_ ${class_}">${lesson.group} (${counter[lesson.group]})</div>`;
                    }
                }

                html += `<td>${data}</td>`
            }
            html += '</tr>';
        }
        html += '</tbody>';
        // </tbody>

        html += '</table>';
        // </table>

        return html;
    }

    function render_schedule(lesson_interval_lesson_list_map, metadata) {
        let month_set = {};  // lesson_interval_lesson_list_map = Dict[str, List[Lesson]]

        // console.log(lesson_interval_lesson_list_map)

        for (let lesson_list of Object.keys(lesson_interval_lesson_list_map)) {
            for (let lesson of lesson_interval_lesson_list_map[lesson_list]) {
                let key = lesson.date.year + '-' + lesson.date.month.toString().padStart(2, '0');

                if (undefined === month_set[key]) {
                    month_set[key] = {
                        year: lesson.date.year,
                        month: lesson.date.month,
                        group: lesson.group,
                        lessons: {}
                    };
                }

                if (undefined === month_set[key].lessons[lesson.date.day + lesson.interval]) {
                    month_set[key].lessons[lesson.date.day + lesson.interval] = []
                }

                month_set[key].lessons[lesson.date.day + lesson.interval].push(lesson)
            }
        }

        console.log(month_set)

        let html = '';

        for (let key of Object.keys(month_set).sort()) {
            html += render_month(month_set[key].year, month_set[key].month, metadata, month_set[key].lessons);
        }

        return html;
    }

    this.render = function (data) {
        const transformed_data = transform_data(data['data']);

        console.log(transformed_data)

        return render_schedule(transformed_data, data['meta']['day_schedule']);
    };
};
