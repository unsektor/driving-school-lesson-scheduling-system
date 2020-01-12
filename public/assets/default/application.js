const Application = function () {
    const api_url = './api/report/lesson-schedule';

    // initialize dependencies. todo: use DI instead
    const groupFormBuilder = new GroupFormBuilder();
    const requestBuilder = new RequestBuilder();
    const scheduleRender = new ScheduleRender();

    // ui
    const application = document.querySelector('.application');
    const button = application.querySelector('.application__submit');
    const schedule = application.querySelector('.schedule');

    // bind ui
    groupFormBuilder.bind(application);
    button.addEventListener('click', function (e) {
        let data = requestBuilder.get_data(application);

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
};
