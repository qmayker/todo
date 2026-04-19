document.addEventListener('DOMContentLoaded', e=>{
    let checkbox = document.querySelector('input');
    let id = document.querySelector('.task').dataset.id;
    let options = {
        method: "POST",
        mode: "same-origin",
        headers : {
            "Content-Type": "application/json",
            "X-CSRFToken": Cookies.get('csrftoken')
        }
    };
    checkbox.addEventListener('click', e=>{
        let body = {'completed':checkbox.checked}; 
        options['body'] = JSON.stringify(body)
        fetch('/api/tasks/'+id+'/mark_completed/', options).then(
            (response) => {
                if (!response.ok){
                    throw response
                }
                return response.json()
            }
        ).then((data)=>{
            let textObject = document.querySelector('.checkbox p');
            let previousText = textObject.textContent;
            let newText = textObject.dataset.marktext;
            textObject.dataset.marktext = previousText;
            textObject.textContent = newText;
            
        })
    })
})