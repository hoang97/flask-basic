const action_menu_btn = document.getElementById('action_menu_btn');
const room_name_disp = document.getElementById('room_name');
const message_count_disp = document.getElementById('message_count');
const submit_btn = document.getElementById('send_btn');
const message_input = document.getElementById('message_input');
const message_log = document.getElementById('message_log');
const home_btn = document.getElementById('home_btn');

room_name_disp.innerText = data.room_name;

const getRelativeTime = (timestamp) => {
    if (timestamp.isBefore(moment().subtract(1, 'w'))){
        return timestamp.format('LT, L')
    }
    else {
        return timestamp.fromNow()
    }
};

async function send_data(data) {
    // POST data to short_url (pre-defined in chat.html)
    let formData = new URLSearchParams(data)
    response = await fetch(short_url, {
        method: 'POST',
        body: formData
    });
    return response.json();
};

async function get_data(info) {
    // GET data from short_url (pre-defined in chat.html)
    url_with_data = new URL(short_url);
    url_with_data.search = new URLSearchParams(info);
    response = await fetch(url_with_data);
    return response.json();
};

function createMessage(data) {
    // Create and Add 1 message to messageLog
    let username = data.username;
    let message = data.message;
    let timestamp = moment(data.timestamp);
    let message_disp = document.createElement('div');
    if (username == data.username) {
        message_disp.classList.add('d-flex','justify-content-end','mb-4')
        message_disp.innerHTML = `
            <div class="d-flex flex-column" style="max-width:90%;">
                <div class="text-muted mr-4 mb-1 small text-right">
                    ${username}
                </div>
                <div class="msg_cotainer_send text-right pr-3">
                    ${message}
                </div>
                <span class="msg_time_send mr-3 mt-1 text-right">${getRelativeTime(timestamp)}</span>
            </div>
            <div class="img_cont_msg">
                <img src="../images/programmer.png" class="rounded-circle user_img_msg">
            </div>
        `
    }
    else {
        message_disp.classList.add('d-flex','justify-content-start','mb-4');
        message_disp.innerHTML = `
            <div class="img_cont_msg">
                <img src="../images/user-default-img.jpg" class="rounded-circle user_img_msg">
            </div>
            <div class="d-flex flex-column" style="max-width:90%;">
                <div class="text-muted ml-4 mb-1 small">
                    ${username}
                </div>
                <div class="msg_cotainer pl-3">
                    ${message}
                </div>
                <span class="msg_time ml-3 mt-1">${getRelativeTime(timestamp)}</span>
            </div>
        `;
    };
    message_log.appendChild(message_disp);
    message_log.scrollTop = message_log.lastElementChild.offsetTop
};

submit_btn.onclick = (event) => {
    event.preventDefault();
    send_data({
        username: data.username,
        room_name: data.room_name,
        message: message_input.value,
        timestamp: moment().format()
    });
    message_input.value = '';
};

message_input.onkeyup = (event) => {
    if (event.keyCode == 13)
        submit_btn.click();
};

home_btn.onclick = () => {
    window.location.href = "/";
};

// fetch data for specific (user,room) (data: pre-defined in chat.html)
const chat_log = []
function contains(chat_log, message) {
    for (i in chat_log) {
        if (JSON.stringify(chat_log[i]) === JSON.stringify(message))
            return true
    }
    return false
}
setInterval(
    () => {
        get_data(data)
            .then(response => {
                message_count_disp.innerText = response['messages'].length.toString() + ' Messages';
                for (i in response['messages']){
                    let message = response['messages'][i]
                    if (!contains(chat_log, message)){
                        createMessage(message)
                        chat_log.push(message)
                    }
                }
            })
    }, 
    1000
)