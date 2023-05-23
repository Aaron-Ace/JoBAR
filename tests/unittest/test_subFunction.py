import io
import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.append(os.getcwd())
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
from bot_data.subFunction.scratchNewPost import scratchNewPost


class TestSubFunction(unittest.TestCase):
    def setUp(self):
        self.model = Mock()
        self.uid = Mock()
        self.m_user_id = Mock()
        self.m_user_name = "test"

    def test_customerServiceFunc(self):
        self.assertEqual(
            customerServiceFunc(self.m_user_name),
            "Hi, test:\n小幫手不能幫你回答問題QQ\n請點選下方連結前往好好吃真人客服尋求更多幫助喔!\nhttps://reurl.cc/oe6m4v",
        )

    @patch("bot_data.subFunction.feasibleOrderProduct.getValidProducts")
    def test_feasibleOrderProductFunc(self, mock_getValidProducts):
        mock_getValidProducts.return_value = [
            {"product_keywords": "草莓"},
            {"product_keywords": "蘋果"},
        ]
        self.assertEqual(
            feasibleOrderProductFunc(self.model, self.uid, self.m_user_name),
            "Hi, test:\n以下為目前可訂購商品列表:\n\n喊單關鍵字：草莓\n喊單關鍵字：蘋果\n請喊關鍵字+數量喔\n\n範例:\n下單(換行)\n草莓+1(換行)\n蘋果+1",
        )

    def test_instructionHelperFunc(self):
        self.assertEqual(
            instructionHelperFunc(self.m_user_name),
            "Hi, test:\n👇以下為機器人指令👇\n\n[貨品更新]\n取貨更新\n關鍵字:{}\n新取貨日:YYYY-MM-DD\n價格:{}\n\n[貨品刪除]\n貨品刪除\n關鍵字:{}",
        )

    @patch("bot_data.subFunction.personalData.getUserDataByLine")
    def test_personalDataFunc(self, mock_getUserDataByLine):
        mock_getUserDataByLine.return_value = (
            "user",
            {
                "id": 1,
                "email": "test",
                "pickup_area": ["1", "台北市"],
                "user_discount": 0,
                "is_enroll": True,
            },
        )
        personalDataFunc(self.model, self.uid, self.m_user_id, self.m_user_name)
        mock_getUserDataByLine.assert_called_once_with(
            self.model, self.uid, self.m_user_id
        )

    @patch("bot_data.subFunction.personalOrder.getUserDataByLine")
    @patch("bot_data.subFunction.personalOrder.getRecentOrders")
    def test_personalOrderFunc(self, mock_getRecentOrders, mock_getUserDataByLine):
        mock_getUserDataByLine.return_value = (
            {"partner_id": 1},
            {
                "id": 1,
                "email": "test",
                "pickup_area": ["1", "台北市"],
                "user_discount": 0,
                "is_enroll": True,
            },
        )
        mock_getRecentOrders.return_value = ""

        personalOrderFunc(self.model, self.uid, self.m_user_name, self.m_user_id)
        mock_getUserDataByLine.assert_called_once_with(
            self.model, self.uid, self.m_user_id
        )
        mock_getRecentOrders.assert_called_once_with(self.model, self.uid, 1)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_processCommentFunc(self, mock_stdout):
        processCommentFunc("")
        self.assertEqual(
            mock_stdout.getvalue(),
            "沒有需要處理的留言。\n",
        )


if __name__ == "__main__":
    unittest.main()
