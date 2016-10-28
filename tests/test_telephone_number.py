from unittest import TestCase
import os

import six
import requests
import requests_mock

from bandwidth_sdk.resources import TelephoneNumber
import bandwidth_sdk


if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch


class TestTelephoneNumber(TestCase):
    def setUp(self):
        bandwidth_sdk.account_id='123456'
        bandwidth_sdk.username='foo'
        bandwidth_sdk.password='bar'
        bandwidth_sdk.iris_endpoint = 'http://resource_tests'

    def tearDown(self):
        pass

    def test_list_available_numbers(self):
        xml_response = \
            '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <SearchResult>
                <ResultCount>10</ResultCount>
                <TelephoneNumberList>
                    <TelephoneNumber>7192041079</TelephoneNumber>
                    <TelephoneNumber>7192041097</TelephoneNumber>
                    <TelephoneNumber>7192041141</TelephoneNumber>
                    <TelephoneNumber>7192041168</TelephoneNumber>
                    <TelephoneNumber>7192041181</TelephoneNumber>
                    <TelephoneNumber>7192041221</TelephoneNumber>
                    <TelephoneNumber>7192041263</TelephoneNumber>
                    <TelephoneNumber>7192041348</TelephoneNumber>
                    <TelephoneNumber>7192041384</TelephoneNumber>
                    <TelephoneNumber>7192041388</TelephoneNumber>
                </TelephoneNumberList>
            </SearchResult>'''

        with requests_mock.Mocker() as m:

            url = 'http://resource_tests/123456/{0}'.format(TelephoneNumber.available_numbers_path)
            m.get(url, content=xml_response)
            available_numbers = TelephoneNumber.list_available_numbers(area_code='719', quantity='10')

            tn = available_numbers[0]

            self.assertTrue(isinstance(available_numbers, list))
            self.assertEqual(len(available_numbers), 10)
            self.assertTrue(isinstance(tn, dict))
            self.assertEqual(tn['TelephoneNumber'], '7192041079')


    def test_list_available_numbers_with_details(self):
        xml_response = \
            '''
            <SearchResult>
                <ResultCount>10</ResultCount>
                <TelephoneNumberDetailList>
                    <TelephoneNumberDetail>
                        <City>CANON CITY</City>
                        <LATA>658</LATA>
                        <RateCenter>CANON CITY</RateCenter>
                        <State>CO</State>
                        <FullNumber>7192041437</FullNumber>
                        <Tier>0</Tier>
                        <VendorId>49</VendorId>
                        <VendorName>Bandwidth CLEC</VendorName>
                    </TelephoneNumberDetail>
                    <TelephoneNumberDetail>
                        <City>CANON CITY</City>
                        <LATA>658</LATA>
                        <RateCenter>CANON CITY</RateCenter>
                        <State>CO</State>
                        <FullNumber>7192041449</FullNumber>
                        <Tier>0</Tier>
                        <VendorId>49</VendorId>
                        <VendorName>Bandwidth CLEC</VendorName>
                    </TelephoneNumberDetail>
                    <TelephoneNumberDetail>
                        <City>CANON CITY</City>
                        <LATA>658</LATA>
                        <RateCenter>CANON CITY</RateCenter>
                        <State>CO</State>
                        <FullNumber>7192041455</FullNumber>
                        <Tier>0</Tier>
                        <VendorId>49</VendorId>
                        <VendorName>Bandwidth CLEC</VendorName>
                    </TelephoneNumberDetail>
                    <TelephoneNumberDetail>
                        <City>CANON CITY</City>
                        <LATA>658</LATA>
                        <RateCenter>CANON CITY</RateCenter>
                        <State>CO</State>
                        <FullNumber>7192041495</FullNumber>
                        <Tier>0</Tier>
                        <VendorId>49</VendorId>
                        <VendorName>Bandwidth CLEC</VendorName>
                    </TelephoneNumberDetail>
                    <TelephoneNumberDetail>
                        <City>CANON CITY</City>
                        <LATA>658</LATA>
                        <RateCenter>CANON CITY</RateCenter>
                        <State>CO</State>
                        <FullNumber>7192041501</FullNumber>
                        <Tier>0</Tier>
                        <VendorId>49</VendorId>
                        <VendorName>Bandwidth CLEC</VendorName>
                    </TelephoneNumberDetail>
                    <TelephoneNumberDetail>
                        <City>CANON CITY</City>
                        <LATA>658</LATA>
                        <RateCenter>CANON CITY</RateCenter>
                        <State>CO</State>
                        <FullNumber>7192041506</FullNumber>
                        <Tier>0</Tier>
                        <VendorId>49</VendorId>
                        <VendorName>Bandwidth CLEC</VendorName>
                    </TelephoneNumberDetail>
                    <TelephoneNumberDetail>
                        <City>CANON CITY</City>
                        <LATA>658</LATA>
                        <RateCenter>CANON CITY</RateCenter>
                        <State>CO</State>
                        <FullNumber>7192041541</FullNumber>
                        <Tier>0</Tier>
                        <VendorId>49</VendorId>
                        <VendorName>Bandwidth CLEC</VendorName>
                    </TelephoneNumberDetail>
                    <TelephoneNumberDetail>
                        <City>CANON CITY</City>
                        <LATA>658</LATA>
                        <RateCenter>CANON CITY</RateCenter>
                        <State>CO</State>
                        <FullNumber>7192041555</FullNumber>
                        <Tier>0</Tier>
                        <VendorId>49</VendorId>
                        <VendorName>Bandwidth CLEC</VendorName>
                    </TelephoneNumberDetail>
                    <TelephoneNumberDetail>
                        <City>CANON CITY</City>
                        <LATA>658</LATA>
                        <RateCenter>CANON CITY</RateCenter>
                        <State>CO</State>
                        <FullNumber>7192041574</FullNumber>
                        <Tier>0</Tier>
                        <VendorId>49</VendorId>
                        <VendorName>Bandwidth CLEC</VendorName>
                    </TelephoneNumberDetail>
                    <TelephoneNumberDetail>
                        <City>CANON CITY</City>
                        <LATA>658</LATA>
                        <RateCenter>CANON CITY</RateCenter>
                        <State>CO</State>
                        <FullNumber>7192041593</FullNumber>
                        <Tier>0</Tier>
                        <VendorId>49</VendorId>
                        <VendorName>Bandwidth CLEC</VendorName>
                    </TelephoneNumberDetail>
                </TelephoneNumberDetailList>
            </SearchResult>
            '''

        with requests_mock.Mocker() as m:
            url = 'http://resource_tests/123456/{0}'.format(TelephoneNumber.available_numbers_path)
            m.get(url, content=xml_response)
            available_numbers = TelephoneNumber.list_available_numbers_with_details(area_code='719', quantity='10')

            tn = available_numbers[0]

            self.assertTrue(isinstance(available_numbers, list))
            self.assertEqual(len(available_numbers), 10)
            self.assertTrue(isinstance(tn, dict))
            self.assertTrue(isinstance(tn['TelephoneNumberDetail'], dict))
            self.assertTrue(tn['TelephoneNumberDetail']['City'], 'CANON CITY' )
            self.assertTrue(tn['TelephoneNumberDetail']['VendorId'], '49' )
            self.assertTrue(tn['TelephoneNumberDetail']['FullNumber'], '7192041079')
            self.assertTrue(tn['TelephoneNumberDetail']['State'], 'CO')
            self.assertTrue(tn['TelephoneNumberDetail']['LATA'], '658')
            self.assertTrue(tn['TelephoneNumberDetail']['RateCenter'], 'CANON CITY')
            self.assertTrue(tn['TelephoneNumberDetail']['Tier'], '0')
            self.assertTrue(tn['TelephoneNumberDetail']['VendorName'], 'Bandwidth CLEC')

    def test_list_inservice_numbers(self):
        pass

