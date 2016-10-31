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
        order_response = \
        '''
            <OrderResponse>
                <Order>
                    <CustomerOrderId>abc-123</CustomerOrderId>
                    <Name>test order 2</Name>
                    <OrderCreateDate>2016-10-31T16:57:34.708Z</OrderCreateDate>
                    <PeerId>912912</PeerId>
                    <BackOrderRequested>true</BackOrderRequested>
                    <id>f2584-fe-47-82-d69aa</id>
                    <AreaCodeSearchAndOrderType>
                        <AreaCode>617</AreaCode>
                        <Quantity>3</Quantity>
                    </AreaCodeSearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>2993</SiteId>
                </Order>
                <OrderStatus>RECEIVED</OrderStatus>
            </OrderResponse>
        '''

        order_inst = \
        '''
            <OrderResponse>
                <CompletedQuantity>3</CompletedQuantity>
                <CreatedByUser>testUser</CreatedByUser>
                <LastModifiedDate>2016-10-31T16:57:34.810Z</LastModifiedDate>
                <OrderCompleteDate>2016-10-31T16:57:34.810Z</OrderCompleteDate>
                <Order>
                    <CustomerOrderId>abc-123</CustomerOrderId>
                    <Name>test order 2</Name>
                    <OrderCreateDate>2016-10-31T16:57:34.708Z</OrderCreateDate>
                    <PeerId>912912</PeerId>
                    <BackOrderRequested>true</BackOrderRequested>
                    <AreaCodeSearchAndOrderType>
                        <AreaCode>617</AreaCode>
                        <Quantity>3</Quantity>
                    </AreaCodeSearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>2993</SiteId>
                </Order>
                <OrderStatus>COMPLETE</OrderStatus>
                <CompletedNumbers>
                    <TelephoneNumber>
                        <FullNumber>6172218217</FullNumber>
                    </TelephoneNumber>
                    <TelephoneNumber>
                        <FullNumber>6172219906</FullNumber>
                    </TelephoneNumber>
                    <TelephoneNumber>
                        <FullNumber>6172219931</FullNumber>
                    </TelephoneNumber>
                </CompletedNumbers>
                <Summary>3 numbers ordered in (617)</Summary>
                <FailedQuantity>0</FailedQuantity>
            </OrderResponse>
        '''

        with requests_mock.Mocker() as m:
            url = 'http://resource_tests/123456/{0}'.format(Order.orders_path)
            m.post(url, content=order_response)

            order = Order.create_area_code_search_and_order(area_code='719',
                                                            quantity='3',
                                                            name = 'test order 2',
                                                            site_id='2993',
                                                            peer_id = '912912',
                                                            customer_order_id = 'abc-123',
                                                            back_order_requested='true'
                                                            )

            self.assertTrue(isinstance(order, dict))
            self.assertTrue(isinstance(order['OrderResponse'], dict))
            self.assertTrue(isinstance(order['OrderResponse']['Order'], dict))
            self.assertEqual(order['OrderResponse']['Order']['Name'], 'test order 2')
            self.assertEqual(order['OrderResponse']['Order']['PeerId'], '912912')
            self.assertEqual(order['OrderResponse']['Order']['BackOrderRequested'], 'true')
            self.assertEqual(order['OrderResponse']['Order']['SiteId'], '2993')
            self.assertEqual(order['OrderResponse']['Order']['AreaCodeSearchAndOrderType']['Quantity'], '3')

            id = order['OrderResponse']['Order']['id']

            url = '{0}/{1}'.format(url, id)
            m.get(url, content=order_inst)
            completed_order = Order.get(id)


            self.assertTrue(isinstance(completed_order, dict))
            self.assertTrue(completed_order['OrderResponse']['OrderStatus'], 'COMPLETED')
            self.assertEqual(completed_order['OrderResponse']['CompletedQuantity'], '3')
            self.assertEqual(completed_order['OrderResponse']['CreatedByUser'], 'testUser')

            tn_list = completed_order['OrderResponse']['CompletedNumbers']
            self.assertTrue(tn_list[0]['FullNumber'], '6172218217')


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
