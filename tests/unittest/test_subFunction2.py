import io
import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta


sys.path.append("../../")
# sys.path.append("...")
# sys.path.append(os.getcwd())

from bot_data.subFunction.customerService import customerServiceFunc
from bot_data.subFunction.feasibleOrderProduct import feasibleOrderProductFunc
from bot_data.subFunction.instructionHelper import instructionHelperFunc
from bot_data.subFunction.odoo_xmlrpc import *
from bot_data.subFunction.orderProduct import orderProductFunc
from bot_data.subFunction.personalData import personalDataFunc
from bot_data.subFunction.personalOrder import personalOrderFunc
from bot_data.subFunction.processComment import processCommentFunc
from bot_data.subFunction.productDelete import productDeleteFunc
from bot_data.subFunction.productModify import productModifyFunc


from bot_data.subFunction.scratchNewComment import scratchNewCommentFunc
from bot_data.subFunction.scratchNewPost import find_chinese, utcEight, scratchNewPost



class TestSubFunction2(unittest.TestCase):
    def setUp(self):
        self.model = Mock()
        self.uid = Mock()
        self.m_user_id = Mock()
        self.m_user_name = "test"

    def test_find_chinese(self):
        # 測試空格字符過濾
        input_text = 'Hello 你好 World'
        expected_output = 'Hello你好World'
        self.assertEqual(find_chinese(input_text), expected_output)
        
        # 測試特殊字符過濾
        input_text = '12345*67890＋'
        expected_output = '1234567890＋'
        self.assertEqual(find_chinese(input_text), expected_output)
        
        # 測試包含換行符的文本
        input_text = 'Hello\nWorld'
        expected_output = 'Hello\nWorld'
        self.assertEqual(find_chinese(input_text), expected_output)
        
        # 測試空文本
        input_text = ''
        expected_output = ''
        self.assertEqual(find_chinese(input_text), expected_output)


    def test_utcEight(self):
        strtime = '2023-05-23T12:00:00+0000'
        expected = datetime(2023, 5, 23, 12, 0, 0)
        self.assertEqual(utcEight(strtime), expected)

    @patch('bot_data.subFunction.odoo_xmlrpc.getFbPost')
    @patch('bot_data.subFunction.odoo_xmlrpc.addFbPost')
    @patch('bot_data.subFunction.odoo_xmlrpc.updateFbPost')
    def test_scratchNewPost(self, mock_updateFbPost, mock_addFbPost, mock_getFbPost):
        # Mocking necessary functions and data
        mock_updateFbPost.return_value = None
        mock_addFbPost.return_value = None
        mock_getFbPost.return_value = {}

        models = endpoint_object()
        # models = 'models'
        uid = 'uid'
        post_result = {
            'data': [
                {
                    'id': 'post1',
                    'updated_time': '2023-05-23T12:00:00+0000',
                    'message': 'Hello 你好 World'
                }
            ]
        }

        # Call the function
        result = scratchNewPost(models, uid, post_result)

        # Assertions
        self.assertEqual(mock_getFbPost.call_count, 1)
        self.assertEqual(mock_addFbPost.call_count, 1)
        self.assertEqual(mock_updateFbPost.call_count, 0)
        self.assertEqual(result, 1)
    
    def test_scratchNewCommentFunc(self):
        pass
    

if __name__ == "__main__":
    unittest.main()
