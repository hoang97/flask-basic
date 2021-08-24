const action_menu_btn = document.getElementById('action_menu_btn');
const room_name_disp = document.getElementById('room_name');
const message_count_disp = document.getElementById('message_count');
const submit_btn = document.getElementById('send_btn');
const message_input = document.getElementById('message_input');
const message_log = document.getElementById('message_log');
const home_btn = document.getElementById('home_btn');

const ws = io(ws_url,{
    query: data
});
const getRelativeTime = (timestamp) => {
    if (timestamp.isBefore(moment().subtract(1, 'w'))){
        return timestamp.format('LT, L')
    }
    else {
        return timestamp.fromNow()
    }
};
let message_count = 0
action_menu_btn.onclick = () => {
    let action_menu = document.querySelector('.action_menu')
    action_menu.classList.toggle('show')
};

room_name_disp.innerText = data.room_name;

ws.on('connect', () => {
    console.log('Connected to websocket');
});

ws.on('disconnect', () => {
    console.log('Disconnected from websocket');
});

ws.on('server_message', (response) => {
    message_count += 1;
    message_count_disp.innerText = message_count.toString() + ' Messages';
    let username = response.username;
    let message = response.message;
    let timestamp = moment(response.timestamp);
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
        message_disp.classList.add('d-flex','justify-content-start','mb-4')
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
        `
    }
    message_log.appendChild(message_disp);
    message_log.scrollTop = message_log.lastElementChild.offsetTop
});

submit_btn.onclick = (event) => {
    event.preventDefault();
    ws.emit('client_message', {
        message: message_input.value,
        timestamp: moment().format()
    });
    message_input.value = ''
}
message_input.onkeyup = (event) => {
    if (event.keyCode == 13)
        submit_btn.click()
};
home_btn.onclick = () => {
    window.location.href = "/";
}