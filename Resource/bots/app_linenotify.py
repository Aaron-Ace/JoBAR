import configparser
import requests
from datetime import datetime, timedelta
from odoo_xmlrpc import *


print('檢查產品數量是否充足...檢查中')

configs = configparser.ConfigParser()
configs.read('announce.ini', 'utf-8')

models = endpoint_object()
uid = conflictRetry(get_uid())

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
        if content[item].find(product_announce[index]['product_keywords']) != -1:
            year = str(datetime.now().date().strftime("%Y"))
            month = str(datetime.strptime(product_announce[0]['sale_end_date'], "%Y-%m-%d %H:%M:%S").month).zfill(2)
            product = product_announce[index]['product_keywords']
            try:
                rec_amount = configs[year+month][product]
            except:
                rec_amount = 9999
            print("原始數量:{}".format(rec_amount))
            print("剩餘數量:{}".format(amount_announce[index]))

            if int(rec_amount) > int(amount_announce[index]) and int(amount_announce[index]) < 10 :
                try:
                    configs.add_section(year+month)
                except:
                    pass
                    #print("Error occured")
                #print(year+month)
                #print(product)
                configs.set(year+month, product, str(int(amount_announce[index])))

                messages = "\n[{}]已經剩下最後{}份\n請前往下方網址關閉留言:\n{}".format(product_announce[index]['name'],
                                                                                   int(amount_announce[index]),
                                                                                   site[item])
                url = 'https://notify-api.line.me/api/notify'
                payload = {'message': messages}
                headers = {'Authorization': 'Bearer SLrFL2wkBdwsxp4uoTgZBGiiP18rh66ZIzsql4kitkJ'}
                res = requests.post(url, data=payload, headers=headers)
                # res = requests.post('https://notify-api.line.me/api/status', data=payload, headers=headers)
                # print(res)
                print("成功發送:{}".format(messages))

with open('announce.ini', 'w', encoding='utf-8') as configfile:
    configs.write(configfile)
print("發送完畢")
