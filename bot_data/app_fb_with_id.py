# coding=utf-8

import re
import json
import time
import requests
import configparser
from operator import itemgetter
from datetime import datetime, timedelta

from odoo_xmlrpc import *


def find_chinese(file):
    pattern = re.compile(r'[^\u4e00-\u9fa5\w\n+＋]')
    chinese = re.sub(pattern, '', file)
    return chinese


def utcEight(strtime):
    dt = strtime.split('T')
    time = dt[1].split('+')
    return datetime.strptime(dt[0] + ' ' + time[0], '%Y-%m-%d %H:%M:%S')  # + timedelta(hours=8)


groupId = '777119749887059'  # 好好吃
# groupId = '1672105386472269'  # 不好吃
debug = 0
test = 0
manual = 0 

models = endpoint_object()
uid = conflictRetry(get_uid())
uidGetTime = dt.now()
configID, getPostFreq = returnGrabFreqAndRecoedID(models, uid)  # 抓文的頻率, sql fk
#print(getPostFreq, configID)
writeFacebookStatus(models, uid, int(configID), '程式執行中...（超過3分鐘為異常）')

print("判斷是否要擷取貼文(根據抓取頻率)......\n")
#print(dt.now().minute)
#print(getPostFreq)
#print(dt.now().minute%getPostFreq)

