from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import LineBotApiError
from flask import Flask, request, abort

app = Flask(__name__)

line_bot_api = LineBotApi('你的Line Bot Access Token')
handler = WebhookHandler('你的Line Bot Secret Key')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("LineBotApiError:", e)
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def reply_message(event):
    user_message = event.message.text
    reply = "我聽不懂你說什麼"
    if "你好" in user_message:
        reply = "你好，有什麼需要我幫忙的嗎？"
    elif "再見" in user_message:
        reply = "掰掰，下次見！"
    elif "你是誰" in user_message:
        reply = "我是一個簡單的Line Bot回話機器人"
    message = TextSendMessage(text=reply)
    line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
    app.run()
