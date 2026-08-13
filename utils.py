import requests
import socket
import time
from config import API_URL

def check_internet():
    """Check if internet is available"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def wait_for_internet():
    """Wait until internet is available"""
    count = 0
    while not check_internet():
        count += 1
        if count % 10 == 0:
            print("Still waiting for internet connection...")
        time.sleep(3)
    print("Internet connection restored.")
    return True

def send_message(chat_id, text):
    if not check_internet():
        return {'ok': False, 'error': 'No internet'}
    
    try:
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        resp = requests.post(f"{API_URL}/sendMessage", json=payload, timeout=10)
        return resp.json().get('result', {})
    except Exception as e:
        print(f"Send error: {e}")
        return {}

def send_message_with_keyboard(chat_id, text, reply_markup):
    if not check_internet():
        return {'ok': False, 'error': 'No internet'}
    
    try:
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown',
            'reply_markup': reply_markup
        }
        resp = requests.post(f"{API_URL}/sendMessage", json=payload, timeout=10)
        return resp.json().get('result', {})
    except Exception as e:
        print(f"Send error: {e}")
        return {}

def delete_message(chat_id, message_id):
    if not check_internet():
        return
    
    try:
        requests.post(
            f"{API_URL}/deleteMessage",
            json={'chat_id': chat_id, 'message_id': message_id},
            timeout=10
        )
    except:
        pass

def get_updates(offset=None, timeout=30):
    """Get updates from Telegram with internet check"""
    # Check internet first
    if not check_internet():
        print("No internet. Waiting for connection...")
        wait_for_internet()
    
    params = {'timeout': timeout}
    if offset:
        params['offset'] = offset + 1
    else:
        params['offset'] = 0
    
    try:
        resp = requests.get(f"{API_URL}/getUpdates", params=params, timeout=timeout + 5)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"Telegram API error: {resp.status_code}")
            return {'ok': False, 'result': []}
    except requests.exceptions.ConnectionError:
        print("Connection error. Waiting for internet...")
        wait_for_internet()
        return {'ok': False, 'result': []}
    except requests.exceptions.Timeout:
        print("Request timeout. Retrying...")
        return {'ok': False, 'result': []}
    except Exception as e:
        print(f"Get updates error: {e}")
        return {'ok': False, 'result': []}