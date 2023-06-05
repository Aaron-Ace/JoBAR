import io
import os
import sys
import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

sys.path.append(os.getcwd())
# sys.path.append("../../")

from bot_data.subFunction.odoo_xmlrpc import *

class TestSubFunction3(unittest.TestCase):
    def setUp(self):
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

    @patch('xmlrpc.client.ServerProxy')
    def test_connectOdoo(self, mock_server_proxy):
        # Mock the xmlrpc.client.ServerProxy
        mock_server_proxy.return_value = 'MockServerProxy'

        # Call the function to test
        result = connectOdoo()

        # Assert the expected result
        self.assertEqual(result, 'MockServerProxy')
        mock_server_proxy.assert_called_with('http://example.com/xmlrpc/2/common')

    @patch('xmlrpc.client.ServerProxy')
    def test_endpoint_object(self, mock_server_proxy):
        # Mock the xmlrpc.client.ServerProxy
        mock_server_proxy.return_value = 'MockServerProxy'

        # Call the function to test
        result = endpoint_object()

        # Assert the expected result
        self.assertEqual(result, 'MockServerProxy')
        mock_server_proxy.assert_called_with('http://example.com/xmlrpc/2/object')

    @patch('xmlrpc.client.ServerProxy')
    def test_get_uid(self, mock_connect_odoo):
        # Mock the connectOdoo function
        mock_connect_odoo.return_value.authenticate.return_value = 1234

        # Call the function to test
        result = get_uid()

        # Assert the expected result
        self.assertEqual(result, 1234)
        mock_connect_odoo.return_value.authenticate.assert_called_with('test_db', 'test_user', 'test_password', {})

    @patch('bot_data.subFunction.odoo_xmlrpc.models.execute_kw')
    def test_getUserDataByLine(self, mock_execute_kw):
        # Mock the models.execute_kw function
        mock_execute_kw.side_effect = [
            [{'id': 1, 'active': True, 'login': 'test_user', 'partner_id': [1], 'oauth_provider_id': 1,
              'oauth_uid': '123', 'oauth_access_token': 'token'}],
            [{'id': 1, 'email': 'test@example.com', 'phone': '1234567890', 'pickup_area': 'area',
              'user_discount': 10, 'is_enroll': True}]
        ]

        # Call the function to test
        result_user, result_partner = getUserDataByLine('models', 1234, '123')

        # Assert the expected results
        self.assertEqual(result_user, {'id': 1, 'active': True, 'login': 'test_user', 'partner_id': 1,
                                       'oauth_provider_id': 1, 'oauth_uid': '123', 'oauth_access_token': 'token'})
        self.assertEqual(result_partner, {'id': 1, 'email': 'test@example.com', 'phone': '1234567890',
                                          'pickup_area': 'area', 'user_discount': 10, 'is_enroll': True})
        mock_execute_kw.assert_any_call('test_db', 1234, 'test_password', 'res.users', 'search_read',
                                        [[['oauth_uid', '=', '123']]],
                                        {'fields': ['id', 'active', 'login', 'partner_id', 'oauth_provider_id',
                                                    'oauth_uid', 'oauth_access_token']})
        mock_execute_kw.assert_any_call('test_db', 1234, 'test_password', 'res.partner', 'search_read',
                                        [[['id', '=', 1]]],
                                        {'fields': ['id', 'email', 'phone', 'pickup_area', 'user_discount', 'is_enroll']})

    @patch('bot_data.subFunction.odoo_xmlrpc.models.execute_kw')
    def test_getPartnerPUArea(self, mock_execute_kw):
        # Mock the models.execute_kw function
        mock_execute_kw.return_value = [{'pickup_area': [1]}]

        # Call the function to test
        result = getPartnerPUArea('models', 1234, 1)

        # Assert the expected result
        self.assertEqual(result, 1)
        mock_execute_kw.assert_called_with('test_db', 1234, 'test_password', 'res.partner', 'search_read',
                                           [[['id', '=', 1]]],
                                           {'fields': ['pickup_area']})

    @patch('bot_data.subFunction.odoo_xmlrpc.models.execute_kw')
    def test_getOrderData(self, mock_execute_kw):
        # Mock the models.execute_kw function
        mock_execute_kw.return_value = [{'id': 1, 'partner_id': 1, 'amount_total': 100, 'pickup_date': '2023-06-05',
                                         'pickup_area': 'area', 'name': 'order'}]

        # Call the function to test
        result = getOrderData('models', 1234, 1)

        # Assert the expected result
        self.assertEqual(result, {'id': 1, 'partner_id': 1, 'amount_total': 100, 'pickup_date': '2023-06-05',
                                  'pickup_area': 'area', 'name': 'order'})
        mock_execute_kw.assert_called_with('test_db', 1234, 'test_password', 'sale.order', 'search_read',
                                           [[['id', '=', 1]]],
                                           {'fields': ['id', 'partner_id', 'amount_total', 'pickup_date',
                                                       'pickup_area', 'name']})

if __name__ == '__main__':
    unittest.main()