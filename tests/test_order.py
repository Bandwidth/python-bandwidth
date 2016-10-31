from unittest import TestCase


from unittest import TestCase
import os

import six
import requests
import requests_mock

from bandwidth_sdk.resources import TelephoneNumber, Order
import bandwidth_sdk



class TestOrder(TestCase):

    def setUp(self):
        bandwidth_sdk.account_id='123456'
        bandwidth_sdk.username='foo'
        bandwidth_sdk.password='bar'
        bandwidth_sdk.iris_endpoint = 'http://resource_tests'

    def tearDown(self):
        pass

    def test_get(self):
        self.fail()

    def test_list(self):
        self.fail()

    def test__create(self):
        self.fail()

    def test_create_existing_telephone_number_order(self):
        query_response = \
            '''
            <SearchResult>
                <ResultCount>3</ResultCount>
                <TelephoneNumberList>
                    <TelephoneNumber>7192041437</TelephoneNumber>
                    <TelephoneNumber>7192041455</TelephoneNumber>
                    <TelephoneNumber>7192041495</TelephoneNumber>
                </TelephoneNumberList>
            </SearchResult>
            '''

        order_response = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <OrderResponse>
            <Order>
                <CustomerOrderId>xyz-123</CustomerOrderId>
                <Name>Test Order 1</Name>
                <OrderCreateDate>2016-10-28T21:36:07.346Z</OrderCreateDate>
                <PeerId>912912</PeerId>
                <BackOrderRequested>false</BackOrderRequested>
                <id>b64b-7a-69-8b62-274d9b0</id>
                <ExistingTelephoneNumberOrderType>
                    <TelephoneNumberList>
                        <TelephoneNumber>7192041437</TelephoneNumber>
                        <TelephoneNumber>7192041455</TelephoneNumber>
                        <TelephoneNumber>7192041495</TelephoneNumber>
                    </TelephoneNumberList>
                </ExistingTelephoneNumberOrderType>
                <PartialAllowed>true</PartialAllowed>
                <SiteId>2993</SiteId>
            </Order>
            <OrderStatus>RECEIVED</OrderStatus>
        </OrderResponse>
        '''

        with requests_mock.Mocker() as m:
            url = 'http://resource_tests/123456/{0}'.format(TelephoneNumber.available_numbers_path)
            m.get(url, content=query_response)
            available_numbers = TelephoneNumber.list_available_numbers(area_code='719', quantity='10')


            url = 'http://resource_tests/123456/{0}'.format(Order.orders_path)
            m.post(url, content=order_response)
            order = Order.create_existing_telephone_number_order(telephone_number_list=available_numbers,
                                                                 name='Test Order 1',
                                                                 site_id='2993',
                                                                 peer_id='912912',
                                                                 customer_order_id='xyz-123'
                                                                 )

            self.assertTrue(isinstance(order, dict))
            self.assertTrue(isinstance(order['OrderResponse'], dict))
            self.assertTrue(isinstance(order['OrderResponse']['Order'], dict))
            self.assertEqual(order['OrderResponse']['Order']['CustomerOrderId'], 'xyz-123')
            self.assertEqual(order['OrderResponse']['Order']['Name'], 'Test Order 1' )
            self.assertEqual(order['OrderResponse']['Order']['OrderCreateDate'], '2016-10-28T21:36:07.346Z')
            self.assertEqual(order['OrderResponse']['Order']['PeerId'], '912912')
            self.assertEqual(order['OrderResponse']['Order']['BackOrderRequested'], 'false')
            self.assertEqual(order['OrderResponse']['Order']['id'], 'b64b-7a-69-8b62-274d9b0')
            self.assertEqual(order['OrderResponse']['Order']['PartialAllowed'], 'true')
            self.assertEqual(order['OrderResponse']['Order']['SiteId'], '2993')
            self.assertTrue(isinstance(order['OrderResponse']['Order']['ExistingTelephoneNumberOrderType']['TelephoneNumberList'], list))

            # TODO the next line should return a list, not a dict
            tn = order['OrderResponse']['Order']['ExistingTelephoneNumberOrderType']['TelephoneNumberList'][0]
            self.assertEqual(tn, '7192041437')


    def test_create_area_code_search_and_order(self):
        self.fail()

    def test_create_rate_center_search_and_order(self):
        self.fail()

    def test_create_npsnxx_search_And_order(self):
        self.fail()

    def test_create_toll_free_vanity_search_and_order(self):
        self.fail()

    def test_create_toll_free_wild_char_search_and_order(self):
        self.fail()

    def test_create_state_search_and_order(self):
        self.fail()

    def test_create_city_search_and_order(self):
        self.fail()

    def test_create_zip_search_and_order(self):
        self.fail()

    def test_create_lata_search_and_order(self):
        self.fail()

    def test_create_combined_search_and_order(self):
        self.fail()

    def test_to_xml(self):
        self.fail()
