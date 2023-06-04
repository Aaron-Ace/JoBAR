from linebot.models import FlexSendMessage

def pickupInfoFunc(line_bot_api, m_user_id):
    jsonMsg = {
        "type": "carousel",
        "contents": [
            {
                "type": "bubble",
                "size": "kilo",
                "hero": {
                    "type": "image",
                    "url": "https://image.cache.storm.mg/styles/smg-800x533-fp/s3/media/image/2017/02/17/20170217-104051_U1841_M248788_fbcc.JPG?itok=p-t99m-l",
                    "size": "full",
                    "aspectMode": "cover",
                    "aspectRatio": "320:213"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "取貨資訊",
                            "size": "xxs",
                            "color": "#1DB446"
                        },
                        {
                            "type": "text",
                            "text": "交大(08:00-17:00)",
                            "weight": "bold",
                            "size": "md",
                            "wrap": True
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "wrap": True,
                                            "color": "#8c8c8c",
                                            "size": "xs",
                                            "flex": 5,
                                            "text": "30010新竹市東區大學路1001號"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "separator"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "前往地圖",
                                "uri": "https://goo.gl/maps/Mb2GRPWzszKMknnb9"
                            }
                        }
                    ],
                    "spacing": "sm",
                    "paddingAll": "13px"
                }
            },
            {
                "type": "bubble",
                "size": "kilo",
                "hero": {
                    "type": "image",
                    "url": "https://lh5.googleusercontent.com/p/AF1QipO8EVjI2qG2UZ3hE3bBErtmwX5pGyYFKFkoUmai=w408-h306-k-no",
                    "size": "full",
                    "aspectMode": "cover",
                    "aspectRatio": "320:213"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "取貨資訊",
                            "size": "xxs",
                            "color": "#1DB446"
                        },
                        {
                            "type": "text",
                            "text": "陽明(08:00-17:00)",
                            "weight": "bold",
                            "size": "md",
                            "wrap": True
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "wrap": True,
                                            "color": "#8c8c8c",
                                            "size": "xs",
                                            "flex": 5,
                                            "text": "112台北市北投區立農街二段155號"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "separator"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "前往地圖",
                                "uri": "https://goo.gl/maps/gwb7xbJvzzZKqveB9"
                            }
                        }
                    ],
                    "spacing": "sm",
                    "paddingAll": "13px"
                }
            }
        ]
    }
    print("回覆Flex Message")
    line_bot_api.push_message(m_user_id, FlexSendMessage(alt_text="取貨資訊", contents=jsonMsg))