taskDetailContainer = document.querySelector('#task-detail-container');

function getTaskDetail(tasksListItem) {
    const url = tasksListItem.dataset.url;
    var options = {
        method: 'GET',
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        }
    }

    fetch(url, options)
    .then(response => response.json())
    .then(data => {
        taskDetailContainer.innerHTML = data['form'];
        window.history.replaceState(null, document.title, data['url']);
    });
}