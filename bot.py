from datetime import datetime


def greeting(username, room_name):
    utc_dt = datetime.now().astimezone()
    timestamp = utc_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
    timestamp = timestamp[:-2] + ':' + timestamp[-2:]

    return {
        'username': 'bot',
        'message': f'Chào mừng {username} đến với phòng {room_name} <3',
        'timestamp': timestamp,
    }

def good_bye(username, room_name):
    utc_dt = datetime.now().astimezone()
    timestamp = utc_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
    timestamp = timestamp[:-2] + ':' + timestamp[-2:]

    return {
        'username': 'bot',
        'message': f'{username} đã rời khỏi phòng {room_name} :\'(',
        'timestamp': timestamp,
    }

def answer(username, room_name, msg: str):
    utc_dt = datetime.now().astimezone()
    timestamp = utc_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
    timestamp = timestamp[:-2] + ':' + timestamp[-2:]

    bot_msg = ''
    if msg.lower().find('hello') != -1:
        bot_msg = f'Holle {username} :)'
    elif msg.lower().find('xin chào') != -1:
        bot_msg = f'Chào {username}'

    return {
        'username': 'bot',
        'message': bot_msg,
        'timestamp': timestamp,
    }