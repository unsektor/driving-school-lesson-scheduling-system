const GroupFormBuilder = function () {
    let group_template =
        '<table class="group">' +
        '    <tr>' +
        '        <td>Название группы</td>' +
        '        <td><input type="text" class="group__name" placeholder="13B" required/></td>' +
        '    </tr>' +
        '    <tr>' +
        '        <td>Дата начала обучения</td>' +
        '        <td><input type="text" class="group__start-date" placeholder="yyyy-mm-dd (eg. 2019-06-30)" required/></td>' +
        '    </tr>' +
        '    <tr>' +
        '        <td>Ученики</td>' +
        '        <td>' +
        '            <table>' +
        '                <tr>' +
        '                    <td>Механика</td>' +
        '                    <td><input type="text" class="group__student-manual-count" placeholder="14" required/></td>' +
        '                </tr>' +
        '                <tr>' +
        '                    <td>Автомат</td>' +
        '                    <td><input type="text" class="group__student-auto-count" placeholder="4" required/></td>' +
        '                </tr>' +
        '            </table>' +
        '        </td>' +
        '    </tr>' +
        '    <tr>' +
        '        <td>Расписание</td>' +
        '        <td class="group__schedule-list">' +
        '            <a class="group__schedule-add" href="javascript://">Добавить расписание</a>' +
        '        </td>' +
        '    </tr>' +
        '    <tr>' +
        '        <td colspan="2">' +
        '            <a class="group__remove" href="javascript://">Удалить группу</a>' +
        '        </td>' +
        '    </tr>' +
        '</table>';

    let group_schedule_template =
        '<div class="group__schedule"><table class="group__schedule-table">' +
        '    <tr>' +
        '        <td>День недели</td>' +
        '        <td>' +
        '            <label><input type="radio" class="group__schedule-weekday" value="0">понедельник</label>' +
        '            <label><input type="radio" class="group__schedule-weekday" value="1">вторник</label>' +
        '            <label><input type="radio" class="group__schedule-weekday" value="2">среда</label>' +
        '            <label><input type="radio" class="group__schedule-weekday" value="3">четверг</label>' +
        '            <label><input type="radio" class="group__schedule-weekday" value="4">пятница</label>' +
        '            <label><input type="radio" class="group__schedule-weekday" value="5">суббота</label>' +
        '            <label><input type="radio" class="group__schedule-weekday" value="6">воскресение</label>' +
        '        </td>' +
        '    </tr>' +
        '    <tr>' +
        '        <td>время</td>' +
        '        <td>' +
        '            <table>' +
        '                <tr>' +
        '                    <td>начало</td>' +
        '                    <td><input class="group__schedule-start-time" type="text" placeholder="12:00"/></td>' +
        '                </tr>' +
        '                <tr>' +
        '                    <td>конец</td>' +
        '                    <td><input class="group__schedule-end-time" type="text" placeholder="14:00"/></td>' +
        '                </tr>' +
        '            </table>' +
        '        </td>' +
        '    </tr>' +
        '    <tr>' +
        '        <td colspan="2">' +
        '            <a class="group__schedule-remove" href="javascript://">Удалить расписание</a>' +
        '        </td>' +
        '    </tr>' +
        '</table></div>';


    function _uuid() {
        // https://www.w3resource.com/javascript-exercises/javascript-math-exercise-23.php
        var dt = new Date().getTime();
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            var r = (dt + Math.random() * 16) % 16 | 0;
            dt = Math.floor(dt / 16);
            return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
    }

    function _lookup_parent_element_by_class_name(element, class_name) {
        for (let element_ = element; !!element_; element_ = element_.parentElement) {
            if (element_.classList.contains(class_name)) {
                return element_;
            }
        }
        return null;
    }

    function bind_group_add_schedule(element) {
        element.querySelectorAll('.group__schedule-add').forEach(function (element) {
            element.addEventListener('click', function (e) {
                e.preventDefault();

                let group_schedule_list = _lookup_parent_element_by_class_name(e.target, 'group__schedule-list');
                if (!!group_schedule_list) {
                    let container_uuid = _uuid();
                    let container = document.createRange().createContextualFragment(group_schedule_template);
                    container.querySelectorAll('input').forEach((e) => e.name = container_uuid);

                    bind_group_remove_schedule(container);
                    group_schedule_list.appendChild(container)
                }

            })
        });
    }

    function bind_group_remove_schedule(element) {
        element.querySelectorAll('.group__schedule-remove').forEach(function (element) {
            element.addEventListener('click', function (e) {
                e.preventDefault();

                let group_schedule = _lookup_parent_element_by_class_name(e.target, 'group__schedule');
                if (!!group_schedule) {
                    group_schedule.parentElement.removeChild(group_schedule)
                }
            })
        });
    }

    function bind_group_remove(element) {
        element.querySelectorAll('.group__remove').forEach(function (element) {
            element.addEventListener('click', function (e) {
                e.preventDefault();

                let group = _lookup_parent_element_by_class_name(e.target, 'group');
                if (!!group) {
                    group.parentElement.removeChild(group)
                }
            })
        });
    }

    this.bind = function (element) {
        element.querySelectorAll('.group__add').forEach(function (element) {
            element.addEventListener('click', function (e) {
                e.preventDefault();

                let group_container = _lookup_parent_element_by_class_name(e.target, 'group-container');
                if (!!group_container) {
                    let group = document.createRange().createContextualFragment(group_template);

                    bind_group_remove_schedule(group);
                    bind_group_add_schedule(group);
                    bind_group_remove(group);

                    group_container.appendChild(group)
                }
            })
        });
    }
};
