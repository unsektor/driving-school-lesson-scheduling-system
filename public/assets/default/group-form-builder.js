const GroupFormBuilder = function () {
    const group_template = document.getElementById('template__group');
    const group_schedule_template = document.getElementById('template__group-schedule');

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
                    let container = document.importNode(group_schedule_template.content, true);
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
                    let group = document.importNode(group_template.content, true);

                    bind_group_remove_schedule(group);
                    bind_group_add_schedule(group);
                    bind_group_remove(group);

                    group_container.appendChild(group)
                }
            })
        });
    }
};
