from flask import Flask, request, abort
# import waitress
from gevent.pywsgi import WSGIServer

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, FollowEvent, JoinEvent, MemberJoinedEvent, TextMessage, ImageMessage, TextSendMessage,
    ImageSendMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn, MessageTemplateAction, URITemplateAction
)

from odoo_xmlrpc import *
from datetime import datetime as dt, timedelta as td
import time
import configparser

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'), timeout=(10.0, 10.0))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

# xmlrpc建立連線
models = endpoint_object()
uid = conflictRetry(get_uid())
uidGetTime = dt.now()


@app.route("/callback", methods=['POST'])
def callback():
    # print("[INFO] Get request:")
    # print(request.__dict__)
    global uidGetTime
    checkTime = dt.now()
    if (checkTime - uidGetTime) > td(minutes=10):
        models = endpoint_object()
        uid = conflictRetry(get_uid())
        uidGetTime = dt.now()
        print("Connect & UID updated!!")

    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # app.logger.info("Request body: " + body)

    print("====================================================\n[Request Body]\n" + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
        print('===================================================')
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    m_user_id = event.source.user_id
    # print(m_user_id)
    m_content = event.message.text.upper().strip()
    try:
        m_user_profile = line_bot_api.get_profile(m_user_id)

    except LineBotApiError:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="嗨嗨！這位朋友\n我還不認識你，可以把我加入好友嗎OwO/")
        )
        return 0

    m_user_name = m_user_profile.display_name
    m_chatroom_name = "自己的聊天室"
    reply_content = ""

    # # 測試警告訊息
    # if m_content.find("成功") >= 0 :
    #     reply_content = 'Hi, ' + m_user_name + ':\n'
    #     reply_content += "目前程式尚在測試\n所有訂單都有被記錄\n小幫手未回應也不用重新下單喔!"
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=reply_content)
    #     )

    if m_content.find("私訊") >= 0 and not m_content.find("請私訊") >= 0:
        reply_content = 'Hi, ' + m_user_name + ':\n'
        reply_content += "請勿私訊管理員!\n請點選下方連結前往好好吃真人客服尋求更多幫助喔!\nhttps://reurl.cc/oe6m4v\n24小時內未回覆請再次傳訊息!\n謝謝您的合作!"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_content)
        )

    if m_content.find("註冊用戶") >= 0:
        reply_content = 'Hi, ' + m_user_name + ':\n'
        # reply_content += "註冊教學還在努力生產中@@"
        with open('Enroll.txt', encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            reply_content += line
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_content)
        )

    auth_group = [
        "Cfd5357a0e2d0534fb99174d9466b181c",  # 好好吃群組1
        "Ccc167a6bd56749b0d064cd55e182b92d",  # 好好吃群組2
        "Cafce7ed68864ec16abc0434c8324d528",  # 好好吃群組3
        "C4a7fa9c0a648b720263b72bd5acb5794",  # 不好吃
        "C3605481f86711e09c248668159c8db0b",  # 好吃小天地
    ]

    # 在群組時做的事
    if event.source.type == 'group' and event.source.group_id in auth_group:
        m_chatroom_name = line_bot_api.get_group_summary(event.source.group_id).group_name
        # print(line_bot_api.get_group_summary(event.source.group_id))
        content_split = m_content.split('\n')

        if content_split[0] == "/小幫手" and event.source.group_id in auth_group[-2:]:
            reply_content = 'Hi, ' + m_user_name + ':\n'
            reply_content += '👇以下為機器人指令👇\n'
            reply_content += '\n'
            reply_content += '[貨品更新]\n'
            reply_content += '取貨更新\n關鍵字:{}\n新取貨日:YYYY-MM-DD\n價格:{}\n'
            reply_content += '\n'
            reply_content += '[貨品刪除]\n'
            reply_content += '貨品刪除\n關鍵字:{}'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_content)
            )

        # 「可訂商品」關鍵字適用於群組及個人
        if m_content == '可訂商品':
            valid_products = getValidProducts(models, uid)
            reply_content = 'Hi, ' + m_user_name + ':\n'
            # reply_content = ''
            reply_content += "以下為目前可訂購商品列表:\n"
            for item in valid_products:
                reply_content += "\n喊單關鍵字：" + item['product_keywords']
            reply_content += "\n請喊關鍵字+數量喔"
            reply_content += "\n\n範例:\n下單(換行)\n草莓+1(換行)\n蘋果+1"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_content)
            )

        if content_split[0].strip() == '下單' and len(content_split) > 1:
            reply_content = 'Hi, ' + m_user_name + ':\n'

            sign_rules = {
                'plus sign': '+',
                '加': '+',
                '＋': '+',
                '十': '+',
                '十': '+',
                '(': '',
                ')': '',
                '囗': '口',
                '*': '+',
            }
            number_rules = {
                'one': '1',
                'two': '2',
                'three': '3',
                'four': '4',
                'five': '5',
                'six': '6',
                'seven': '7',
                'eight': '8',
                'night': '9',
                'zero': '0',
                '一': '1',
                '二': '2',
                '三': '3',
                '四': '4',
                '五': '5',
                '六': '6',
                '七': '7',
                '八': '8',
                '九': '9',
                '零': '0',
                '１': '1',
                '２': '2',
                '３': '3',
                '４': '4',
                '５': '5',
                '６': '6',
                '７': '7',
                '８': '8',
                '９': '9',
                '０': '0'
            }
            flag = 0  # 判斷格式正確

            # 判斷是否有取貨地點start
            endRow = len(content_split)
            customPUAreaFK = 0

            if content_split[len(content_split) - 1].find("取") > 0:
                flag = 6
                adata = getPickupAreas(models, uid,
                                       #    content_split[len(content_split) - 1][:content_split[len(content_split) - 1].find("取")]
                                       content_split[-1].split('取')[0].replace('囗', '口').replace('*', '+').strip()
                                       )
                if len(adata) != 0:
                    customPUAreaFK = adata[0]['id']
                    flag = 0

                endRow = endRow - 1
            # 判斷是否有自己加取貨地點結束
            # print(endRow)
            problem = []
            pickup_dates = {}  # 0504
            for i in range(1, endRow):
                for rep, val in sign_rules.items():
                    content_split[i] = content_split[i].replace(rep, val)
                content = content_split[i].strip().split('+')
                # 如果下單項目被+號切割後數量不等於2或數量不等於整數
                if len(content) != 2:
                    flag = 1
                    break
                for rep, val in number_rules.items():
                    content[1] = content[1].replace(rep, val)
                try:
                    content[1] = int(content[1].strip())
                except ValueError:
                    flag = 1
                    break
                if content[1] == 0:
                    flag = 1
                    break

                # 用關鍵字搜尋商品
                check = getProductDataWithKeyword(models, uid, content[0].strip())
                # except TypeError:
                if len(check) == 0 or check['sale_ok'] == False:
                    if len(check) == 0:
                        # searchProbProduct(models, uid, content[0].strip())
                        problem.append(content[0].strip())
                    flag = 2
                    break
                else:
                    if check['pickup_date'] in pickup_dates.keys():
                        pickup_dates[check['pickup_date']].append((check['id'], content[1]))
                    else:
                        pickup_dates[check['pickup_date']] = [(check['id'], content[1])]

                # 檢查商品庫存
                s_status, s_inStock = checkInStock(models, uid, check['id'], int(content[1]))
                if not s_status:
                    if s_inStock > 0:
                        reply_content += check['name'] + '數量不足了\n'
                        flag = 5
                    else:
                        reply_content += '{} 已經賣完了🥲\n'.format(check['name'])
                        flag = 7
                    break

            # 取得odoo UserID(partner_id)
            # 取得User取貨地點FK
            odoo_user, odoo_partner = getUserDataByLine(models, uid, m_user_id)
            # print(odoo_partner, '\n-----------------------------------------')
            if odoo_user == [] or odoo_partner == []:
                flag = 3
            else:
                if not odoo_partner['pickup_area'] and customPUAreaFK == 0:
                    flag = 4

            if flag == 0:
                # 新增訂單
                #   - 填入odoo UserID
                #   - 填入取貨地點FK
                # 取得訂單ID
                for day in pickup_dates.keys():
                    if customPUAreaFK == 0:
                        orderId = newOrder(models, uid, odoo_user['partner_id'], day,
                                           odoo_partner['pickup_area'][0])
                    else:
                        orderId = newOrder(models, uid, odoo_user['partner_id'], day, customPUAreaFK)
                    print('----------------------------------------')
                    print('[商品資料]')
                    try:
                        seq = getOrderLineSequence(models, uid, orderId['id'])  # 如果是已經存在的訂單
                        orderId = orderId['id']
                        print("沿用舊訂單:", orderId)
                    except:
                        seq = 8  # 新的訂單
                        print("添加新訂單", orderId)
                    for i, item in enumerate(pickup_dates[day]):  # 0504
                        print(item)  # 0504
                        newOrderLine(models, uid, orderId, seq + 1 + i, item[0], item[1])  # 0504

                        # 新增一筆訂單記錄
                        #   - 填入訂單FK
                        #   - 填入序號
                        #   - 填入商品FK
                        #   - 填入數量
                    # order_result = getOrderData(models, uid, orderId)
                    # final_total = order_result['amount_total']
                # reply_content += '訂單新增成功囉！\n這次訂單的總金額是：$' + str(final_total) + '\n請在 '+ order_result['pickup_date'] + '\n到 ' + order_result['pickup_area'][1] + ' 取貨。'

                reply_content += '下單成功🤩'
            elif flag == 1:
                reply_content += '糟糕😰格式好像哪裡出錯了\n請確認之後再試一遍🥺'
            elif flag == 2:
                reply_content += '我找不到這樣商品耶...😅\n請確認關鍵字正確之後再試一遍😘'
            elif flag == 3:
                reply_content += '您好像還沒綁定帳號喔🧐\n請前往下方網址以Line註冊登入並且填寫相關資料\nhttps://reurl.cc/an9xXX'
            elif flag == 4:
                reply_content += '您尚未設定有效的取貨地點哦😮\n請前往下方網址設定!\nhttps://reurl.cc/an9xXX'
            elif flag == 5:
                reply_content += '請您調整數量後再嘗試🥲'
            elif flag == 6:
                reply_content += '糟糕😰取貨地點好像打錯了\n請確認之後再試一遍🥲'
            elif flag == 7:
                reply_content += '請您調整下單內容後再試一次😣'

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_content)
            )

        if content_split[0] == "取貨更新" and len(content_split) >= 2 and event.source.group_id in auth_group[-2:]:
            reply_content = 'Hi, 管理員:'

            print(content_split)
            keywords = content_split[1][4:]  # 關鍵字:
            newPickupDate = content_split[2][5:]  # 新取貨日:
            price = content_split[3][3:]  # 價格:
            print("關鍵字:{}".format(keywords))
            print("新取貨日:{}".format(newPickupDate))
            print("價格:{}".format(price))

            # 取得商品資訊
            item = getProductDataWithKeyword(models, uid, keywords)
            # 更新取貨日
            print("商品ID:{}".format(item['id']))
            print("商品價格OLD:{}".format(item['list_price']))
            result = updateProductPickupDate(models, uid, item['id'], newPickupDate, price)
            if result:
                print("成功更新商品資訊")
            # 取得order line紀錄
            # print(item['name'])
            # print(item['list_price'])
            # print(item['sale_start_date'])

            if item['pickup_date'] != newPickupDate:  # 如果日期需要更新
                records = getOrderLineRecord(models, uid, item['name'], price, item['sale_start_date'],
                                             item['sale_end_date'], newPickupDate)
            else:
                records = getOrderLineRecord(models, uid, item['name'], price, item['sale_start_date'],
                                             item['sale_end_date'])
            print(records)
            print("===============開始更新==================")
            success = 0
            error = 0
            for rec in records:
                print("訂單ID:{}-產品ID:{}-數量:{} 更新成功".format(rec['order_id'], rec['product_id'],
                                                                    rec['product_uom_qty']))
                # 取得舊訂單資料
                order = getOrderData(models, uid, rec['order_id'][0])
                # 取得新訂單ID
                orderId = newOrder(models, uid, order['partner_id'][0], newPickupDate,
                                   order['pickup_area'][0])
                # 寫入order line
                try:
                    seq = getOrderLineSequence(models, uid, orderId['id'])  # 如果是已經存在的訂單
                    orderId = orderId['id']
                    print("沿用舊訂單")
                except:
                    seq = 8  # 新的訂單
                    print("添加新訂單")
                newOrderLine(models, uid, orderId, seq + 1, rec['product_id'][0], rec['product_uom_qty'])
                # 更新舊的order line amount
                result = updateOrderLineAmount(models, uid, rec['id'], 0)
                if result:
                    success += 1
                    print("更新成功")
                error = len(records) - success
            reply_content += "更新成功!\n"
            reply_content += "===============\n"
            reply_content += "[成功更新筆數]:" + str(success) + '\n'
            reply_content += "[失敗更新筆數]:" + str(error) + '\n'
            reply_content += "===============\n"
            reply_content += "[總共更新筆數]:" + str(len(records))

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_content)
            )

        if content_split[0] == "貨品刪除" and len(content_split) >= 2 and event.source.group_id in auth_group[-2:]:
            reply_content = 'Hi, 管理員:'
            keywords = content_split[1][4:]  # 關鍵字:
            item = getProductDataWithKeyword(models, uid, keywords)
            print(item['name'])
            print(item['list_price'])
            print(item['sale_start_date'])
            print(item['sale_end_date'])
            records = getOrderLineRecord(models, uid, item['name'], int(item['list_price']), item['sale_start_date'],
                                         item['sale_end_date'], '1971-01-01')  # 最後面添加一個日期方便取得所有紀錄(無意義)
            print("待處理紀錄:{}筆".format(len(records)))
            print("===============開始更新==================")
            success = 0
            error = 0
            for rec in records:
                try:
                    # 更新舊的order line amount
                    result = updateOrderLineAmount(models, uid, rec['id'], 0)
                    print("訂單ID:{}-產品ID:{}-數量:{}-刪除成功(數量更新為0)".format(rec['order_id'], rec['product_id'],
                                                                                     rec['product_uom_qty']))
                    if result:
                        print("更新完畢")
                        success += 1
                except:
                    error += 1

            reply_content += "刪除成功!\n"
            reply_content += "===============\n"
            reply_content += "[成功刪除筆數]:" + str(success) + '\n'
            reply_content += "[失敗刪除筆數]:" + str(error) + '\n'
            reply_content += "===============\n"
            reply_content += "[總共刪除筆數]:" + str(len(records))
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_content)
            )
    # 在個人聊天室時做的事
    elif event.source.type == 'user':
        if m_content.strip() == '個人訂單' or m_content.strip() == '取貨總額':
            reply_content = 'Hi, ' + m_user_name + ':\n'
            try:
                # 取得odoo UserID(partner_id)
                odoo_user, odoo_partner = getUserDataByLine(models, uid, m_user_id)

                odatas = getRecentOrders(models, uid, odoo_user['partner_id'])
                if len(odatas) == 0:
                    # reply_content += '找不到您將在 '+getRecentPickupDate(mode=1)+' 取貨的訂單耶...\n趕快去群組下單吧!'
                    reply_content += '找不到您的訂單耶...\n趕快去群組下單吧!'

                else:
                    dts = sorted(list(set([d['pickup_date'] for d in odatas])))
                    for dt in dts:

                        reply_content += '\n以下是您在 ' + dt + ' 要取貨的訂單：'

                        plas = list(set([d['pickup_area'][1] for d in odatas]))
                        for pla in plas:
                            reply_content += '\n====================\n在 ' + pla + ' 取貨：\n'
                            orders = [d['id'] for d in odatas if d['pickup_area'][1] == pla and d['pickup_date'] == dt]
                            details = getOrderDetail(models, uid, orders)
                            # prdts = list(set([ d['name'] for d in details ]))
                            prdts = [{'name': d['name'], 'price': d['price_unit']} for d in details]
                            prdts = [dict(t) for t in {tuple(d.items()) for d in prdts}]
                            for product in prdts:
                                total = int(
                                    sum([d['product_uom_qty'] for d in details if d['name'] == product['name']]))
                                if total > 0:
                                    reply_content += '\n' + product['name'] + '(單價 ' + str(
                                        int(product['price'])) + ')：' + str(total)
                            reply_content += '\n\n總計是 ' + str(int(sum([d['amount_total'] for d in odatas if
                                                                          d['pickup_area'][1] == pla and d[
                                                                              'pickup_date'] == dt]))) + ' 元整'
                        if dt != dts[-1]:
                            reply_content += '\n'

                    # textMessage = TextSendMessage(text=reply_content)

                    # ==================0422棄用======================
                    # clns = []

                    # # LINE限制最多10筆
                    # if len(odatas)>10:
                    #      odatas = odatas[:10]

                    # for data in odatas:
                    #     if data['access_token']:
                    #         uri_link='https://haohaochi.subuy.net/my/orders/'+str(data['id'])+'?access_token='+data['access_token']
                    #     else:
                    #         uri_link='https://haohaochi.subuy.net/my/orders/'

                    #     msg = '取貨地點：'+data['pickup_area'][1]+'\n合計金額：$'+str(int(data['amount_total']))
                    #     clns.append(CarouselColumn(
                    #         thumbnail_image_url='https://haohaochi.subuy.net/web/image/3026/S__119816203_0.jpg',
                    #         title=data['name'],
                    #         text=msg,
                    #         actions=[
                    #             URITemplateAction(
                    #                 label='訂單細節',
                    #                 uri=uri_link
                    #             )
                    #         ]
                    #     ))
                    # carouselTemplate = TemplateSendMessage(
                    #     alt_text='訂單資訊',
                    #     template=CarouselTemplate(columns=clns)
                    # )
                    # line_bot_api.reply_message(
                    #     event.reply_token,
                    #     [textMessage, carouselTemplate])
                    # ======================================================================

            except TypeError:
                reply_content += '您好像還沒綁定帳號喔！\n請前往下方網址以Line註冊登入並且填寫相關資料\nhttps://reurl.cc/an9xXX'

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_content)
            )

        elif m_content == '取貨資訊':
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url='https://haohaochi.subuy.net/web/image/3026/S__119816203_0.jpg',
                    preview_image_url='https://haohaochi.subuy.net/web/image/3026/S__119816203_0.jpg'
                )
            )

        elif m_content == '客服聯繫':
            reply_content = 'Hi, ' + m_user_name + ':\n'
            reply_content += '小幫手不能幫你回答問題QQ\n請點選下方連結前往好好吃真人客服尋求更多幫助喔!\nhttps://reurl.cc/oe6m4v'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_content))


        elif m_content == '可訂商品':
            valid_products = getValidProducts(models, uid)
            reply_content = 'Hi, ' + m_user_name + ':\n'
            reply_content += "以下為目前可訂購商品列表:\n"
            for item in valid_products:
                reply_content += "\n喊單關鍵字：" + item['product_keywords']
            reply_content += "\n請到群組喊關鍵字+數量喔！"
            reply_content += "\n\n範例:\n下單(換行)\n草莓+1(換行)\n蘋果+1"

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_content)
            )

        elif m_content == '個人編號':
            reply_content = 'Hi, ' + m_user_name + ':\n'
            try:
                odoo_user, odoo_partner = getUserDataByLine(models, uid, m_user_id)
                reply_content += '您的會員編號是： C' + str(odoo_partner['id']).zfill(6)
            except TypeError:
                reply_content += '您好像還沒綁定帳號喔！\n請前往下方網址以Line註冊登入並且填寫相關資料\nhttps://reurl.cc/an9xXX'

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_content))

        elif m_content == '購物金':
            reply_content = 'Hi, ' + m_user_name + ':\n'
            try:
                # 取得odoo UserID(partner_id)
                odoo_user, odoo_partner = getUserDataByLine(models, uid, m_user_id)
                reply_content += '您現在有 ' + str(odoo_partner['user_discount']) + ' 元的購物金！'
            except TypeError:
                reply_content += '您好像還沒綁定帳號喔！\n請前往下方網址以Line註冊登入並且填寫相關資料\nhttps://reurl.cc/an9xXX'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_content))
        elif m_content == '個人資訊':
            reply_content = 'Hi, ' + m_user_name + ':\n'
            try:
                # 取得odoo UserID(partner_id) ['id', 'email', 'phone', 'pickup_area','user_discount', 'is_enroll']
                odoo_user, odoo_partner = getUserDataByLine(models, uid, m_user_id)

                id = "C" + str(odoo_partner['id']).zfill(6)
                enroll = "成功" if odoo_partner['is_enroll'] == True else "失敗"
                reply_content += '[個人編號]:' + str(id) + '\n'
                reply_content += '[Email]:' + str(odoo_partner['email']) + '\n'
                reply_content += '[取貨區域]:' + str(odoo_partner['pickup_area'][1]) + '\n'
                reply_content += '[購物金]:$' + str(odoo_partner['user_discount']) + '\n'
                reply_content += '[註冊狀態]:' + str(enroll) + '\n'
                reply_content += '[備註]:\n非臉書用戶註冊狀態失敗請忽略'

            except TypeError:
                reply_content += '您好像還沒綁定帳號喔！\n請前往下方網址以Line註冊登入並且填寫相關資料\nhttps://reurl.cc/an9xXX'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_content))
    print('-----------------------------------------')
    print('[訊息內容]')
    print(m_user_name + " 在 ", m_chatroom_name + " 說：\n" + m_content)
    if reply_content != "":
        print('-----------------------------------------')
        print('[已回覆的內容]\n')
        print(reply_content)


@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    print('-----------------------------------------')
    print('這是一張圖片')


if __name__ == "__main__":
    # app.run()
    # waitress.serve(app, host='0.0.0.0', port='5000')
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
