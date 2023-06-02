from .odoo_xmlrpc import *
from linebot.models import FlexSendMessage, TextSendMessage

def buildSeperateJson():
    return {"type": "separator","margin": "xxl"}

def buildCommentJson():
    return {
        "type": "box",
        "layout": "horizontal",
        "margin": "xxl",
        "contents": [
            {
                "type": "text",
                "size": "sm",
                "color": "#555555",
                "text": "[範例]\n下單\n蘋果+1(換行)\n橘子+3",
                "wrap": True
            },
            {
                "type": "text",
                "size": "sm",
                "color": "#555555",
                "text": "※請前往群組下單",
                "wrap": True
            }
        ]
    }

def buildProductJson(keyworkds, price):
    return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "關鍵字"
                },
                {
                    "type": "text",
                    "text": str(keyworkds),
                    "size": "sm",
                    "color": "#555555",
                    "flex": 0
                },
                {
                    "type": "text",
                    "text": str(price),
                    "size": "sm",
                    "color": "#111111",
                    "align": "end"
                }
            ]
        }

def buildFlexMsg(keyLine):
    msgJson =  {
        "type": "bubble",
        "size": "kilo",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "可訂商品",
                    "weight": "bold",
                    "color": "#1DB446",
                    "size": "sm"
                },
                {
                    "type": "text",
                    "text": "商品明細",
                    "weight": "bold",
                    "size": "xxl",
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "xxl",
                    "spacing": "sm",
                    "contents": keyLine
                }
            ]
        },
        "styles": {
            "footer": {
                "separator": True
            }
        }
    }
    return msgJson

def feasibleOrderProductFunc(line_bot_api, models, uid, m_user_id):
    valid_products = getValidProducts(models, uid)
    MsgList = []
    for item in valid_products:
        MsgList.append(buildProductJson(item['product_keywords'], item['list_price']))
    MsgList.append(buildSeperateJson())
    MsgList.append(buildCommentJson())
    MsgSend = FlexSendMessage(alt_text="FeasibleProduct", contents=buildFlexMsg(MsgList))
    print("回覆Flex Message")
    line_bot_api.push_message(m_user_id, MsgSend)
