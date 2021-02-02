const Application = function () {
    const api_url = './api/report/theory-lesson-schedule';

    // initialize dependencies. todo: use DI instead
    const formBuilder = new FormBuilder();
    const formSerializer = new FormSerializer(formBuilder);

    // ui
    const application = document.querySelector('.application');
    const button = application.querySelector('.application__submit');

    const schedule_type = application.querySelector('.schedule-type');
    const schedule = application.querySelector('.schedule');

    // bind ui
    formBuilder.bind(application);

    const render = new function () {   // todo generalize with render contract
        const defaultScheduleRender = new DefaultScheduleRender();  // todo generalize with render contract

        const render_map = {
            'default': defaultScheduleRender,
        };

        this.render = function (data, render_type) {
            const render = render_map[render_type];

            if (undefined === render) {
                throw new Error('Undefined render type ' + render_type);  // Should never happen
            }

            return render.render(data);
        }
    };

    function resolve_render_type(render_type) {
        return 'default';
    }

    button.addEventListener('click', function (e) {
        const data = formSerializer.get_data(application);
        const render_type = resolve_render_type(schedule_type);

        schedule.innerText = '';  // clear

        fetch(new Request(api_url, {method: 'POST', body: JSON.stringify(data)}))
            .then(response => {
                if (response.status === 200) {
                    return response.json();
                }
                throw new Error('Something went wrong on api server!');
            })
            .then(data => schedule.innerHTML = render.render(data, render_type));
    });

    // restore last state
    const key = 'land.md.9ef1df6f-f6b3-4ff2-8273-f7d910ea8567.theory';
    const savedState = localStorage.getItem(key);
    if (null !== savedState) {
        formSerializer.set_data(application, JSON.parse(savedState))
    }

    setInterval(function () {  // may conflict with form loading from storage!
        localStorage.setItem(key, JSON.stringify(formSerializer.get_data(application)));
    }, 3000);
};
