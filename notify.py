import requests

def LineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
    }

    body = {
        'message': msg
    }

    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=body)
    return r.status_code

if __name__ == "__main__":
    token = "hiAoFxB0BUrSq1ltBmF0cxKkqWLuweqdg1329BzMq4V"
    message = '通知'
    status = LineNotifyMessage(token, message)
    print("Status: ", status)