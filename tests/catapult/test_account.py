import unittest
import six
import requests
from tests.catapult.helpers import create_response, get_client, AUTH, headers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client


class AccountTests(unittest.TestCase):

    def test_get_account(self):
        """
        get_account() should return account data
        """
        estimated_json = """
        {"balance": "538.37250","accountType":"pre-pay"}
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_account()
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/account',
                auth=AUTH,
                headers=headers)
            self.assertEqual('pre-pay', data['account_type'])

    def test_list_account_transactions(self):
        """
        list_account_transactions() should return account transactions
        """
        estimated_request = {
            'maxItems': None,
            'toDate': None,
            'fromDate': None,
            'type': None,
            'size': None,
            'number': None
        }
        estimated_json = """
            [
                {
                    "id":"transactionId1",
                    "time":"2013-02-21T13:39:09Z",
                    "amount":"0.00750",
                    "type":"charge",
                    "units":"1",
                    "productType":"sms-out",
                    "number":"1234567890"
                }
            ]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.list_account_transactions())
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/account/transactions',
                auth=AUTH,
                params=estimated_request,
                headers=headers)
            self.assertEqual('transactionId1', data[0]['id'])
