const Application = function () {
    const api_url = './api/report/lesson-schedule';

    // initialize dependencies. todo: use DI instead
    const formBuilder = new FormBuilder();
    const formSerializer = new FormSerializer(formBuilder);
    const scheduleRender = new ScheduleRender();

    // ui
    const application = document.querySelector('.application');
    const button = application.querySelector('.application__submit');
    const schedule = application.querySelector('.schedule');

    // bind ui
    formBuilder.bind(application);
    button.addEventListener('click', function (e) {
        let data = formSerializer.get_data(application);

        schedule.innerText = '';  // clear

        fetch(new Request(api_url, {method: 'POST', body: JSON.stringify(data)}))
            .then(response => {
                if (response.status === 200) {
                    return response.json();
                }
                throw new Error('Something went wrong on api server!');
            })
            .then(data => schedule.innerHTML = scheduleRender.render(data));
    });

    // restore last state
    const key = 'land.md.9ef1df6f-f6b3-4ff2-8273-f7d910ea8567';
    const savedState = localStorage.getItem(key);
    if (null !== savedState) {
        formSerializer.set_data(application, JSON.parse(savedState))
    }

    setInterval(function () {  // may conflict with form loading from storage!
        localStorage.setItem(key, JSON.stringify(formSerializer.get_data(application)));
    }, 3000);
};
