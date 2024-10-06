taskDetailContainer = document.querySelector('#task-detail-container');
document.querySelectorAll("textarea").forEach(autoGrow);

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
        document.querySelectorAll("textarea").forEach(autoGrow);
    });
}

function autoGrow(element) {
    element.style.height = "auto";
    element.style.height = (element.scrollHeight-20)+"px";
    console.log(element.scrollHeight);
}