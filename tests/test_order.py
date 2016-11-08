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
        order_inst = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <OrderResponse>
                <CreatedByUser>testUser</CreatedByUser>
                <ErrorList>
                    <Error>
                        <Code>5019</Code>
                        <Description>Order is pending. Please check the status of your order later. </Description>
                    </Error>
                </ErrorList>
                <Order>
                    <CustomerOrderId>test Order 18</CustomerOrderId>
                    <Name>Existing Number Order</Name>
                    <OrderCreateDate>2016-10-31T21:59:57.853Z</OrderCreateDate>
                    <PeerId>1819</PeerId>
                    <BackOrderRequested>false</BackOrderRequested>
                    <id>020-a2-4a-9b-1234bc</id>
                    <LATASearchAndOrderType>
                        <Quantity>3</Quantity>
                    </LATASearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>1918</SiteId>
                </Order>
                <OrderStatus>RECEIVED</OrderStatus>
            </OrderResponse>
        '''
        with requests_mock.Mocker() as m:
            url = 'http://resource_tests/123456/{0}'.format(Order.orders_path)

            id = '020-a2-4a-9b-1234bc'

            url = '{0}/{1}'.format(url, id)
            m.get(url, content=order_inst)
            completed_order = Order.get(id)

            self.assertTrue(isinstance(completed_order, dict))
            self.assertEqual(completed_order['OrderResponse']['OrderStatus'], 'RECEIVED')

            for error in completed_order['OrderResponse']['ErrorList']:
                error['Code']
                error['Description']


    def test_create_existing_telephone_number_order(self):
        query_response = \
            '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
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
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
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
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
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
            self.assertEqual(order['OrderResponse']['Order']['AreaCodeSearchAndOrderType']['AreaCode'], '617')

            id = order['OrderResponse']['Order']['id']

            url = '{0}/{1}'.format(url, id)
            m.get(url, content=order_inst)
            completed_order = Order.get(id)


            self.assertTrue(isinstance(completed_order, dict))
            self.assertEqual(completed_order['OrderResponse']['OrderStatus'], 'COMPLETE')
            self.assertEqual(completed_order['OrderResponse']['CompletedQuantity'], '3')
            self.assertEqual(completed_order['OrderResponse']['CreatedByUser'], 'testUser')
            self.assertEqual(completed_order['OrderResponse']['FailedQuantity'], '0')

            tn_list = completed_order['OrderResponse']['CompletedNumbers']
            self.assertEqual(tn_list[0]['FullNumber'], '6172218217')


    def test_create_rate_center_search_and_order(self):
        order_response = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <OrderResponse>
            <Order>
                <CustomerOrderId>efg-456</CustomerOrderId>
                <Name>test order 3</Name>
                <OrderCreateDate>2016-10-31T20:37:27.563Z</OrderCreateDate>
                <PeerId>912912</PeerId>
                <BackOrderRequested>true</BackOrderRequested>
                <id>d416-11-7d-d9-173d</id>
                <RateCenterSearchAndOrderType>
                    <EnableLCA>true</EnableLCA>
                    <Quantity>3</Quantity>
                    <RateCenter>DENVER</RateCenter>
                    <State>CO</State>
                </RateCenterSearchAndOrderType>
                <PartialAllowed>true</PartialAllowed>
                <SiteId>2993</SiteId>
            </Order>
            <OrderStatus>RECEIVED</OrderStatus>
        </OrderResponse>
        '''

        order_inst = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <OrderResponse>
            <CompletedQuantity>3</CompletedQuantity>
            <CreatedByUser>testUser</CreatedByUser>
            <LastModifiedDate>2016-10-31T20:37:28.081Z</LastModifiedDate>
            <OrderCompleteDate>2016-10-31T20:37:28.081Z</OrderCompleteDate>
            <Order>
                <CustomerOrderId>efg-456</CustomerOrderId>
                <Name>test order 3</Name>
                <OrderCreateDate>2016-10-31T20:37:27.563Z</OrderCreateDate>
                <PeerId>912912</PeerId>
                <BackOrderRequested>true</BackOrderRequested>
                <RateCenterSearchAndOrderType>
                    <EnableLCA>true</EnableLCA>
                    <Quantity>3</Quantity>
                    <RateCenter>DENVER</RateCenter>
                    <State>CO</State>
                </RateCenterSearchAndOrderType>
                <PartialAllowed>true</PartialAllowed>
                <SiteId>2993</SiteId>
            </Order>
            <OrderStatus>COMPLETE</OrderStatus>
            <CompletedNumbers>
                <TelephoneNumber>
                    <FullNumber>7203707877</FullNumber>
                </TelephoneNumber>
                <TelephoneNumber>
                    <FullNumber>7203708409</FullNumber>
                </TelephoneNumber>
                <TelephoneNumber>
                    <FullNumber>7203708478</FullNumber>
                </TelephoneNumber>
            </CompletedNumbers>
            <Summary>3 numbers ordered in (720)</Summary>
            <FailedQuantity>0</FailedQuantity>
        </OrderResponse>
        '''
        with requests_mock.Mocker() as m:
            url = 'http://resource_tests/123456/{0}'.format(Order.orders_path)
            m.post(url, content=order_response)

            order = Order.create_rate_center_search_and_order(rate_center='DENVER',
                                                              quantity='3',
                                                              state='CO',
                                                              name='test order 3',
                                                              site_id='2993',
                                                              peer_id='912912',
                                                              customer_order_id='efg-456',
                                                              back_order_requested='true'
                                                              )
            self.assertTrue(isinstance(order, dict))
            self.assertTrue(isinstance(order['OrderResponse'], dict))
            self.assertTrue(isinstance(order['OrderResponse']['Order'], dict))
            self.assertEqual(order['OrderResponse']['Order']['Name'], 'test order 3')
            self.assertEqual(order['OrderResponse']['Order']['PeerId'], '912912')
            self.assertEqual(order['OrderResponse']['Order']['BackOrderRequested'], 'true')
            self.assertEqual(order['OrderResponse']['Order']['SiteId'], '2993')
            self.assertEqual(order['OrderResponse']['Order']['RateCenterSearchAndOrderType']['Quantity'], '3')
            self.assertEqual(order['OrderResponse']['Order']['RateCenterSearchAndOrderType']['RateCenter'], 'DENVER')
            self.assertEqual(order['OrderResponse']['Order']['RateCenterSearchAndOrderType']['State'], 'CO')

            id = order['OrderResponse']['Order']['id']

            url = '{0}/{1}'.format(url, id)
            m.get(url, content=order_inst)
            completed_order = Order.get(id)

            self.assertTrue(isinstance(completed_order, dict))
            self.assertEqual(completed_order['OrderResponse']['OrderStatus'], 'COMPLETE')
            self.assertEqual(completed_order['OrderResponse']['CompletedQuantity'], '3')
            self.assertEqual(completed_order['OrderResponse']['CreatedByUser'], 'testUser')
            self.assertEqual(completed_order['OrderResponse']['FailedQuantity'], '0')

            tn_list = completed_order['OrderResponse']['CompletedNumbers']
            self.assertEqual(tn_list[0]['FullNumber'], '7203707877')
            self.assertEqual(tn_list[len(tn_list)-1]['FullNumber'], '7203708478')


    def test_create_npsnxx_search_And_order(self):
        order_response = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <OrderResponse>
            <Order>
                <CustomerOrderId>hij-789</CustomerOrderId>
                <Name>test order 4</Name>
                <OrderCreateDate>2016-10-31T20:58:11.676Z</OrderCreateDate>
                <PeerId>912912</PeerId>
                <BackOrderRequested>false</BackOrderRequested>
                <id>3141-05-4f-b8-2094</id>
                <NPANXXSearchAndOrderType>
                    <EnableLCA>false</EnableLCA>
                    <NpaNxx>919439</NpaNxx>
                    <Quantity>3</Quantity>
                </NPANXXSearchAndOrderType>
                <PartialAllowed>true</PartialAllowed>
                <SiteId>2993</SiteId>
            </Order>
            <OrderStatus>RECEIVED</OrderStatus>
        </OrderResponse>
        '''

        order_inst = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <OrderResponse>
                <CompletedQuantity>3</CompletedQuantity>
                <CreatedByUser>testUser</CreatedByUser>
                <LastModifiedDate>2016-10-31T20:58:11.751Z</LastModifiedDate>
                <OrderCompleteDate>2016-10-31T20:58:11.751Z</OrderCompleteDate>
                <Order>
                    <CustomerOrderId>123456789</CustomerOrderId>
                    <Name>Existing Number Order</Name>
                    <OrderCreateDate>2016-10-31T20:58:11.676Z</OrderCreateDate>
                    <PeerId>519858</PeerId>
                    <BackOrderRequested>false</BackOrderRequested>
                    <NPANXXSearchAndOrderType>
                        <EnableLCA>false</EnableLCA>
                        <NpaNxx>919439</NpaNxx>
                        <Quantity>3</Quantity>
                    </NPANXXSearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>6992</SiteId>
                </Order>
                <OrderStatus>COMPLETE</OrderStatus>
                <CompletedNumbers>
                    <TelephoneNumber>
                        <FullNumber>9194390189</FullNumber>
                    </TelephoneNumber>
                    <TelephoneNumber>
                        <FullNumber>9194394284</FullNumber>
                    </TelephoneNumber>
                    <TelephoneNumber>
                        <FullNumber>9194396493</FullNumber>
                    </TelephoneNumber>
                </CompletedNumbers>
                <Summary>3 numbers ordered in (919)</Summary>
                <FailedQuantity>0</FailedQuantity>
            </OrderResponse>
        '''
        with requests_mock.Mocker() as m:
            url = 'http://resource_tests/123456/{0}'.format(Order.orders_path)
            m.post(url, content=order_response)

            order = Order.create_npsnxx_search_And_order(npanxx = '919439',
                                                         quantity = '3',
                                                         enable_lca='false',
                                                         enable_tn_details='false',
                                                         name='test order 4',
                                                         site_id='2993',
                                                         peer_id='912912',
                                                         customer_order_id='hij-789',
                                                         back_order_requested='false'
                                                         )

            self.assertTrue(isinstance(order, dict))
            self.assertTrue(isinstance(order['OrderResponse'], dict))
            self.assertTrue(isinstance(order['OrderResponse']['Order'], dict))
            self.assertEqual(order['OrderResponse']['Order']['Name'], 'test order 4')
            self.assertEqual(order['OrderResponse']['Order']['PeerId'], '912912')
            self.assertEqual(order['OrderResponse']['Order']['BackOrderRequested'], 'false')
            self.assertEqual(order['OrderResponse']['Order']['SiteId'], '2993')
            self.assertEqual(order['OrderResponse']['Order']['NPANXXSearchAndOrderType']['Quantity'], '3')
            self.assertEqual(order['OrderResponse']['Order']['NPANXXSearchAndOrderType']['NpaNxx'], '919439')
            self.assertEqual(order['OrderResponse']['Order']['NPANXXSearchAndOrderType']['EnableLCA'], 'false')

            id = order['OrderResponse']['Order']['id']

            url = '{0}/{1}'.format(url, id)
            m.get(url, content=order_inst)
            completed_order = Order.get(id)

            self.assertTrue(isinstance(completed_order, dict))
            self.assertEqual(completed_order['OrderResponse']['OrderStatus'], 'COMPLETE')
            self.assertEqual(completed_order['OrderResponse']['CompletedQuantity'], '3')
            self.assertEqual(completed_order['OrderResponse']['CreatedByUser'], 'testUser')
            self.assertEqual(completed_order['OrderResponse']['FailedQuantity'], '0')

            tn_list = completed_order['OrderResponse']['CompletedNumbers']
            self.assertEqual(tn_list[0]['FullNumber'], '9194390189')
            self.assertEqual(tn_list[len(tn_list) - 1]['FullNumber'], '9194396493')


    def test_create_state_search_and_order(self):
        order_response = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <OrderResponse>
                <Order>
                    <CustomerOrderId>klm-1011</CustomerOrderId>
                    <Name>test order 5</Name>
                    <OrderCreateDate>2016-10-31T21:17:28.603Z</OrderCreateDate>
                    <PeerId>912912</PeerId>
                    <BackOrderRequested>false</BackOrderRequested>
                    <id>0061-1e-49-ad-ba617</id>
                    <StateSearchAndOrderType>
                        <Quantity>3</Quantity>
                        <State>CO</State>
                    </StateSearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>2993</SiteId>
                </Order>
                <OrderStatus>RECEIVED</OrderStatus>
            </OrderResponse>
        '''

        order_inst = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <OrderResponse>
                <CompletedQuantity>3</CompletedQuantity>
                <CreatedByUser>testUser</CreatedByUser>
                <LastModifiedDate>2016-10-31T21:17:29.103Z</LastModifiedDate>
                <OrderCompleteDate>2016-10-31T21:17:29.102Z</OrderCompleteDate>
                <Order>
                    <CustomerOrderId>klm-1011</CustomerOrderId>
                    <Name>test order 5</Name>
                    <OrderCreateDate>2016-10-31T21:17:28.603Z</OrderCreateDate>
                    <PeerId>912912</PeerId>
                    <BackOrderRequested>false</BackOrderRequested>
                    <StateSearchAndOrderType>
                        <Quantity>3</Quantity>
                        <State>CO</State>
                    </StateSearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>2993</SiteId>
                </Order>
                <OrderStatus>COMPLETE</OrderStatus>
                <CompletedNumbers>
                    <TelephoneNumber>
                        <FullNumber>7193990461</FullNumber>
                    </TelephoneNumber>
                    <TelephoneNumber>
                        <FullNumber>7193990484</FullNumber>
                    </TelephoneNumber>
                    <TelephoneNumber>
                        <FullNumber>7193990505</FullNumber>
                    </TelephoneNumber>
                </CompletedNumbers>
                <Summary>3 numbers ordered in (719)</Summary>
                <FailedQuantity>0</FailedQuantity>
            </OrderResponse>
        '''
        with requests_mock.Mocker() as m:
            url = 'http://resource_tests/123456/{0}'.format(Order.orders_path)
            m.post(url, content=order_response)

            order = Order.create_state_search_and_order(state='CO',
                                                        quantity='3',
                                                        name='test order 5',
                                                        site_id='2993',
                                                        peer_id='912912',
                                                        customer_order_id='klm-1011',
                                                        back_order_requested='false'
                                                        )

            self.assertTrue(isinstance(order, dict))
            self.assertTrue(isinstance(order['OrderResponse'], dict))
            self.assertTrue(isinstance(order['OrderResponse']['Order'], dict))
            self.assertEqual(order['OrderResponse']['Order']['Name'], 'test order 5')
            self.assertEqual(order['OrderResponse']['Order']['PeerId'], '912912')
            self.assertEqual(order['OrderResponse']['Order']['BackOrderRequested'], 'false')
            self.assertEqual(order['OrderResponse']['Order']['SiteId'], '2993')
            self.assertEqual(order['OrderResponse']['Order']['StateSearchAndOrderType']['Quantity'], '3')
            self.assertEqual(order['OrderResponse']['Order']['StateSearchAndOrderType']['State'], 'CO')

            id = order['OrderResponse']['Order']['id']

            url = '{0}/{1}'.format(url, id)
            m.get(url, content=order_inst)
            completed_order = Order.get(id)

            self.assertTrue(isinstance(completed_order, dict))
            self.assertEqual(completed_order['OrderResponse']['OrderStatus'], 'COMPLETE')
            self.assertEqual(completed_order['OrderResponse']['CompletedQuantity'], '3')
            self.assertEqual(completed_order['OrderResponse']['CreatedByUser'], 'testUser')
            self.assertEqual(completed_order['OrderResponse']['FailedQuantity'], '0')

            tn_list = completed_order['OrderResponse']['CompletedNumbers']
            self.assertEqual(tn_list[0]['FullNumber'], '7193990461')
            self.assertEqual(tn_list[len(tn_list) - 1]['FullNumber'], '7193990505')


    def test_create_city_search_and_order(self):
        order_response = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <OrderResponse>
                <Order>
                    <CustomerOrderId>nmo-1213</CustomerOrderId>
                    <Name>test order 6</Name>
                    <OrderCreateDate>2016-10-31T21:25:23.598Z</OrderCreateDate>
                    <PeerId>912912</PeerId>
                    <BackOrderRequested>false</BackOrderRequested>
                    <id>34cc-6b-46-94-fc34</id>
                    <CitySearchAndOrderType>
                        <City>DENVER</City>
                        <Quantity>3</Quantity>
                        <State>CO</State>
                    </CitySearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>2993</SiteId>
                </Order>
                <OrderStatus>RECEIVED</OrderStatus>
            </OrderResponse>
        '''

        order_inst = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <OrderResponse>
                <CompletedQuantity>3</CompletedQuantity>
                <CreatedByUser>testUser</CreatedByUser>
                <LastModifiedDate>2016-10-31T21:28:30.014Z</LastModifiedDate>
                <OrderCompleteDate>2016-10-31T21:28:30.014Z</OrderCompleteDate>
                <Order>
                    <CustomerOrderId>nmo-1213</CustomerOrderId>
                    <Name>test order 6</Name>
                    <OrderCreateDate>2016-10-31T21:28:27.746Z</OrderCreateDate>
                    <PeerId>912912</PeerId>
                    <BackOrderRequested>false</BackOrderRequested>
                    <CitySearchAndOrderType>
                        <City>DENVER</City>
                        <Quantity>3</Quantity>
                        <State>CO</State>
                    </CitySearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>2993</SiteId>
                </Order>
                <OrderStatus>COMPLETE</OrderStatus>
                <CompletedNumbers>
                    <TelephoneNumber>
                        <FullNumber>7203708644</FullNumber>
                    </TelephoneNumber>
                    <TelephoneNumber>
                        <FullNumber>7203708773</FullNumber>
                    </TelephoneNumber>
                    <TelephoneNumber>
                        <FullNumber>7203720271</FullNumber>
                    </TelephoneNumber>
                </CompletedNumbers>
                <Summary>3 numbers ordered in (720)</Summary>
                <FailedQuantity>0</FailedQuantity>
            </OrderResponse>
        '''
        with requests_mock.Mocker() as m:
            url = 'http://resource_tests/123456/{0}'.format(Order.orders_path)
            m.post(url, content=order_response)

            order = Order.create_city_search_and_order(city='DENVER',
                                                       state='CO',
                                                       quantity='3',
                                                       name='test order 6',
                                                       site_id='2993',
                                                       peer_id='912912',
                                                       customer_order_id='nmo-1213',
                                                       back_order_requested='false'
                                                       )

            self.assertTrue(isinstance(order, dict))
            self.assertTrue(isinstance(order['OrderResponse'], dict))
            self.assertTrue(isinstance(order['OrderResponse']['Order'], dict))
            self.assertEqual(order['OrderResponse']['Order']['Name'], 'test order 6')
            self.assertEqual(order['OrderResponse']['Order']['PeerId'], '912912')
            self.assertEqual(order['OrderResponse']['Order']['BackOrderRequested'], 'false')
            self.assertEqual(order['OrderResponse']['Order']['SiteId'], '2993')
            self.assertEqual(order['OrderResponse']['Order']['CitySearchAndOrderType']['Quantity'], '3')
            self.assertEqual(order['OrderResponse']['Order']['CitySearchAndOrderType']['City'], 'DENVER')
            self.assertEqual(order['OrderResponse']['Order']['CitySearchAndOrderType']['State'], 'CO')

            id = order['OrderResponse']['Order']['id']

            url = '{0}/{1}'.format(url, id)
            m.get(url, content=order_inst)
            completed_order = Order.get(id)

            self.assertTrue(isinstance(completed_order, dict))
            self.assertEqual(completed_order['OrderResponse']['OrderStatus'], 'COMPLETE')
            self.assertEqual(completed_order['OrderResponse']['CompletedQuantity'], '3')
            self.assertEqual(completed_order['OrderResponse']['CreatedByUser'], 'testUser')
            self.assertEqual(completed_order['OrderResponse']['FailedQuantity'], '0')

            tn_list = completed_order['OrderResponse']['CompletedNumbers']
            self.assertEqual(tn_list[0]['FullNumber'], '7203708644')
            self.assertEqual(tn_list[len(tn_list) - 1]['FullNumber'], '7203720271')


    def test_create_zip_search_and_order(self):
        order_response = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <OrderResponse>
                <Order>
                    <CustomerOrderId>qrs-1415</CustomerOrderId>
                    <Name>test order 7</Name>
                    <OrderCreateDate>2016-10-31T21:45:59.068Z</OrderCreateDate>
                    <PeerId>912912</PeerId>
                    <BackOrderRequested>false</BackOrderRequested>
                    <id>5bb8bfca-d6df-440f-849f-5fd70993ffbb</id>
                    <ZIPSearchAndOrderType>
                        <Quantity>3</Quantity>
                        <Zip>80202</Zip>
                    </ZIPSearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>2993</SiteId>
                </Order>
                <OrderStatus>RECEIVED</OrderStatus>
            </OrderResponse>
        '''

        order_inst = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <OrderResponse>
                <CompletedQuantity>3</CompletedQuantity>
                <CreatedByUser>testUser</CreatedByUser>
                <LastModifiedDate>2016-10-31T21:46:00.224Z</LastModifiedDate>
                <OrderCompleteDate>2016-10-31T21:46:00.224Z</OrderCompleteDate>
                <Order>
                    <CustomerOrderId>qrs-1415</CustomerOrderId>
                    <Name>test order 7</Name>
                    <OrderCreateDate>2016-10-31T21:45:59.068Z</OrderCreateDate>
                    <PeerId>912912</PeerId>
                    <BackOrderRequested>false</BackOrderRequested>
                    <ZIPSearchAndOrderType>
                        <Quantity>3</Quantity>
                        <Zip>80202</Zip>
                    </ZIPSearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>2993</SiteId>
                </Order>
                <OrderStatus>COMPLETE</OrderStatus>
                <CompletedNumbers>
                    <TelephoneNumber>
                        <FullNumber>7203720319</FullNumber>
                    </TelephoneNumber>
                    <TelephoneNumber>
                        <FullNumber>7203721280</FullNumber>
                    </TelephoneNumber>
                    <TelephoneNumber>
                        <FullNumber>7203721282</FullNumber>
                    </TelephoneNumber>
                </CompletedNumbers>
                <Summary>3 numbers ordered in (720)</Summary>
                <FailedQuantity>0</FailedQuantity>
            </OrderResponse>
        '''
        with requests_mock.Mocker() as m:
            url = 'http://resource_tests/123456/{0}'.format(Order.orders_path)
            m.post(url, content=order_response)

            order = Order.create_zip_search_and_order(zip='80202',
                                                      quantity='3',
                                                      name='test order 7',
                                                      site_id='2993',
                                                      peer_id='912912',
                                                      customer_order_id='qrs-1415',
                                                      back_order_requested='false'
                                                      )

            self.assertTrue(isinstance(order, dict))
            self.assertTrue(isinstance(order['OrderResponse'], dict))
            self.assertTrue(isinstance(order['OrderResponse']['Order'], dict))
            self.assertEqual(order['OrderResponse']['Order']['Name'], 'test order 7')
            self.assertEqual(order['OrderResponse']['Order']['PeerId'], '912912')
            self.assertEqual(order['OrderResponse']['Order']['BackOrderRequested'], 'false')
            self.assertEqual(order['OrderResponse']['Order']['SiteId'], '2993')
            self.assertEqual(order['OrderResponse']['Order']['ZIPSearchAndOrderType']['Quantity'], '3')
            self.assertEqual(order['OrderResponse']['Order']['ZIPSearchAndOrderType']['Zip'], '80202')

            id = order['OrderResponse']['Order']['id']

            url = '{0}/{1}'.format(url, id)
            m.get(url, content=order_inst)
            completed_order = Order.get(id)

            self.assertTrue(isinstance(completed_order, dict))
            self.assertEqual(completed_order['OrderResponse']['OrderStatus'], 'COMPLETE')
            self.assertEqual(completed_order['OrderResponse']['CompletedQuantity'], '3')
            self.assertEqual(completed_order['OrderResponse']['CreatedByUser'], 'testUser')
            self.assertEqual(completed_order['OrderResponse']['FailedQuantity'], '0')

            tn_list = completed_order['OrderResponse']['CompletedNumbers']
            self.assertEqual(tn_list[0]['FullNumber'], '7203720319')
            self.assertEqual(tn_list[len(tn_list) - 1]['FullNumber'], '7203721282')


    def test_create_lata_search_and_order(self):
        order_response = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <OrderResponse>
                <Order>
                    <CustomerOrderId>tuv-1617</CustomerOrderId>
                    <Name>test order 8</Name>
                    <OrderCreateDate>2016-10-31T21:59:57.853Z</OrderCreateDate>
                    <PeerId>912912</PeerId>
                    <BackOrderRequested>false</BackOrderRequested>
                    <id>0220-a2-5a-ab-5c0c3</id>
                    <LATASearchAndOrderType>
                        <Quantity>3</Quantity>
                    </LATASearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>2993</SiteId>
                </Order>
                <OrderStatus>RECEIVED</OrderStatus>
            </OrderResponse>
        '''

        # TODO Get the real one; this is a from the zip order
        order_inst = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <OrderResponse>
                <CompletedQuantity>3</CompletedQuantity>
                <CreatedByUser>testUser</CreatedByUser>
                <LastModifiedDate>2016-10-31T21:46:00.224Z</LastModifiedDate>
                <OrderCompleteDate>2016-10-31T21:46:00.224Z</OrderCompleteDate>
                <Order>
                    <CustomerOrderId>qrs-1415</CustomerOrderId>
                    <Name>test order 7</Name>
                    <OrderCreateDate>2016-10-31T21:45:59.068Z</OrderCreateDate>
                    <PeerId>912912</PeerId>
                    <BackOrderRequested>false</BackOrderRequested>
                    <ZIPSearchAndOrderType>
                        <Quantity>3</Quantity>
                        <Zip>80202</Zip>
                    </ZIPSearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>2993</SiteId>
                </Order>
                <OrderStatus>COMPLETE</OrderStatus>
                <CompletedNumbers>
                    <TelephoneNumber>
                        <FullNumber>7203720319</FullNumber>
                    </TelephoneNumber>
                    <TelephoneNumber>
                        <FullNumber>7203721280</FullNumber>
                    </TelephoneNumber>
                    <TelephoneNumber>
                        <FullNumber>7203721282</FullNumber>
                    </TelephoneNumber>
                </CompletedNumbers>
                <Summary>3 numbers ordered in (720)</Summary>
                <FailedQuantity>0</FailedQuantity>
            </OrderResponse>

        '''
        with requests_mock.Mocker() as m:
            url = 'http://resource_tests/123456/{0}'.format(Order.orders_path)
            m.post(url, content=order_response)

            order = Order.create_lata_search_and_order(lata='224',
                                                       quantity='3',
                                                       name='test order 8',
                                                       site_id='2993',
                                                       peer_id='912912',
                                                       customer_order_id='tuv-1617',
                                                       back_order_requested='true'
                                                       )

            self.assertTrue(isinstance(order, dict))
            self.assertTrue(isinstance(order['OrderResponse'], dict))
            self.assertTrue(isinstance(order['OrderResponse']['Order'], dict))
            self.assertEqual(order['OrderResponse']['Order']['Name'], 'test order 8')
            self.assertEqual(order['OrderResponse']['Order']['PeerId'], '912912')
            self.assertEqual(order['OrderResponse']['Order']['BackOrderRequested'], 'false')
            self.assertEqual(order['OrderResponse']['Order']['SiteId'], '2993')
            self.assertEqual(order['OrderResponse']['Order']['LATASearchAndOrderType']['Quantity'], '3')


            id = order['OrderResponse']['Order']['id']

            url = '{0}/{1}'.format(url, id)
            m.get(url, content=order_inst)
            completed_order = Order.get(id)

            self.assertTrue(isinstance(completed_order, dict))
            self.assertEqual(completed_order['OrderResponse']['OrderStatus'], 'COMPLETE')
            self.assertEqual(completed_order['OrderResponse']['CompletedQuantity'], '3')
            self.assertEqual(completed_order['OrderResponse']['CreatedByUser'], 'testUser')
            self.assertEqual(completed_order['OrderResponse']['FailedQuantity'], '0')

            tn_list = completed_order['OrderResponse']['CompletedNumbers']
            self.assertEqual(tn_list[0]['FullNumber'], '7203720319')
            self.assertEqual(tn_list[len(tn_list) - 1]['FullNumber'], '7203721282')


    def test_create_toll_free_vanity_search_and_order(self):
        order_response = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <OrderResponse>
                <Order>
                    <CustomerOrderId>wxy-1819</CustomerOrderId>
                    <Name>test order 9</Name>
                    <OrderCreateDate>2016-11-01T19:38:09.990Z</OrderCreateDate>
                    <PeerId>912912</PeerId>
                    <BackOrderRequested>false</BackOrderRequested>
                    <id>a8ed-3a-45-8f-4a8fa1</id>
                    <TollFreeVanitySearchAndOrderType>
                        <Quantity>1</Quantity>
                        <TollFreeVanity>surf</TollFreeVanity>
                    </TollFreeVanitySearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>2993</SiteId>
                </Order>
                <OrderStatus>RECEIVED</OrderStatus>
            </OrderResponse>
        '''

        order_inst = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <OrderResponse>
                <CompletedQuantity>1</CompletedQuantity>
                <CreatedByUser>testUser</CreatedByUser>
                <LastModifiedDate>2016-11-01T19:38:15.255Z</LastModifiedDate>
                <OrderCompleteDate>2016-11-01T19:38:15.255Z</OrderCompleteDate>
                <Order>
                    <CustomerOrderId>wxy-1819</CustomerOrderId>
                    <Name>test order 9</Name>
                    <OrderCreateDate>2016-11-01T19:38:09.990Z</OrderCreateDate>
                    <PeerId>912912</PeerId>
                    <BackOrderRequested>false</BackOrderRequested>
                    <TollFreeVanitySearchAndOrderType>
                        <Quantity>1</Quantity>
                        <TollFreeVanity>surf</TollFreeVanity>
                    </TollFreeVanitySearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>2993</SiteId>
                </Order>
                <OrderStatus>COMPLETE</OrderStatus>
                <CompletedNumbers>
                    <TelephoneNumber>
                        <FullNumber>8552178735</FullNumber>
                    </TelephoneNumber>
                </CompletedNumbers>
                <Summary>1 number ordered in (855)</Summary>
                <FailedQuantity>0</FailedQuantity>
            </OrderResponse>
        '''
        with requests_mock.Mocker() as m:
            url = 'http://resource_tests/123456/{0}'.format(Order.orders_path)
            m.post(url, content=order_response)

            order = Order.create_toll_free_vanity_search_and_order(toll_free_vanity='surf',
                                                                   quantity='1',
                                                                   name='test order 9',
                                                                   site_id='2993',
                                                                   peer_id='912912',
                                                                   customer_order_id='wxy-1819',
                                                                   back_order_requested='false')

            self.assertTrue(isinstance(order, dict))
            self.assertTrue(isinstance(order['OrderResponse'], dict))
            self.assertTrue(isinstance(order['OrderResponse']['Order'], dict))
            self.assertEqual(order['OrderResponse']['Order']['Name'], 'test order 9')
            self.assertEqual(order['OrderResponse']['Order']['PeerId'], '912912')
            self.assertEqual(order['OrderResponse']['Order']['BackOrderRequested'], 'false')
            self.assertEqual(order['OrderResponse']['Order']['SiteId'], '2993')
            self.assertEqual(order['OrderResponse']['Order']['TollFreeVanitySearchAndOrderType']['Quantity'], '1')
            self.assertEqual(order['OrderResponse']['Order']['TollFreeVanitySearchAndOrderType']['TollFreeVanity'], 'surf')
            self.assertEqual(order['OrderResponse']['OrderStatus'], 'RECEIVED')

            id = order['OrderResponse']['Order']['id']

            url = '{0}/{1}'.format(url, id)
            m.get(url, content=order_inst)
            completed_order = Order.get(id)

            self.assertTrue(isinstance(completed_order, dict))
            self.assertEqual(completed_order['OrderResponse']['OrderStatus'], 'COMPLETE')
            self.assertEqual(completed_order['OrderResponse']['CompletedQuantity'], '1')
            self.assertEqual(completed_order['OrderResponse']['CreatedByUser'], 'testUser')
            self.assertEqual(completed_order['OrderResponse']['FailedQuantity'], '0')

            tn_list = completed_order['OrderResponse']['CompletedNumbers']
            self.assertEqual(tn_list[0]['FullNumber'], '8552178735')



    def test_create_toll_free_wild_char_search_and_order(self):
        order_response = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <OrderResponse>
                <Order>
                    <CustomerOrderId>abc-2021</CustomerOrderId>
                    <Name>test order 10</Name>
                    <OrderCreateDate>2016-11-08T14:59:09.346Z</OrderCreateDate>
                    <PeerId>912912</PeerId>
                    <BackOrderRequested>true</BackOrderRequested>
                    <id>3c5a76db-2773-4a52-8e9d-bc06524842dd</id>
                    <TollFreeWildCharSearchAndOrderType>
                        <Quantity>1</Quantity>
                        <TollFreeWildCardPattern>8**</TollFreeWildCardPattern>
                    </TollFreeWildCharSearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>2993</SiteId>
                </Order>
                <OrderStatus>RECEIVED</OrderStatus>
            </OrderResponse>
        '''

        order_inst = \
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <OrderResponse>
                <CompletedQuantity>1</CompletedQuantity>
                <CreatedByUser>testUser</CreatedByUser>
                <LastModifiedDate>2016-11-08T14:59:14.089Z</LastModifiedDate>
                <OrderCompleteDate>2016-11-08T14:59:14.089Z</OrderCompleteDate>
                <Order>
                    <CustomerOrderId>abc-2021</CustomerOrderId>
                    <Name>test order 10</Name>
                    <OrderCreateDate>2016-11-08T14:59:09.346Z</OrderCreateDate>
                    <PeerId>912912</PeerId>
                    <BackOrderRequested>true</BackOrderRequested>
                    <TollFreeWildCharSearchAndOrderType>
                        <Quantity>1</Quantity>
                        <TollFreeWildCardPattern>8**</TollFreeWildCardPattern>
                    </TollFreeWildCharSearchAndOrderType>
                    <PartialAllowed>true</PartialAllowed>
                    <SiteId>2993</SiteId>
                </Order>
                <OrderStatus>COMPLETE</OrderStatus>
                <CompletedNumbers>
                    <TelephoneNumber>
                        <FullNumber>8446107874</FullNumber>
                    </TelephoneNumber>
                </CompletedNumbers>
                <Summary>1 number ordered in (844)</Summary>
            </OrderResponse>
        '''
        with requests_mock.Mocker() as m:
            url = 'http://resource_tests/123456/{0}'.format(Order.orders_path)
            m.post(url, content=order_response)

            order = Order.create_toll_free_wild_char_search_and_order(wild_card_pattern='8**',
                                                                      quantity='1',
                                                                      name='test order 10',
                                                                      site_id='2993',
                                                                      peer_id='912912',
                                                                      customer_order_id='abc-2021',
                                                                      back_order_requested='true'
                                                                      )


            self.assertTrue(isinstance(order, dict))
            self.assertTrue(isinstance(order['OrderResponse'], dict))
            self.assertTrue(isinstance(order['OrderResponse']['Order'], dict))
            self.assertEqual(order['OrderResponse']['Order']['Name'], 'test order 10')
            self.assertEqual(order['OrderResponse']['Order']['PeerId'], '912912')
            self.assertEqual(order['OrderResponse']['Order']['BackOrderRequested'], 'true')
            self.assertEqual(order['OrderResponse']['Order']['SiteId'], '2993')
            self.assertEqual(order['OrderResponse']['Order']['TollFreeWildCharSearchAndOrderType']['Quantity'], '1')
            self.assertEqual(order['OrderResponse']['Order']['TollFreeWildCharSearchAndOrderType']['TollFreeWildCardPattern'], '8**')
            self.assertEqual(order['OrderResponse']['OrderStatus'], 'RECEIVED')

            id = order['OrderResponse']['Order']['id']

            url = '{0}/{1}'.format(url, id)
            m.get(url, content=order_inst)
            completed_order = Order.get(id)

            self.assertTrue(isinstance(completed_order, dict))
            self.assertEqual(completed_order['OrderResponse']['OrderStatus'], 'COMPLETE')
            self.assertEqual(completed_order['OrderResponse']['CompletedQuantity'], '1')
            self.assertEqual(completed_order['OrderResponse']['CreatedByUser'], 'testUser')

            tn_list = completed_order['OrderResponse']['CompletedNumbers']
            self.assertEqual(tn_list[0]['FullNumber'], '8446107874')


    def test_create_combined_search_and_order(self):
        order_response = \
            '''

            '''

        order_inst = \
            '''
            '''
        with requests_mock.Mocker() as m:
            url = 'http://resource_tests/123456/{0}'.format(Order.orders_path)
            m.post(url, content=order_response)

            order = Order.create_combined_search_and_order(area_code='',
                                                           rate_center='',
                                                           state='',
                                                           npanxx='',
                                                           lata='',
                                                           city='',
                                                           zip='',
                                                           enable_lca='',
                                                           quantity='',
                                                           local_vantity=None,
                                                           ends_in='false',
                                                           name='test order 10',
                                                           site_id='2993',
                                                           peer_id='912912',
                                                           customer_order_id='abc-2021',
                                                           back_order_requested='true'
                                                           )

            self.assertTrue(isinstance(order, dict))
            self.assertTrue(isinstance(order['OrderResponse'], dict))
            self.assertTrue(isinstance(order['OrderResponse']['Order'], dict))
            self.assertEqual(order['OrderResponse']['Order']['Name'], 'test order 10')
            self.assertEqual(order['OrderResponse']['Order']['PeerId'], '912912')
            self.assertEqual(order['OrderResponse']['Order']['BackOrderRequested'], 'true')
            self.assertEqual(order['OrderResponse']['Order']['SiteId'], '2993')
            self.assertEqual(order['OrderResponse']['Order']['CombinedSearchAndOrderType']['Quantity'], '1')
            self.assertEqual(order['OrderResponse']['Order']['CombinedSearchAndOrderType']['RateCenter'], '')
            self.assertEqual(order['OrderResponse']['OrderStatus'], 'RECEIVED')

            id = order['OrderResponse']['Order']['id']

            url = '{0}/{1}'.format(url, id)
            m.get(url, content=order_inst)
            completed_order = Order.get(id)

            self.assertTrue(isinstance(completed_order, dict))
            self.assertEqual(completed_order['OrderResponse']['OrderStatus'], 'COMPLETE')
            self.assertEqual(completed_order['OrderResponse']['CompletedQuantity'], '1')
            self.assertEqual(completed_order['OrderResponse']['CreatedByUser'], 'testUser')
            self.assertEqual(completed_order['OrderResponse']['FailedQuantity'], '0')

            tn_list = completed_order['OrderResponse']['CompletedNumbers']
            self.assertEqual(tn_list[0]['FullNumber'], '8552178735')