facebook_status = ""
if manual == 1 or dt.now().minute % getPostFreq <= 1:  # 如果 手動操作==1 or 分鐘％爬文頻率小於1分鐘則執行（crontab 5分鐘抓一次）
    if debug == 0:
        print('[程式開始執行]\n\n從Facebook取得社團貼文清單中......')
        post_result = getGroupPosts(groupId, getFacebookToken(models, uid))
        #print(post_result)
        try:
            post_result['data']
        except:
            facebook_status += "貼文抓取失敗\n"

        print('抓取完畢！\n\n更新貼文資訊......')
        newPostCount = 0
        for post in post_result['data']:
            # pprint(post)
            postId = post['id']
            # if postId == '777119749887059_1024865021779196':
            #     continue
            # print(postId)
            postUdTime = utcEight(post['updated_time'])
            postInfo = getFbPost(models, uid, postId)
            addr = postId.split('_')
            address = 'https://www.facebook.com/groups/' + addr[0] + '/posts/' + addr[1] + '/'
            try:
                msg = post['message']
            except:
                msg = ''
                post['message'] = ''
            postContent = find_chinese(msg)
            # print(postContent)
            postType = postContent.split('\n')[0][-3:]
            # print(postType)
            if len(postInfo) == 0:
                if postType == "到貨團":
                    pageId = addFbPost(models, uid, postId, str(postUdTime), find_chinese(post['message']), address,
                                       True)
                else:
                    pageId = addFbPost(models, uid, postId, str(postUdTime), find_chinese(post['message']), address,
                                       False)
                newPostCount += 1
            else:
                if postInfo['update_time'] != str(postUdTime):
                    updateFbPost(models, uid, postInfo['id'], str(postUdTime), find_chinese(post['message']))
        if newPostCount != 0:
            print("這次新增了{}篇貼文。".format(newPostCount))
        else:
            print("這次沒有新增貼文。")
        print('更新完成！\n\n抓取各則貼文留言中......')
        print('更新完成！\n\n抓取各則貼文留言中......')
        for postId in getValidPost(models, uid):
            if postId == '777119749887059_1101790657419965':
                continue
            checkTime = datetime.now()
            if (checkTime - uidGetTime) > timedelta(minutes=10):
                models = endpoint_object()
                uid = conflictRetry(get_uid())
                uidGetTime = datetime.now()
                print("Connect & UID updated!!")
            print('=======================================\n從Facebook取得貼文 {} 的留言中....'.format(postId))
            raw_result = getGroupCommentsForEachPost(getFacebookToken(models, uid), postId, "500")
            # print(raw_result)
            print('抓取完畢，開始更新貼文留言資訊......')
            succ = 0
            fail = 0
            addCount = 0
            postInfo = getFbPost(models, uid, postId)
            pageId = postInfo['id']
            print(pageId)
            try:
                postCanComment = raw_result['summary']['can_comment']
            except:
                postCanComment = False
            # postCanComment = True
            # print(postCanComment)
            # a=input('Hello')
            try:
                print('貼文有{}則留言'.format(len(raw_result['data'])))
                # pprint(raw_result['data'])
                # a = input('Press enter!')
                for comment in raw_result['data']:
                    addCount += 1
                    # print("Count:{}".format(addCount))
                    # print(comment)
                    try:
                        commentId = comment['id']
                        searchResult = searchFbComment(models, uid, commentId)

                        commentContent = find_chinese(str(comment['message'].replace('*', '+')))
                        rawCreatedTime = comment['created_time']
                        commentCreatedTime = utcEight(rawCreatedTime)

                        try:
                            user_id = ""
                            rawComment = comment['message'].replace("號", "").replace("：", ":").split("\n")
                            rawComment[0] = rawComment[0].strip().upper()
                            if rawComment[0].find('C') != -1:
                                user_id = int(rawComment[0][rawComment[0].find("C") + 1:])
                            elif rawComment[0].find('c') != -1:
                                user_id = int(rawComment[0][rawComment[0].find("c") + 1:])
                            elif rawComment[0].find(':') != -1:
                                user_id = int(rawComment[0][rawComment[0].find(":") + 1:])
                            else:
                                user_id = int(rawComment[0])

                            # print(user_id)

                            if len(searchUsersID(models, uid, user_id)) == 0:
                                user_id = 2
                        except:
                            user_id = 2

                        if len(searchResult) == 0:
                            if user_id != 2:
                                addComment(models, uid, user_id, pageId, commentId, commentContent, 'incomplete',
                                           str(commentCreatedTime))
                            else:
                                addComment(models, uid, user_id, pageId, commentId, commentContent, '未留言編號',
                                           str(commentCreatedTime))
                        else:
                            if searchResult['state'][:4].upper().strip() != 'DONE':
                                # print(searchResult['state'])
                                if user_id != 2 and int(
                                        searchResult['partner_id'][0]) == 2:  # 如果有找到新的ID替代原本的Odoobot
                                    updatePartnerID(models, uid, searchResult['id'], user_id)
                                    print("成功更新ID:{}_{}".format(user_id, comment['from']['name']))
                                    updateCommentState(models, uid, searchResult['id'], 'incomplete')  # 如果有更新ID要重新抓
                                if searchResult['comment_content'] != find_chinese(
                                        str(comment['message'].replace('*', '+'))) \
                                        and int(searchResult['partner_id'][0]) != 100:  # 也不等於業主的留言# 如果留言有更新就寫入
                                    print("Old:{}\n".format(searchResult['comment_content']))
                                    print("New:{}\n".format(str(comment['message'])))
                                    updatePartnerContent(models, uid, searchResult['id'],
                                                         find_chinese(str(comment['message'].replace('*', '+'))))
                                    print("成功更新留言:{}{}\n".format(searchResult['id'], str(comment['message'])))
                                    updateCommentState(models, uid, searchResult['id'], 'incomplete')  # 如果有更新留言要重新抓
                                if searchResult['state'][:7] == 'Error#3' or searchResult['state'][:4] == '沒有授權':
                                    updateCommentState(models, uid, searchResult['id'], 'incomplete')  # 如果庫存不足要重新抓
                        succ += 1
                    except KeyError:
                        commentId = comment['id']
                        searchResult = searchFbComment(models, uid, commentId)
                        if len(searchResult) == 0:
                            commentContent = str(comment['message'])
                            rawCreatedTime = comment['created_time']
                            commentCreatedTime = utcEight(rawCreatedTime)
                            addComment(models, uid, 2, pageId, commentId, commentContent, '未留言編號',
                                       str(commentCreatedTime))
                        fail += 1
                        continue
                if len(raw_result['data']) != 0:
                    print('共有{}則留言成功註冊並授權，{}則有誤。本次增加{}則留言...'.format(succ, fail, addCount))
                if postCanComment == False:
                    updatePostState(models, uid, postId, False)
            except KeyError:
                print('No comment!!')
                facebook_status += "留言抓取失敗\n"
                continue
            except Exception as e:
                print('Error:', comment, sep='\n')
                print(e)
                facebook_status += e + '\n'
                # a = input("Can I continue?")
                continue

            # a = input('Press Enter again.')
        print('=======================================\n留言新增/更新完畢......\n')
    if debug == 0:
        if test == 1:
            comments = [
                {
                    'id': 110022,
                    'partner_id': 81,
                    'create_time': '2022-03-18 06:55:07',
                    'comment_content': '下單\n香蒜小羅宋+1\n鹽水雞+1\n楊梅取'
                }
                # {
                #     'id': 13,
                #     # 'user_id': 80,
                #     'partner_id': 81,
                #     'create_time': '2022-03-18 06:55:07',
                #     'comment_content': '下單\n香蒜小羅宋+1\n鹽水雞+1\n楊梅取'
                # },
                # {
                #     'id': 14,
                #     # 'user_id': 81,
                #     'partner_id': 82,
                #     'create_time': '2022-03-20 21:52:06',
                #     'comment_content': '下單\n甘蔗雞+1\n柳丁原汁+1'
                # },
                # {
                #     'id': 15,
                #     # 'user_id': 29,
                #     'partner_id': 30,
                #     'create_time': '2022-03-17 12:35:26',
                #     'comment_content': '下單\n我來亂的啦'
                # },
                # {
                #     'id': 16,
                #     # 'user_id': 107,
                #     'partner_id': 108,
                #     'create_time': '2022-03-19 15:21:32',
                #     'comment_content': '下單'
                # },
                # {
                #     'id': 20,
                #     # 'user_id': 12,
                #     'partner_id': 13,
                #     'create_time': '2022-03-17 09:18:30',
                #     'comment_content': '下單\n鹽水雞+9999999999999'
                # }
            ]
        else:
            print('從資料庫取得未完成留言中......')
            if test == 0:
                comments = getUnprocessComments(models, uid)
            else:
                comments = getTestComments(models, uid)
            print('完成，共有{}則未處理留言。'.format(len(comments)))

        # 如果回傳長度不為0
        if len(comments) != 0:
            # 按留言時間進行排序
            comments = sorted(comments, key=itemgetter('create_time'))

            print('開始處理未完成留言......')
            for comment in comments:

                checkTime = datetime.now()
                if (checkTime - uidGetTime) > timedelta(minutes=10):
                    models = endpoint_object()
                    uid = conflictRetry(get_uid())
                    uidGetTime = datetime.now()
                    print("Connect & UID updated!!")
                print(comment)

                if len(comment['comment_content'].strip()) > 0:

                    m_content = comment['comment_content'].upper().strip()
                    content_split = m_content.split('\n')

                    # if content_split[-1].find("取") == -1:
                    #     content_split = content_split[:-1]

                    # if content_split[0] == '下單' and len(content_split) > 1:
                    sign_rules = {
                        'plus sign': '+',
                        '加': '+',
                        '＋': '+',
                        '十': '+',
                        '十': '+',
                        '(': '',
                        ')': '',
                        '囗': '口',
                        ' ': '',
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
                    flag = 0  # 紀錄最後處理狀態

                    # 判斷留言是否有取貨地點
                    endRow = len(content_split)
                    customPUAreaFK = 0

                    print(content_split)
                    if content_split[-1].find("取") > 0:
                        flag = -1
                        adata = getPickupAreas(models, uid,
                                               #    content_split[len(content_split) - 1][:content_split[len(content_split) - 1].find("取")]
                                               content_split[-1].split('取')[0].replace('囗', '口').strip()
                                               )
                        if len(adata) != 0:
                            customPUAreaFK = adata[0]['id']
                            flag = 0
                        else:
                            flag = 4
                        endRow = endRow - 1

                    if endRow == 0:
                        flag = 1
                    else:
                        # 對每行留言進行分析
                        pickup_dates = {}  # 0504
                        for i in range(1, endRow):
                            for rep, val in sign_rules.items():
                                content_split[i] = content_split[i].replace(rep, val)
                            content = content_split[i].strip().split('+')
                            print(content)
                            # 如果下單項目被+號切割後數量不等於2或數量不等於整數
                            if len(content) != 2:
                                flag = 1
                                break
                            try:
                                content[1] = int(content[1].strip())
                            except ValueError:
                                flag = 1
                                break
                            if content[1] == 0:
                                flag = 1
                                break

                            # 檢查商品是否存在
                            check = getProductDataWithKeyword(models, uid, content[0].strip())
                            if len(check) == 0 or check['sale_ok'] == False:
                                flag = 2
                                break
                            # ==========0504==========
                            else:
                                if check['pickup_date'] in pickup_dates.keys():
                                    pickup_dates[check['pickup_date']].append((check['id'], content[1]))
                                else:
                                    pickup_dates[check['pickup_date']] = [(check['id'], content[1])]
                            # ========================

                            # 檢查商品庫存數量是否足夠
                            s_status, s_inStock = checkInStock(models, uid, check['id'], int(content[1]))
                            if not s_status:
                                flag = 3
                                break

                            if customPUAreaFK == 0:
                                customPUAreaFK = getPartnerPUArea(models, uid, comment['partner_id'][0])
                                if not customPUAreaFK:
                                    flag = 4

                            if comment['partner_id'][0] == 2:
                                    flag = 7

                    if flag == 0:
                        orderName = ""
                        for day in pickup_dates.keys():
                            print(comment['partner_id'][0], day, customPUAreaFK)
                            orderId = newOrder(models, uid, comment['partner_id'][0], day, customPUAreaFK)
                            print(orderId)
                            # ========= 0504棄用 ==========
                            # for i in range(0, endRow):
                            #     content = content_split[i].split('+')
                            #     product_keyword, amount_str = content[0].strip(), content[1].strip()
                            #     product = getProductDataWithKeyword(models, uid, product_keyword)
                            #     # print(orderId, 10-1+i , int(amount_str), product, len(product_keyword))
                            #     newOrderLine(models, uid, orderId, 10 - 1 + i, product['id'], int(amount_str))
                            # ============================
                            for i, item in enumerate(pickup_dates[day]):  # 0504
                                # print(item) # 0504
                                newOrderLine(models, uid, orderId, 10 - 1 + i, item[0], item[1])  # 0504
                            order_result = getOrderData(models, uid, orderId)
                            if orderName == "":
                                orderName += order_result['name']
                            else:
                                orderName += '&{}'.format(order_result['name'])
                        print(orderName)
                        updateCommentState(models, uid, comment['id'], 'Done=' + orderName)
                        print('[' + str(comment['id']) + ': Done=' + orderName + ']')
                    elif flag == 1:
                        updateCommentState(models, uid, comment['id'], 'Error#1:格式錯誤')
                        print('[' + str(comment['id']) + ': Error_1=格式錯誤]')
                    elif flag == 2:
                        updateCommentState(models, uid, comment['id'], 'Error#2:找不到商品')
                        print('[' + str(comment['id']) + ': Error_2=找不到商品]')
                    elif flag == 3:
                        updateCommentState(models, uid, comment['id'], 'Error#3:庫存不足')
                        print('[' + str(comment['id']) + ': Error_3=庫存不足]')
                    elif flag == 4:
                        updateCommentState(models, uid, comment['id'], 'Error#4:取貨地點有誤')
                        print('[' + str(comment['id']) + ': Error_4=取貨地點有誤]')
                    elif flag == 5:
                        updateCommentState(models, uid, comment['id'], 'Error#5:ID與資料庫未配對')
                        print('[' + str(comment['id']) + ': Error_5=ID與資料庫未配對]')
                    elif flag == 6:
                        updateCommentState(models, uid, comment['id'], 'Error#6:未註冊or授權')
                        print('[' + str(comment['id']) + ': Error_6=未註冊or授權]')
                    elif flag == 7:
                        updateCommentState(models, uid, comment['id'], 'Error#7:ID填寫錯誤')
                        print('[' + str(comment['id']) + ': Error_7=ID填寫錯誤]')
                    # else:
                    #     updateCommentState(comment['id'], 'Error#0')
                    #     print('['+str(comment['id'])+': Error_0=沒有下單動作]')
                    # time.sleep(0.1)
                else:
                    updateCommentState(models, uid, comment['id'], 'Error#1:格式錯誤')
                    print('[' + str(comment['id']) + ': Error_1=格式錯誤]')
            print('處理留言完成。')
        else:
            print('沒有需要處理的留言。')
    # 將狀態傳回網頁
    if facebook_status == '': facebook_status = '無異常狀況'
    writeFacebookStatus(models, uid, configID, facebook_status)

'''
    print('檢查產品數量是否充足...檢查中')

    configs = configparser.ConfigParser()
    configs.read('announce.ini', 'utf-8')
    import requests

    product_announce, amount_announce = getAmountLessProducts(models, uid)
    # print(product_announce[0]['name'])

    print("數量預警的產品:")
    print(product_announce)
    print("數量:")
    print(amount_announce)

    # 找尋對應FB post
    site, content = getValidPostMessage(models, uid)

    print("發送警示訊息...")
    for index in range(len(product_announce)):
        for item in range(len(content)):
            if content[item].find(product_announce[index]['product_keywords']) >= 0:
                month = str(datetime.strptime(product_announce[0]['sale_end_date'], "%Y-%m-%d %H:%M:%S").month).zfill(2)
                product = product_announce[index]['product_keywords']
                try:
                    rec_amount = configs[month][product]
                except:
                    rec_amount = 1000
                print("原始數量:{}".format(rec_amount))
                print("剩餘數量:{}".format(amount_announce[index]))
                if int(rec_amount) > int(amount_announce[index]):
                    try:
                        configs.add_section(month)
                    except:
                        pass
                    configs.set(month, product, str(int(amount_announce[index])))

                    messages = "\nHI~~美女管理員😉\n[{}]已經剩下最後{}份\n請前往下方網址關閉留言:\n{}".format(product_announce[index]['name'],
                                                                                       int(amount_announce[index]),
                                                                                       site[item])
                    url = 'https://notify-api.line.me/api/notify'
                    payload = {'message': messages}
                    headers = {'Authorization': 'Bearer LIYcisceht12YChwFk7gJ3NKXouzaOcFiAdinIw1Uim'}
                    res = requests.post(url, data=payload, headers=headers)
                    # res = requests.post('https://notify-api.line.me/api/status', data=payload, headers=headers)
                    print(res)
                    print("成功發送:{}".format(messages))

    with open('announce.ini', 'w', encoding='utf-8') as configfile:
        configs.write(configfile)
    print("發送完畢")
'''
# print('\n[程式結束]')

# coding=utf-8
