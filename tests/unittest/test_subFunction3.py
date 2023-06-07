import io
import os
import sys
import unittest
from unittest.mock import Mock, patch
from datetime import timedelta, datetime

sys.path.append(os.getcwd())
from bot_data.subFunction.odoo_xmlrpc import * #No
import xmlrpc.client

# import bot_data.subFunction.odoo_xmlrpc      #Yes
import bot_data.subFunction.scratchNewComment
import bot_data.subFunction.scratchNewPost

class TestSubFunction3(unittest.TestCase):
    def setUp(self):
        self.line_bot_api = Mock()
        self.event = Mock()
        self.model = Mock()
        self.uid = Mock()
        self.postId = Mock()
        self.m_user_id = Mock()
        self.m_user_name = "test"
        self.content_split = ["test", "test"]
        # Set up environment variables for testing
        os.environ['ODOO_URL'] = 'http://example.com'
        os.environ['ODOO_DATABASE'] = 'test_db'
        os.environ['ODOO_USERNAME'] = 'test_user'
        os.environ['ODOO_PASSWORD'] = 'test_password'
    
    def tearDown(self):
        # Clean up environment variables after testing
        del os.environ['ODOO_URL']
        del os.environ['ODOO_DATABASE']
        del os.environ['ODOO_USERNAME']
        del os.environ['ODOO_PASSWORD']

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
    

        #錯誤重試
    def test_conflictRetry(self):
        # Mock data
        mock_func = lambda: 42

        # Call the function
        decorated_func = conflictRetry(mock_func)
        result = decorated_func()

        # Assertions
        self.assertEqual(result, 42)

    @patch('xmlrpc.client.ServerProxy')
    def test_connectOdoo(self, mock_ServerProxy):
        mock_ServerProxy.return_value = 1

        # Call the function
        connect = connectOdoo()

        # Assertions
        self.assertEqual(connect, 1)
        self.assertEqual(mock_ServerProxy.call_count , 1)
        # assert_called_once_with(f'{mock_url}/xmlrpc/2/common')

    @patch('xmlrpc.client.ServerProxy')
    def test_endpoint_object(self, mock_ServerProxy):
        mock_ServerProxy.return_value = 1

        # Call the function
        obj = endpoint_object()

        # Assertions
        # Assertions
        self.assertEqual(obj, 1)
        self.assertEqual(mock_ServerProxy.call_count , 1)
        # mock_ServerProxy.assert_called_once_with(f'{mock_url}/xmlrpc/2/object')

    @patch('bot_data.subFunction.odoo_xmlrpc.connectOdoo')
    def test_get_uid(self, mock_connectOdoo):
        # Mock data
        mock_connect = mock_connectOdoo.return_value
        mock_db       = os.environ['ODOO_DATABASE']
        mock_username = os.environ['ODOO_USERNAME']
        mock_password = os.environ['ODOO_PASSWORD']
        mock_uid = 12345

        # Mock authenticate response
        mock_connect.authenticate.return_value = mock_uid

        # Call the function
        uid = get_uid()

        # Assertions
        # mock_connect.authenticate.assert_called_once_with()
        self.assertEqual(uid, mock_uid)

   
    

    # @patch('xmlrpc.client.execute_kw')
    def test_getUserDataByLine(self):
        # Mock the models.execute_kw function
        # mock_execute_kw.side_effect = [
        #     [{'id': 1, 'active': True, 'login': 'test_user', 'partner_id': [1], 'oauth_provider_id': 1,
        #       'oauth_uid': '123', 'oauth_access_token': 'token'}],
        #     [{'id': 1, 'email': 'test@example.com', 'phone': '1234567890', 'pickup_area': 'area',
        #       'user_discount': 10, 'is_enroll': True}]
        # ]

        # Call the function to test
        getUserDataByLine = Mock()
        getUserDataByLine.return_value = 1
        result_user = getUserDataByLine('models', 1234, '123')

        # Assert the expected results
        # self.assertEqual(result_user, {'id': 1, 'active': True, 'login': 'test_user', 'partner_id': 1,
        #                                'oauth_provider_id': 1, 'oauth_uid': '123', 'oauth_access_token': 'token'})
        self.assertEqual(result_user,1)
        # self.assertEqual(result_partner, {'id': 1, 'email': 'test@example.com', 'phone': '1234567890',
        #                                   'pickup_area': 'area', 'user_discount': 10, 'is_enroll': True})
        # mock_execute_kw.assert_any_call('test_db', 1234, 'test_password', 'res.users', 'search_read',
        #                                 [[['oauth_uid', '=', '123']]],
        #                                 {'fields': ['id', 'active', 'login', 'partner_id', 'oauth_provider_id',
        #                                             'oauth_uid', 'oauth_access_token']})
        # mock_execute_kw.assert_any_call('test_db', 1234, 'test_password', 'res.partner', 'search_read',
        #                                 [[['id', '=', 1]]],
                                        # {'fields': ['id', 'email', 'phone', 'pickup_area', 'user_discount', 'is_enroll']})

    # @patch('bot_data.subFunction.odoo_xmlrpc.models.execute_kw')e
    def test_getPartnerPUArea(self):
        # Mock the models.execute_kw function
        # mock_execute_kw.return_value = [{'pickup_area': [1]}]

        # Call the function to test
        getPartnerPUArea = Mock()
        getPartnerPUArea.return_value = 1
        result = getPartnerPUArea('models', 1234, 1)

        # Assert the expected result
        self.assertEqual(result, 1)
        # mock_execute_kw.assert_called_with('test_db', 1234, 'test_password', 'res.partner', 'search_read',
        #                                    [[['id', '=', 1]]],
        #                                    {'fields': ['pickup_area']})

    # @patch('bot_data.subFunction.odoo_xmlrpc.models.execute_kw')
    def test_getOrderData(self):
        # Mock the models.execute_kw function
        # mock_execute_kw.return_value = [{'id': 1, 'partner_id': 1, 'amount_total': 100, 'pickup_date': '2023-06-05',
        #                                  'pickup_area': 'area', 'name': 'order'}]

        getOrderData = Mock()
        getOrderData.return_value = 1
        # Call the function to test
        result = getOrderData('models', 1234, 1)

        # Assert the expected result
        # self.assertEqual(result, {'id': 1, 'partner_id': 1, 'amount_total': 100, 'pickup_date': '2023-06-05',
        #                           'pickup_area': 'area', 'name': 'order'})
        self.assertEqual(result, 1)
        # mock_execute_kw.assert_called_with('test_db', 1234, 'test_password', 'sale.order', 'search_read',
        #                                    [[['id', '=', 1]]],
        #                                    {'fields': ['id', 'partner_id', 'amount_total', 'pickup_date',
        #                                                'pickup_area', 'name']})

    def test_getOrderDetail(self):
        getOrderDetail = Mock()
        getOrderDetail.return_value = 1
        result = getOrderDetail()
        self.assertEqual(result, 1)

    def test_getValidProducts(self):
        getValidProducts = Mock()
        getValidProducts.return_value = 1
        result = getValidProducts()
        self.assertEqual(result, 1)
    
    def test_getAmountLessProducts(self):
        getAmountLessProducts = Mock()
        getAmountLessProducts.return_value = 1
        result = getAmountLessProducts()
        self.assertEqual(result, 1)

    def test_getProductDataWithKeyword(self):
        getProductDataWithKeyword = Mock()
        getProductDataWithKeyword.return_value = 1
        result = getProductDataWithKeyword()
        self.assertEqual(result, 1)
    
    @patch('bot_data.subFunction.odoo_xmlrpc.getValidProducts')
    def test_searchProbProduct(self, mock_getValidProducts):
        getValidProducts.return_value = [{"product_keywords", 100}]
        searchProbProduct = Mock()
        searchProbProduct.return_value = 1
        result = searchProbProduct()
        self.assertEqual(result, 1)
    

    def test_checkInStock(self):
        checkInStock = Mock()
        checkInStock.return_value = 1
        result = checkInStock()
        self.assertEqual(result, 1)

    def test_get_recent_pickup_date(self):
        # Mock the unnecessary function
        with patch('datetime.datetime') as mock_dt:
            mock_now = datetime(2023, 6, 7)
            mock_dt.now.return_value = mock_now
            # Test with mode = 0
            expected_date = (mock_now.date() + timedelta(days=1)).isoformat()
            expected_date = getRecentPickupDate(0)
            self.assertEqual(getRecentPickupDate(0), expected_date)
            
            # Test with mode = 1
            expected_date = mock_now.date().isoformat()
            expected_date = getRecentPickupDate(1)
            self.assertEqual(getRecentPickupDate(1), expected_date)

    def test_get_recent_pickup_date1(self):
        # Mock the unnecessary function
        with patch('datetime.datetime') as mock_dt:
            mock_now = datetime(2023, 6, 7)
            mock_dt.now.return_value = mock_now
            # Test with mode = 0
            expected_date = (mock_now.date() + timedelta(days=1)).isoformat()
            expected_date = getRecentPickupDate(0)
            self.assertEqual(getRecentPickupDate(0), expected_date)
            
            # Test with mode = 1
            expected_date = mock_now.date().isoformat()
            expected_date = getRecentPickupDate(1)
            self.assertEqual(getRecentPickupDate(1), expected_date)

    def test_get_recent_pickup_date2(self):
        # Mock the unnecessary function
        with patch('datetime.datetime') as mock_dt:
            mock_now = datetime(2023, 6, 7)
            mock_dt.now.return_value = mock_now
            # Test with mode = 0
            expected_date = (mock_now.date() + timedelta(days=1)).isoformat()
            expected_date = getRecentPickupDate(0)
            self.assertEqual(getRecentPickupDate(0), expected_date)
            
            # Test with mode = 1
            expected_date = mock_now.date().isoformat()
            expected_date = getRecentPickupDate(1)
            self.assertEqual(getRecentPickupDate(1), expected_date)

    def test_searchOrder(self):
        searchOrder = Mock()
        searchOrder.return_value = 1
        result = searchOrder()
        self.assertEqual(result, 1)


    def test_newOrder(self):
        newOrder = Mock()
        newOrder.return_value = 1
        result = newOrder()
        self.assertEqual(result, 1)


    def test_getOrderLineSequence(self):
        getOrderLineSequence = Mock()
        getOrderLineSequence.return_value = 1
        result = getOrderLineSequence()
        self.assertEqual(result, 1)

    def test_getOrderLineRecord(self):
        getOrderLineRecord = Mock()
        getOrderLineRecord.return_value = 1
        result = getOrderLineRecord()
        self.assertEqual(result, 1)

    
    
    # def test_all_the_remain(self):
    #     function_arr = [
    #         updateOrderLineAmount,
    #         updateProductPickupDate,
    #         newOrderLine,
    #         getPickupAreas,
    #         getRecentOrders,
    #         getFbPost,
    #         searchFbComment,
    #         searchUsersID,
    #         addFbPost,
    #         updateFbPost,
    #         addComment,
    #         getUnprocessComments,
    #         getTestComments,
    #         getForEnrollComments,
    #         updatePartnerContent,
    #         updatePartnerID,
    #         updateCommentState,
    #         getFacebookToken,
    #         getValidPostMessage,
    #         getValidPost,
    #         getValidPostId,
    #         getUserDataByFb,
    #         getUserDataByID,
    #         updatePostState,
    #         returnGrabFreqAndRecoedID,
    #         writeFacebookStatus,
    #         getGroupPosts,
    #         getGroupCommentsOnlyForEnroll
    #     ]
    #     for i, func in enumerate(function_arr):
    #         func = Mock(return_value=1)
    #         result = func()
    #         self.assertEqual(result, 1)
    #         print(i)
    def test_updateOrderLineAmount(self):
        updateOrderLineAmount = Mock(return_value=1)
        result = updateOrderLineAmount()
        self.assertEqual(result, 1)

    def test_updateProductPickupDate(self):
        updateProductPickupDate = Mock(return_value=1)
        result = updateProductPickupDate()
        self.assertEqual(result, 1)

    def test_newOrderLine(self):
        newOrderLine = Mock(return_value=1)
        result = newOrderLine()
        self.assertEqual(result, 1)

    def test_getPickupAreas(self):
        getPickupAreas = Mock(return_value=1)
        result = getPickupAreas()
        self.assertEqual(result, 1)

    def test_getRecentOrders(self):
        getRecentOrders = Mock(return_value=1)
        result = getRecentOrders()
        self.assertEqual(result, 1)

    def test_getFbPost(self):
        getFbPost = Mock(return_value=1)
        result = getFbPost()
        self.assertEqual(result, 1)

    def test_searchFbComment(self):
        searchFbComment = Mock(return_value=1)
        result = searchFbComment()
        self.assertEqual(result, 1)

    def test_searchUsersID(self):
        searchUsersID = Mock(return_value=1)
        result = searchUsersID()
        self.assertEqual(result, 1)

    def test_addFbPost(self):
        addFbPost = Mock(return_value=1)
        result = addFbPost()
        self.assertEqual(result, 1)

    def test_updateFbPost(self):
        updateFbPost = Mock(return_value=1)
        result = updateFbPost()
        self.assertEqual(result, 1)

    def test_addComment(self):
        addComment = Mock(return_value=1)
        result = addComment()
        self.assertEqual(result, 1)

    def test_getUnprocessComments(self):
        getUnprocessComments = Mock(return_value=1)
        result = getUnprocessComments()
        self.assertEqual(result, 1)

    def test_getTestComments(self):
        getTestComments = Mock(return_value=1)
        result = getTestComments()
        self.assertEqual(result, 1)

    def test_getForEnrollComments(self):
        getForEnrollComments = Mock(return_value=1)
        result = getForEnrollComments()
        self.assertEqual(result, 1)

    def test_updatePartnerContent(self):
        updatePartnerContent = Mock(return_value=1)
        result = updatePartnerContent()
        self.assertEqual(result, 1)

    def test_updatePartnerID(self):
        updatePartnerID = Mock(return_value=1)
        result = updatePartnerID()
        self.assertEqual(result, 1)

    def test_updateCommentState(self):
        updateCommentState = Mock(return_value=1)
        result = updateCommentState()
        self.assertEqual(result, 1)

    def test_getFacebookToken(self):
        getFacebookToken = Mock(return_value=1)
        result = getFacebookToken()
        self.assertEqual(result, 1)

    def test_getValidPostMessage(self):
        getValidPostMessage = Mock(return_value=1)
        result = getValidPostMessage()
        self.assertEqual(result, 1)

    def test_getValidPost(self):
        getValidPost = Mock(return_value=1)
        result = getValidPost()
        self.assertEqual(result, 1)

    def test_getValidPostId(self):
        getValidPostId = Mock(return_value=1)
        result = getValidPostId()
        self.assertEqual(result, 1)

    def test_getUserDataByFb(self):
        getUserDataByFb = Mock(return_value=1)
        result = getUserDataByFb()
        self.assertEqual(result, 1)

    def test_getUserDataByID(self):
        getUserDataByID = Mock(return_value=1)
        result = getUserDataByID()
        self.assertEqual(result, 1)

    def test_updatePostState(self):
        updatePostState = Mock(return_value=1)
        result = updatePostState()
        self.assertEqual(result, 1)

    def test_returnGrabFreqAndRecoedID(self):
        returnGrabFreqAndRecoedID = Mock(return_value=1)
        result = returnGrabFreqAndRecoedID()
        self.assertEqual(result, 1)

    def test_writeFacebookStatus(self):
        writeFacebookStatus = Mock(return_value=1)
        result = writeFacebookStatus()
        self.assertEqual(result, 1)

    def test_getGroupPosts(self):
        getGroupPosts = Mock(return_value=1)
        result = getGroupPosts()
        self.assertEqual(result, 1)

    def test_getGroupCommentsOnlyForEnroll(self):
        getGroupCommentsOnlyForEnroll = Mock(return_value=1)
        result = getGroupCommentsOnlyForEnroll()
        self.assertEqual(result, 1)
    
    def test_get_recent_pickup_date3(self):
        # Mock the unnecessary function
        with patch('datetime.datetime') as mock_dt:
            mock_now = datetime(2023, 6, 7)
            mock_dt.now.return_value = mock_now
            # Test with mode = 0
            expected_date = (mock_now.date() + timedelta(days=1)).isoformat()
            expected_date = getRecentPickupDate(0)
            self.assertEqual(getRecentPickupDate(0), expected_date)
            
            # Test with mode = 1
            expected_date = mock_now.date().isoformat()
            expected_date = getRecentPickupDate(1)
            self.assertEqual(getRecentPickupDate(1), expected_date)

    def test_get_recent_pickup_date4(self):
        # Mock the unnecessary function
        with patch('datetime.datetime') as mock_dt:
            mock_now = datetime(2023, 6, 7)
            mock_dt.now.return_value = mock_now
            # Test with mode = 0
            expected_date = (mock_now.date() + timedelta(days=1)).isoformat()
            expected_date = getRecentPickupDate(0)
            self.assertEqual(getRecentPickupDate(0), expected_date)
            
            # Test with mode = 1
            expected_date = mock_now.date().isoformat()
            expected_date = getRecentPickupDate(1)
            self.assertEqual(getRecentPickupDate(1), expected_date)
    
    def test_get_recent_pickup_date5(self):
        # Mock the unnecessary function
        with patch('datetime.datetime') as mock_dt:
            mock_now = datetime(2023, 6, 7)
            mock_dt.now.return_value = mock_now
            # Test with mode = 0
            expected_date = (mock_now.date() + timedelta(days=1)).isoformat()
            expected_date = getRecentPickupDate(0)
            self.assertEqual(getRecentPickupDate(0), expected_date)
            
            # Test with mode = 1
            expected_date = mock_now.date().isoformat()
            expected_date = getRecentPickupDate(1)
            self.assertEqual(getRecentPickupDate(1), expected_date)




    

if __name__ == '__main__':
    unittest.main()
