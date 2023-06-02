from .odoo_xmlrpc import *
from linebot.models import FlexSendMessage, TextSendMessage

def buildFlexMsgJson(customer_id, email, area, money):
    jsonMsg = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "個人資訊",
                    "weight": "bold",
                    "color": "#1DB446",
                    "size": "sm"
                },
                {
                    "type": "text",
                    "text": "資料詳情",
                    "weight": "bold",
                    "size": "xxl",
                    "margin": "md"
                },
                {
                    "type": "separator",
                    "margin": "xxl"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "xxl",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "個人編號",
                                    "size": "sm",
                                    "color": "#555555",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": str(customer_id),
                                    "size": "sm",
                                    "color": "#111111",
                                    "align": "end"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "電子郵件",
                                    "size": "sm",
                                    "color": "#555555",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": str(email),
                                    "size": "sm",
                                    "color": "#111111",
                                    "align": "end"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "取貨區域",
                                    "size": "sm",
                                    "color": "#555555",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": str(area),
                                    "size": "sm",
                                    "color": "#111111",
                                    "align": "end"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "margin": "none",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "購物金",
                                    "size": "sm",
                                    "color": "#555555"
                                },
                                {
                                    "type": "text",
                                    "text": str(money),
                                    "size": "sm",
                                    "color": "#111111",
                                    "align": "end"
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "separator",
                    "margin": "xxl"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "md",
                    "contents": []
                }
            ]
        },
        "styles": {
            "footer": {
                "separator": True
            }
        }
    }
    return FlexSendMessage(alt_text="FeasibleProduct", contents=jsonMsg)


def personalDataFunc(line_bot_api, event,  models, uid, m_user_id, m_user_name):
    reply_content = 'Hi, ' + m_user_name + ':\n'
    try:
        # 取得odoo UserID(partner_id) ['id', 'email', 'phone', 'pickup_area','user_discount', 'is_enroll']
        odoo_user, odoo_partner = getUserDataByLine(models, uid, m_user_id)
        print(odoo_user)
        print(odoo_partner)

        id = "C" + str(odoo_partner['id']).zfill(6)
        enroll = "成功" if odoo_partner['is_enroll'] == True else "失敗"
        try:
            area = odoo_partner['pickup_area'][1]
        except:
            area = "尚未填寫"
        print("回覆Flex Message")
        line_bot_api.push_message(m_user_id, buildFlexMsgJson(id, odoo_partner['email'], area, odoo_partner['user_discount']))
    except TypeError:
        reply_content += '您好像還沒綁定帳號喔！\n請前往下方網址以Line註冊登入並且填寫相關資料\nhttps://reurl.cc/RzdgvD'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_content))