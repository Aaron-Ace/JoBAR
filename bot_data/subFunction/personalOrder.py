from .odoo_xmlrpc import *
from linebot.models import FlexSendMessage, TextSendMessage

def buildSeperateJson():
    return {"type": "separator","margin": "xxl"}

def buildTotalJson(amount_total):
    return {"type": "box","layout": "horizontal","contents": [
        {"type": "text","text": "總共金額","size": "sm","color": "#555555"},
        {"type": "text","text": str(amount_total),"size": "sm","color": "#111111","align": "end"}]}

def buildItemsCountJson(count):
    return {"type": "box","layout": "horizontal","margin": "xxl","contents": [
        {"type": "text","text": "商品數量","size": "sm","color": "#555555"},
        {"type": "text","text": str(count),"size": "sm","color": "#111111","align": "end"}]}

def buildJson(name, price, amount):
    return {
        "type": "box",
        "layout": "horizontal",
        "contents": [
            {
                "type": "text",
                "text": name,
                "size": "sm",
                "color": "#555555",
                "flex": 0
            },
            {
                "type": "text",
                "text": price,
                "size": "sm",
                "color": "#111111",
                "align": "center"
            },
            {
                "type": "text",
                "text": amount,
                "size": "sm",
                "color": "#111111",
                "align": "end"
            }
        ]
    }


def buildPersonalOrderFlexMsg(pickup_date, pickup_area, product_list_json, sale_order_id):
    personalOrderFlexMsg = {
        "type": "bubble",
        "size": "giga",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "個人訂單",
                    "weight": "bold",
                    "color": "#1DB446",
                    "size": "sm"
                },
                {
                    "type": "text",
                    "text": "訂單明細",
                    "weight": "bold",
                    "size": "xxl",
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {
                            "type": "text",
                            "text": "取貨日期"
                        },
                        {
                            "type": "text",
                            "text": str(pickup_date),
                            "align": "end"
                        }
                    ],
                    "margin": "lg"
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {
                            "type": "text",
                            "text": "取貨地點"
                        },
                        {
                            "type": "text",
                            "text": str(pickup_area),
                            "align": "end",
                            "flex": 2
                        }
                    ]
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
                    "contents": product_list_json
                },
                {
                    "type": "separator",
                    "margin": "xxl"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "訂單編號",
                            "size": "xs",
                            "color": "#aaaaaa",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": sale_order_id,
                            "color": "#aaaaaa",
                            "size": "xs",
                            "align": "end"
                        }
                    ]
                }
            ]
        },
        "styles": {
            "footer": {
                "separator": True
            }
        }
    }
    return personalOrderFlexMsg

def personalOrderFlexMsgSend(MsgList):
    personalOrderFlexMsgCarousel = {"type": "carousel", "contents":MsgList}
    return FlexSendMessage(alt_text="個人訂單", contents=personalOrderFlexMsgCarousel)


def personalOrderFunc(line_bot_api, event, models, uid, m_user_name, m_user_id):
    reply_content = 'Hi, ' + m_user_name + ':\n'
    try:
        # 取得odoo UserID(partner_id)
        odoo_user, odoo_partner = getUserDataByLine(models, uid, m_user_id)

        odatas = getRecentOrders(models, uid, odoo_user['partner_id'])
        if len(odatas) == 0:
            reply_content += '找不到您的訂單耶...\n趕快去群組下單吧!'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_content))
        else:
            dts = sorted(list(set([d['pickup_date'] for d in odatas])))
            MsgList = []
            for dt in dts:
                plas = list(set([d['pickup_area'][1] for d in odatas]))
                for pla in plas:
                    orders = [d['id'] for d in odatas if d['pickup_area'][1] == pla and d['pickup_date'] == dt]
                    try:
                        orders_name = [d['name'] for d in odatas if d['pickup_area'][1] == pla and d['pickup_date'] == dt][0]
                    except:
                        continue
                    details = getOrderDetail(models, uid, orders)
                    prdts = [{'name': d['name'], 'price': d['price_unit']} for d in details]
                    prdts = [dict(t) for t in {tuple(d.items()) for d in prdts}]
                    count = 0
                    json_list = []
                    for product in prdts:
                        count += 1
                        total = int(sum([d['product_uom_qty'] for d in details if d['name'] == product['name']]))

                        if total > 0:
                            json_list.append(buildJson(product['name'],  str(product['price']), str(total)))
                    amount_total = sum([d['amount_total'] for d in odatas if d['pickup_area'][1] == pla and d['pickup_date'] == dt])
                    json_list.append(buildSeperateJson())
                    json_list.append(buildItemsCountJson(count))
                    json_list.append(buildTotalJson(amount_total))
                    temp = buildPersonalOrderFlexMsg(dt, pla, json_list, orders_name)
                    MsgList.append(temp)
            print("回覆Flex Message")
            line_bot_api.push_message(m_user_id, personalOrderFlexMsgSend(MsgList))

    except TypeError:
        reply_content += '您好像還沒綁定帳號喔！\n請前往下方網址以Line註冊登入並且填寫相關資料\nhttps://reurl.cc/RzdgvD'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_content))
