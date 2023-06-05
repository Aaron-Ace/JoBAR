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
from bot_data.subFunction.pickupInfo import pickupInfoFunc
from bot_data.subFunction.processComment import processCommentFunc
from bot_data.subFunction.productDelete import productDeleteFunc
from bot_data.subFunction.productModify import productModifyFunc
from bot_data.subFunction.scratchNewComment import scratchNewCommentFunc
from bot_data.subFunction.scratchNewPost import scratchNewPost


class TestSubFunction(unittest.TestCase):
    def setUp(self):
        self.line_bot_api = Mock()
        self.event = Mock()
        self.model = Mock()
        self.uid = Mock()
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

    def test_customerServiceFunc(self):
        self.assertEqual(
            customerServiceFunc(self.m_user_name),
            "Hi, test:\n請點選下方連結前往真人客服尋求更多幫助!\nhttps://reurl.cc/qLg1dp",
        )

    @patch("bot_data.subFunction.feasibleOrderProduct.getValidProducts")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_feasibleOrderProductFunc(self, mock_stdout, mock_getValidProducts):
        mock_getValidProducts.return_value = self.getValidProducts
        feasibleOrderProductFunc(
            self.line_bot_api, self.model, self.uid, self.m_user_name
        )
        self.assertEqual(mock_stdout.getvalue(), "回覆Flex Message\n")

    def test_instructionHelperFunc(self):
        self.assertEqual(
            instructionHelperFunc(self.m_user_name),
            "Hi, test:\n👇以下為機器人指令👇\n\n[貨品更新]\n取貨更新\n關鍵字:{}\n新取貨日:YYYY-MM-DD\n價格:{}\n\n[貨品刪除]\n貨品刪除\n關鍵字:{}",
        )

    @patch("bot_data.subFunction.orderProduct.getProductDataWithKeyword")
    @patch("bot_data.subFunction.orderProduct.checkInStock")
    @patch("bot_data.subFunction.orderProduct.getUserDataByLine")
    @patch("bot_data.subFunction.orderProduct.newOrder")
    @patch("bot_data.subFunction.orderProduct.getOrderLineSequence")
    @patch("bot_data.subFunction.orderProduct.newOrderLine")
    def test_orderProductFunc_flag0(
        self,
        mock_newOrderLine,
        mock_getOrderLineSequence,
        mock_newOrder,
        mock_getUserDataByLine,
        mock_checkInStock,
        mock_getProductDataWithKeyword,
    ):
        mock_getProductDataWithKeyword.return_value = self.getProductData
        mock_checkInStock.return_value = (True, 1)
        mock_getUserDataByLine.return_value = self.getUserDataByLine
        mock_newOrder.return_value = self.newOrder
        mock_getOrderLineSequence.return_value = 1
        content_split = ["test", "test+1"]
        self.assertEqual(
            orderProductFunc(
                self.model,
                self.uid,
                self.m_user_name,
                self.m_user_id,
                content_split,
            ),
            "Hi, test:\n下單成功🤩",
        )

    @patch("bot_data.subFunction.orderProduct.getUserDataByLine")
    def test_orderProductFunc_flag1(
        self,
        mock_getUserDataByLine,
    ):
        mock_getUserDataByLine.return_value = self.getUserDataByLine
        content_split = ["test", "test"]
        self.assertEqual(
            orderProductFunc(
                self.model,
                self.uid,
                self.m_user_name,
                self.m_user_id,
                content_split,
            ),
            "Hi, test:\n糟糕😰格式好像哪裡出錯了\n請確認之後再試一遍🥺",
        )

    @patch("bot_data.subFunction.orderProduct.getProductDataWithKeyword")
    @patch("bot_data.subFunction.orderProduct.checkInStock")
    @patch("bot_data.subFunction.orderProduct.getUserDataByLine")
    def test_orderProductFunc_flag2(
        self,
        mock_getUserDataByLine,
        mock_checkInStock,
        mock_getProductDataWithKeyword,
    ):
        mock_getProductDataWithKeyword.return_value = {
            "id": 1,
            "name": "test",
            "list_price": 1,
            "sale_start_date": "2023-01-01",
            "sale_end_date": "2023-01-01",
            "pickup_date": "2023-01-01",
            "sale_ok": False,
        }
        mock_checkInStock.return_value = (True, 1)
        mock_getUserDataByLine.return_value = self.getUserDataByLine
        content_split = ["test", "test+1"]
        self.assertEqual(
            orderProductFunc(
                self.model,
                self.uid,
                self.m_user_name,
                self.m_user_id,
                content_split,
            ),
            "Hi, test:\n我找不到這樣商品耶...😅\n請確認關鍵字正確之後再試一遍😘",
        )

    @patch("bot_data.subFunction.orderProduct.getProductDataWithKeyword")
    @patch("bot_data.subFunction.orderProduct.checkInStock")
    @patch("bot_data.subFunction.orderProduct.getUserDataByLine")
    def test_orderProductFunc_flag3(
        self,
        mock_getUserDataByLine,
        mock_checkInStock,
        mock_getProductDataWithKeyword,
    ):
        mock_getProductDataWithKeyword.return_value = self.getProductData
        mock_checkInStock.return_value = (True, 1)
        mock_getUserDataByLine.return_value = ([], [])
        content_split = ["test", "test+1"]
        self.assertEqual(
            orderProductFunc(
                self.model,
                self.uid,
                self.m_user_name,
                self.m_user_id,
                content_split,
            ),
            "Hi, test:\n您好像還沒綁定帳號喔🧐\n請前往下方網址以Line註冊登入並且填寫相關資料\nhttps://reurl.cc/an9xXX",
        )

    @patch("bot_data.subFunction.orderProduct.getProductDataWithKeyword")
    @patch("bot_data.subFunction.orderProduct.checkInStock")
    @patch("bot_data.subFunction.orderProduct.getUserDataByLine")
    def test_orderProductFunc_flag4(
        self,
        mock_getUserDataByLine,
        mock_checkInStock,
        mock_getProductDataWithKeyword,
    ):
        mock_getProductDataWithKeyword.return_value = self.getProductData
        mock_checkInStock.return_value = (True, 1)
        mock_getUserDataByLine.return_value = (
            {"partner_id": 1},
            {
                "id": 1,
                "email": "test",
                "pickup_area": [],
                "user_discount": 0,
                "is_enroll": True,
            },
        )
        content_split = ["test", "test+1"]
        self.assertEqual(
            orderProductFunc(
                self.model,
                self.uid,
                self.m_user_name,
                self.m_user_id,
                content_split,
            ),
            "Hi, test:\n您尚未設定有效的取貨地點哦😮\n請前往下方網址設定!\nhttps://reurl.cc/an9xXX",
        )

    @patch("bot_data.subFunction.orderProduct.getProductDataWithKeyword")
    @patch("bot_data.subFunction.orderProduct.checkInStock")
    @patch("bot_data.subFunction.orderProduct.getUserDataByLine")
    def test_orderProductFunc_flag5(
        self,
        mock_getUserDataByLine,
        mock_checkInStock,
        mock_getProductDataWithKeyword,
    ):
        mock_getProductDataWithKeyword.return_value = self.getProductData
        mock_checkInStock.return_value = (False, 1)
        mock_getUserDataByLine.return_value = self.getUserDataByLine
        content_split = ["test", "test+1"]
        self.assertEqual(
            orderProductFunc(
                self.model,
                self.uid,
                self.m_user_name,
                self.m_user_id,
                content_split,
            ),
            "Hi, test:\ntest數量不足了\n請您調整數量後再嘗試🥲",
        )

    @patch("bot_data.subFunction.orderProduct.getPickupAreas")
    @patch("bot_data.subFunction.orderProduct.getProductDataWithKeyword")
    @patch("bot_data.subFunction.orderProduct.checkInStock")
    @patch("bot_data.subFunction.orderProduct.getUserDataByLine")
    def test_orderProductFunc_flag6(
        self,
        mock_getUserDataByLine,
        mock_checkInStock,
        mock_getProductDataWithKeyword,
        mock_getPickupAreas,
    ):
        mock_getProductDataWithKeyword.return_value = self.getProductData
        mock_checkInStock.return_value = (True, 1)
        mock_getUserDataByLine.return_value = self.getUserDataByLine
        mock_getPickupAreas = self.getPickupAreas
        content_split = ["test", "test+1", "1取貨地點"]
        self.assertEqual(
            orderProductFunc(
                self.model,
                self.uid,
                self.m_user_name,
                self.m_user_id,
                content_split,
            ),
            "Hi, test:\n糟糕😰取貨地點好像打錯了\n請確認之後再試一遍🥲",
        )

    @patch("bot_data.subFunction.orderProduct.getProductDataWithKeyword")
    @patch("bot_data.subFunction.orderProduct.checkInStock")
    @patch("bot_data.subFunction.orderProduct.getUserDataByLine")
    def test_orderProductFunc_flag7(
        self,
        mock_getUserDataByLine,
        mock_checkInStock,
        mock_getProductDataWithKeyword,
    ):
        mock_getProductDataWithKeyword.return_value = self.getProductData
        mock_checkInStock.return_value = (False, 0)
        mock_getUserDataByLine.return_value = self.getUserDataByLine
        content_split = ["test", "test+1"]
        self.assertEqual(
            orderProductFunc(
                self.model,
                self.uid,
                self.m_user_name,
                self.m_user_id,
                content_split,
            ),
            "Hi, test:\ntest 已經賣完了🥲\n請您調整下單內容後再試一次😣",
        )

    @patch("bot_data.subFunction.personalData.getUserDataByLine")
    def test_personalDataFunc(self, mock_getUserDataByLine):
        mock_getUserDataByLine.return_value = self.getUserDataByLine
        personalDataFunc(
            self.line_bot_api,
            self.event,
            self.model,
            self.uid,
            self.m_user_id,
            self.m_user_name,
        )
        mock_getUserDataByLine.assert_called_once_with(
            self.model, self.uid, self.m_user_id
        )

    @patch("bot_data.subFunction.personalOrder.getUserDataByLine")
    @patch("bot_data.subFunction.personalOrder.getRecentOrders")
    def test_personalOrderFunc(self, mock_getRecentOrders, mock_getUserDataByLine):
        mock_getUserDataByLine.return_value = self.getUserDataByLine
        mock_getRecentOrders.return_value = ""
        personalOrderFunc(
            self.line_bot_api,
            self.event,
            self.model,
            self.uid,
            self.m_user_name,
            self.m_user_id,
        )
        mock_getUserDataByLine.assert_called_once_with(
            self.model, self.uid, self.m_user_id
        )
        mock_getRecentOrders.assert_called_once_with(self.model, self.uid, 1)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_pickupInfoFunc(self, mock_stdout):
        pickupInfoFunc(self.line_bot_api, self.m_user_id)
        self.assertEqual(
            mock_stdout.getvalue(),
            "回覆Flex Message\n",
        )

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_processCommentFunc(self, mock_stdout):
        processCommentFunc("")
        self.assertEqual(
            mock_stdout.getvalue(),
            "沒有需要處理的留言。\n",
        )

    @patch("bot_data.subFunction.productDelete.getProductDataWithKeyword")
    @patch("bot_data.subFunction.productDelete.getOrderLineRecord")
    @patch("bot_data.subFunction.productDelete.updateOrderLineAmount")
    def test_productDeleteFunc(
        self, mock_updateOrderLineAmount, mock_getOrderLineRecord, mock_getProductData
    ):
        mock_getProductData.return_value = self.getProductData
        mock_getOrderLineRecord.return_value = self.getOrderLineRecord
        mock_updateOrderLineAmount.return_value = 1
        self.assertEqual(
            productDeleteFunc(self.model, self.uid, self.content_split),
            "Hi, 管理員:刪除成功!\n===============\n[成功刪除筆數]:2\n[失敗刪除筆數]:0\n===============\n[總共刪除筆數]:2",
        )

    @patch("bot_data.subFunction.productModify.getProductDataWithKeyword")
    @patch("bot_data.subFunction.productModify.updateProductPickupDate")
    @patch("bot_data.subFunction.productModify.getOrderLineRecord")
    @patch("bot_data.subFunction.productModify.getOrderData")
    @patch("bot_data.subFunction.productModify.newOrder")
    @patch("bot_data.subFunction.productModify.getOrderLineSequence")
    @patch("bot_data.subFunction.productModify.newOrderLine")
    @patch("bot_data.subFunction.productModify.updateOrderLineAmount")
    def test_productModifyFunc(
        self,
        mock_updateOrderLineAmount,
        mock_newOrderLine,
        mock_getOrderLineSequence,
        mock_newOrder,
        mock_getOrderData,
        mock_getOrderLineRecord,
        mock_updateProductPickupDate,
        mock_getProductData,
    ):
        content_split = [
            "test",
            "1234test_keywords",
            "12345test_pickup_date",
            "123test_price",
        ]
        mock_getProductData.return_value = self.getProductData
        mock_updateProductPickupDate.return_value = 1
        mock_getOrderLineRecord.return_value = self.getOrderLineRecord
        mock_getOrderData.return_value = self.getOrderData
        mock_newOrder.return_value = self.newOrder
        mock_getOrderLineSequence.return_value = 1
        mock_updateOrderLineAmount.return_value = 1
        self.assertEqual(
            productModifyFunc(self.model, self.uid, content_split),
            "Hi, 管理員:更新成功!\n===============\n[成功更新筆數]:2\n[失敗更新筆數]:0\n===============\n[總共更新筆數]:2",
        )


if __name__ == "__main__":
    unittest.main()
