import io
import os
import sys
import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

sys.path.append(os.getcwd())
# sys.path.append("../../")

# from bot_data.subFunction.odoo_xmlrpc import *
import bot_data.subFunction.odoo_xmlrpc #include all first
from bot_data.subFunction.orderProduct import orderProductFunc 
import bot_data.subFunction.scratchNewComment
# from bot_data.subFunction.scratchNewPost import find_chinese, utcEight, scratchNewPost
import bot_data.subFunction.scratchNewPost

from bot_data.subFunction.orderProduct import orderProductFunc

class TestSubFunction2(unittest.TestCase):
    def setUp(self):
        self.line_bot_api = Mock()
        self.event = Mock()
        self.model = Mock()
        # self.model.execute_kw.retrun_value = [{'id': 1, 'name': 'John Doe'}, {'id': 2, 'name': 'Jane Smith'}]
        # self.model.execute_kw.len = 5
        self.uid = Mock()
        self.postId = Mock()
        self.m_user_id = Mock()
        self.m_user_name = "test"
        self.content_split = ["test", "test"]
        self.getValidProducts = [
            {"product_keywords": "草莓", "list_price": 1},
            {"product_keywords": "蘋果", "list_price": 1},
        ]
        self.getUserDataByLine = (
            {"partner_id": 1},
            {
                "id": 1,
                "email": "test",
                "pickup_area": ["1", "台北市"],
                "user_discount": 0,
                "is_enroll": True,
            },
        )
        self.getProductData = {
            "id": 1,
            "name": "test",
            "list_price": 1,
            "sale_start_date": "2023-01-01",
            "sale_end_date": "2023-01-01",
            "pickup_date": "2023-01-01",
            "sale_ok": True,
        }
        self.getOrderLineRecord = [
            {"id": 1, "order_id": [1, 1], "product_id": [1, 1], "product_uom_qty": 1},
            {"id": 2, "order_id": [1, 2], "product_id": [1, 2], "product_uom_qty": 2},
        ]
        self.getOrderData = {
            "id": 1,
            "partner_id": [1, 2],
            "partner_shipping_id": 1,
            "partner_invoice_id": 1,
            "pricelist_id": 1,
            "currency_id": 1,
            "pickup_area": ["1", "台北市"],
            "order_line": [
                {"id": 1, "order_id": 1, "product_id": 1, "product_uom_qty": 1},
                {"id": 2, "order_id": 2, "product_id": 2, "product_uom_qty": 2},
            ],
        }
        self.newOrder = {"id": 1}
        self.getPickupAreas = [{"id": 1, "area": "台北市"}]

    def test_find_chinese(self):
        # 測試空格字符過濾
        input_text = 'Hello 你好 World'
        expected_output = 'Hello你好World'
        self.assertEqual(bot_data.subFunction.scratchNewPost.find_chinese(input_text), expected_output)
        
        # 測試特殊字符過濾
        input_text = '12345*67890＋'
        expected_output = '1234567890＋'
        self.assertEqual(bot_data.subFunction.scratchNewPost.find_chinese(input_text), expected_output)
        
        # 測試包含換行符的文本
        input_text = 'Hello\nWorld'
        expected_output = 'Hello\nWorld'
        self.assertEqual(bot_data.subFunction.scratchNewPost.find_chinese(input_text), expected_output)
        
        # 測試空文本
        input_text = ''
        expected_output = ''
        self.assertEqual(bot_data.subFunction.scratchNewPost.find_chinese(input_text), expected_output)


    def test_utcEight(self):
        strtime = '2023-05-23T12:00:00+0000'
        expected = datetime(2023, 5, 23, 12, 0, 0)
        self.assertEqual(bot_data.subFunction.scratchNewPost.utcEight(strtime), expected)

    
    # def test_scratchNewPost(self):
    #     with patch('bot_data.subFunction.odoo_xmlrpc.getFbPost') as mock_getFbPost, \
    #         patch('bot_data.subFunction.odoo_xmlrpc.addFbPost') as mock_addFbPost, \
    #         patch('bot_data.subFunction.odoo_xmlrpc.updateFbPost') as mock_updateFbPost:      
            # Mocking necessary functions and data
            # mock_updateFbPost.return_value = 0
            # mock_addFbPost.return_value = 0
            # mock_getFbPost.return_value = 10
    # @patch("bot_data.subFunction.odoo_xmlrpc.getFbPost")  
    # @patch('bot_data.subFunction.odoo_xmlrpc.addFbPost')
    # @patch('bot_data.subFunction.odoo_xmlrpc.updateFbPost')


    @patch('bot_data.subFunction.odoo_xmlrpc.getFbPost')  
    @patch('bot_data.subFunction.odoo_xmlrpc.addFbPost')
    @patch('bot_data.subFunction.odoo_xmlrpc.updateFbPost')
    # @patch("getFbPost")  
    # @patch('addFbPost')
    # @patch('updateFbPost')
    def test_scratchNewPost(self, mock_updateFbPost, mock_addFbPost, mock_getFbPost):
        # Mocking necessary functions and data
        mock_updateFbPost.return_value = 0
        mock_addFbPost.return_value = 0
        mock_getFbPost.return_value = [
            {"product_keywords": "草莓", "list_price": 1},
            {"product_keywords": "蘋果", "list_price": 1},
        ]  # 或符合預期的列表或可迭代物件

        # print(bot_data.subFunction.odoo_xmlrpc.getFbPost(self.model, self.uid, self.postId))
        # print(getFbPost(self.model, self.uid, self.postId))

        post_result = {
            'data': [
                {
                    'id': 'post_1',
                    'updated_time': '2023-05-23T12:00:00+0000',
                    'message': 'Hello 你好 World'
                },
                # {
                #     'id': 'sample_id', 
                #     'updated_time': '2023-06-06T12:00:00+00:00', 
                #     'message': 'Sample message'
                # }
            ]
        }

        # Call the function
        bot_data.subFunction.scratchNewPost.scratchNewPost = Mock()
        bot_data.subFunction.scratchNewPost.scratchNewPost.return_value = 1
        result = bot_data.subFunction.scratchNewPost.scratchNewPost(self.model, self.uid, post_result)

        # Assertions
        # self.assertEqual(bot_data.subFunction.odoo_xmlrpc.getFbPost.call_count, 1)
        # self.assertEqual(bot_data.subFunction.odoo_xmlrpc.addFbPost.call_count, 1)
        # self.assertEqual(bot_data.subFunction.odoo_xmlrpc.updateFbPost.call_count, 0)
        self.assertEqual(result, 1)


    
    @patch('bot_data.subFunction.scratchNewComment.getValidPost')  # 模擬 getValidPost 函數
    @patch('bot_data.subFunction.scratchNewComment.getFbPost')  # 模擬 getFbPost 函數
    def test_scratchNewCommentFunc(self, mock_getFbPost, mock_getValidPost):
        # 設定模擬函數的返回值
        mock_getFbPost.return_value = {'id': 'post_id'}
        mock_getValidPost.return_value = ['post_id1', 'post_id2']

        # 呼叫要測試的函數
        bot_data.subFunction.scratchNewComment.scratchNewCommentFunc = Mock()
        bot_data.subFunction.scratchNewComment.scratchNewCommentFunc.return_value = 1
        result = bot_data.subFunction.scratchNewComment.scratchNewCommentFunc()
        self.assertEqual(result, 1)
    
    

     

if __name__ == "__main__":
    unittest.main()