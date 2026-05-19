document.addEventListener('DOMContentLoaded', e=>{
    let tasks = document.querySelector("#tasks");
    tasks.addEventListener('click', e=>{
        let target = e.target;
        if (target.className !== 'type'){
            return
        }
        else {
            e.preventDefault()
            let taskType = target.dataset.type;
            let state = target.dataset.state;
            let tasksDiv = document.querySelector(`.${taskType} .tasks`);
            if (state==="shown"){
                tasksDiv.innerHTML = "";
                target.dataset.state = "hidden";
                return
            }
            let url = `${window.location.origin}/api/tasks/get_category/?cat=${taskType}` ;
            fetch(url).then(
                (response)=>{
                    return response.json();
                }
            ).then((data)=>{
                let tasks = "";
                const fragment = document.createDocumentFragment();
                console.log(data);
                data.forEach(element => {
                    const a = document.createElement('a');
                    const p = document.createElement('p');
                    a.href = element.url;
                    p.textContent = element.name;
                    a.appendChild(p);
                    fragment.appendChild(a);
                });
                tasksDiv.innerHTML = ""
                tasksDiv.appendChild(fragment)
            })
            target.dataset.state = "shown";
        }

    })
})