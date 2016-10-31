import six
from lxml.etree import Element, SubElement, tostring, fromstring

import bandwidth_sdk
import bandwidth_sdk.models as models
from bandwidth_sdk.models import GenericResource
from bandwidth_sdk.client import get_iris_client
from bandwidth_sdk.utils import to_api, drop_empty, etree2dict, etree_to_simple_list, camelize, remove_key_from_dict


def get_content_from_path(path, **kwargs):
    client = get_iris_client()

    url = '{0}/{1}/{2}'.format(bandwidth_sdk.iris_endpoint, bandwidth_sdk.account_id, path)

    params = to_api(kwargs)

    response = client.get(url=url, join_endpoint=False, params=params)
    content = response.content

    return content


class TelephoneNumber(models.GenericResource):
    available_numbers_path = 'availableNumbers'
    inservice_numbers_path = 'inserviceNumbers'
    tn_list_element_name = 'TelephoneNumberList'
    tn_details_element_name = 'TelephoneNumberDetailList'
    enable_tn_details = 'enableTNDetail'

    @classmethod
    def list_available_numbers(cls, **kwargs):
        """
        This method returns a list of dictionaries with TelephoneNumber. Use the list_available_numbers_with_details
        method if you want a list of details
        Args:
            **kwargs:

        Returns:list of dictionaries with TelephoneNumber
        """
        kwargs = remove_key_from_dict(kwargs, cls.enable_tn_details)

        content = get_content_from_path(cls.available_numbers_path, **kwargs)

        if content:
            root = fromstring(content)

            tn_list = etree_to_simple_list(root, cls.tn_list_element_name)

        return tn_list


    @classmethod
    def list_available_numbers_with_details(cls, **kwargs):
        """
        This method returns a list of dictionaries with TelephoneNumberDetails. Use the list_available_numbers list if
        you just want a list of TelephoneNumbers.
        Args:
            **kwargs:

        Returns: list of dictionaries with TelephoneNumberDetail
        """
        kwargs = remove_key_from_dict(kwargs, cls.enable_tn_details)

        kwargs[cls.enable_tn_details] = True

        content = get_content_from_path(cls.available_numbers_path, **kwargs)

        if content:
            root = fromstring(content)
            tn_list = etree_to_simple_list(root, cls.tn_details_element_name)

        return tn_list


    @classmethod
    def get(*args, **kwargs):
        """
        note that this will have to include the TNs endpoint, as well as inservice_numbers
            <TelephoneNumberDetail>
                <City>COLORADO SPRINGS</City>
                <LATA>658</LATA>
                <RateCenter>COLORDOSPG</RateCenter>
                <State>CO</State>
                <FullNumber>7192031416</FullNumber>
                <Tier>0</Tier>
                <VendorId>49</VendorId>
                <VendorName>Bandwidth CLEC</VendorName>
            </TelephoneNumberDetail>
        """
        client = get_iris_client()


    @classmethod
    def list_inservice_numbers(*args, **kwargs):
        """
        TODO Implement this
        """
        client = get_iris_client()



class Order(GenericResource):

    orders_path='orders'
    order_element_name = 'Order'

    def __init__(self):
        super(GenericResource, self).__init__()


    @classmethod
    def get(cls, order_id=None, location_link=None):
        """

        Args:
            order_id:
            location_link:

        Returns:

        """
        if location_link is not None:
            url = location_link
        elif order_id is not None:
            url = '{0}/{1}/{2}/{3}'.format(bandwidth_sdk.iris_endpoint,
                                       bandwidth_sdk.account_id,
                                       cls.orders_path,
                                       order_id)
        else:
            return None # can't get an Order if there's not an id

        client_ = get_iris_client()
        response = client_.get(url=url, join_endpoint=False)

        content = response.content
        if content:
            root = fromstring(content)
            order = etree2dict(root)

        return order


    @classmethod
    def list(cls, *args):
        pass

    @classmethod
    def _create(cls, payload):  # pragma: no cover
        """
        Internal method that should never be called directly. Use one of the create_xxx_order methods

        This method takes a payload, generates a url and calls the client post method with the order payload
        :param args:
        :param kwargs:
        :return:
        """
        client = get_iris_client()
        url = '{0}/{1}/{2}'.format(bandwidth_sdk.iris_endpoint, bandwidth_sdk.account_id, cls.orders_path)
        response = client.post(url, data=payload, join_endpoint=False, xml=True)
        content = response.content
        if content:
            root = fromstring(content)

            order_response = etree2dict(root)

        return order_response


    @classmethod
    def create_existing_telephone_number_order(cls,
                                               telephone_number_list=None,
                                               reservation_id_list=None,
                                               **kwargs):
        """
        this method creates the xml to order of ExistingTelephoneNumberOrderType, e.g.
            <ExistingTelephoneNumberOrderType>
                <TelephoneNumberList>
                    <TelephoneNumber>9193752369</TelephoneNumber>
                    <TelephoneNumber>9193752720</TelephoneNumber>
                    <TelephoneNumber>9193752648</TelephoneNumber>
                </TelephoneNumberList>
                <ReservationIdList>
                    <ReservationId>[GUID]</ReservationId>
                    <ReservationId>[GUID]</ReservationId>
                </ReservationIdList>
            </ExistingTelephoneNumberOrderType>
        Args:
            telephone_number_list:
            reservation_id_list:
            **kwargs:

        Returns: A dictionary with Order and ExistingTelephoneNumberOrderType

        """
        # get the main 'Order' xml
        order_node = Order.to_xml(**kwargs)
        order_type_node = SubElement(order_node, 'ExistingTelephoneNumberOrderType')

        if telephone_number_list is not None:
            tn_list_node = SubElement(order_type_node, 'TelephoneNumberList')
            for tn in telephone_number_list:
                SubElement(tn_list_node, camelize(tn.keys()[0])).text = tn.values()[0]

        if reservation_id_list is not None:
            res_list_node = SubElement(order_type_node, 'ReservationIdList')
            for res in reservation_id_list:
                SubElement(res_list_node, camelize(res.keys()[0])).text = res.values()[0]

        payload = tostring(order_node)
        # TODO - print payload on debug

        # return the OrderResponse
        return Order._create(payload)


    @classmethod
    def create_area_code_search_and_order(cls, area_code, quantity, **kwargs):
        """
            Searchs for and creates an order given an area code and quantity
            <AreaCodeSearchAndOrderType>
                <AreaCode>617</AreaCode>
                <Quantity>1</Quantity>
            </AreaCodeSearchAndOrderType>

        Args:
            area_code:
            quantity:
            *kwargs:

        Returns:

        """
        # get the main 'Order' xml
        order_node = Order.to_xml(**kwargs)

        # add the specifics for this order type
        order_type_node = SubElement(order_node, 'AreaCodeSearchAndOrderType')
        SubElement(order_type_node, 'AreaCode').text = area_code
        SubElement(order_type_node, 'Quantity').text = quantity

        payload = tostring(order_node)
        # TODO - print payload on debug

        # return the OrderResponse
        return Order._create(payload)


    @classmethod
    def create_rate_center_search_and_order(cls, rate_center, state, quantity, **kwargs):
        """
        <RateCenterSearchAndOrderType>
            <RateCenter>RALEIGH</RateCenter>
            <State>NC</State>
            <Quantity>1</Quantity>
        </RateCenterSearchAndOrderType>
        Args:
            rate_center: name of rate cetner
            state:
            quantity:
            **kwargs:

        Returns: dictionary with OrderResponse
        """
        # get the main 'Order' xml
        order_node = Order.to_xml(**kwargs)

        # add the specifics for this order type
        order_type_node = SubElement(order_node, 'RateCenterSearchAndOrderType')
        SubElement(order_type_node, 'RateCenter').text = rate_center
        SubElement(order_type_node, 'State').text = state
        SubElement(order_type_node, 'Quantity').text = quantity

        payload = tostring(order_node)

        #TODO - print payload on debug

        return Order._create(payload)


    @classmethod
    def create_npsnxx_search_And_order(cls, npanxx, quantity, enable_lca='false', enable_tn_details='false', **kwargs):
        """
        <NPANXXSearchAndOrderType>
            <NpaNxx>919439</NpaNxx>
            <EnableTNDetail>true</EnableTNDetail>
            <EnableLCA>false</EnableLCA>
            <Quantity>1</Quantity>
        </NPANXXSearchAndOrderType>
        Args:
            npanxx:
            quantity:
            enable_lca:
            enable_tn_details:
            **kwargs:

        Returns: dictionary with OrderResponse

        """
        # get the main 'Order' xml
        order_node = Order.to_xml(**kwargs)

        # add the specifics for this order type
        order_type_node = SubElement(order_node, 'NPANXXSearchAndOrderType')
        SubElement(order_type_node, 'NpaNxx').text = npanxx
        SubElement(order_type_node, 'Quantity').text = quantity
        SubElement(order_type_node, 'EnableLCA').text = enable_lca
        SubElement(order_type_node, 'EnableTNDetail').text = enable_tn_details

        payload = tostring(order_node)
        #TODO - print payload on debug

        #return the OrderResponse
        return Order._create(payload)


    @classmethod
    def create_toll_free_vanity_search_and_order(cls, toll_free_vanity, quantity, **kwargs):
        """
        <TollFreeVanitySearchAndOrderType>
            <TollFreeVanity>newcars</TollFreeVanity>
            <Quantity>1</Quantity>
        </TollFreeVanitySearchAndOrderType>
        Args:
            toll_free_vanity:
            quantity:
            **kwargs:

        Returns: dictionary with OrderResponse

        """
        # get the main 'Order' xml
        order_node = Order.to_xml(**kwargs)

        # add the specifics for this order type
        order_type_node = SubElement(order_node, 'TollFreeVanitySearchAndOrderType')
        SubElement(order_type_node, 'TollFreeVanity').text = toll_free_vanity
        SubElement(order_type_node, 'Quantity').text = quantity

        payload = tostring(order_node)
        #TODO - print payload on debug

        #return the OrderResponse
        return Order._create(payload)


    @classmethod
    def create_toll_free_wild_char_search_and_order(cls, wild_card_pattern, quantity, **kwargs):
        """
        <TollFreeWildCharSearchAndOrderType>
            <TollFreeWildCardPattern>8**</TollFreeWildCardPattern>
            <Quantity>1</Quantity>
        </TollFreeWildCharSearchAndOrderType>
        Args:
            wild_card_pattern:
            quantity:
            **kwargs:

        Returns:
        """
        # get the main 'Order' xml
        order_node = Order.to_xml(**kwargs)

        # add the specifics for this order type
        order_type_node = SubElement(order_node, 'TollFreeWildCharSearchAndOrderType')
        SubElement(order_type_node, 'TollFreeWildCardPattern').text = wild_card_pattern
        SubElement(order_type_node, 'Quantity').text = quantity

        payload = tostring(order_node)
        #TODO - print payload on debug

        #return the OrderResponse
        return Order._create(payload)


    @classmethod
    def create_state_search_and_order(cls, state, quantity, **kwargs):
        """
        <StateSearchAndOrderType>
            <State>CO</State>
            <Quantity>1</Quantity>
        </StateSearchAndOrderType>
        Args:
            state:
            quantity:
            **kwargs:

        Returns:
        """
        # get the main 'Order' xml
        order_node = Order.to_xml(**kwargs)

        # add the specifics for this order type
        order_type_node = SubElement(order_node, 'StateSearchAndOrderType')
        SubElement(order_type_node, 'State').text = state
        SubElement(order_type_node, 'Quantity').text = quantity

        payload = tostring(order_node)
        #TODO - print payload on debug

        #return the OrderResponse
        return Order._create(payload)


    @classmethod
    def create_city_search_and_order(cls, city, state, quantity, **kwargs):
        """
        <CitySearchAndOrderType>
            <City>RALEIGH</City>
            <State>NC</State>
            <Quantity>1</Quantity>
        </CitySearchAndOrderType>
        Args:
            city:
            state:
            quantity:
            **kwargs:

        Returns:
        """
        # get the main 'Order' xml
        order_node = Order.to_xml(**kwargs)

        # add the specifics for this order type
        order_type_node = SubElement(order_node, 'CitySearchAndOrderType')
        SubElement(order_type_node, 'City').text = city
        SubElement(order_type_node, 'State').text = state
        SubElement(order_type_node, 'Quantity').text = quantity

        payload = tostring(order_node)
        #TODO - print payload on debug

        #return the OrderResponse
        return Order._create(payload)


    @classmethod
    def create_zip_search_and_order(cls, zip, quantity, **kwargs):
        """
        <ZIPSearchAndOrderType>
            <Zip>27606</Zip>
            <Quantity>1</Quantity>
        </ZIPSearchAndOrderType>
        Args:
            zip:
            quantity:
            **kwargs:

        Returns:
        """
        # get the main 'Order' xml
        order_node = Order.to_xml(**kwargs)

        # add the specifics for this order type
        order_type_node = SubElement(order_node, 'ZIPSearchAndOrderType')
        SubElement(order_type_node, 'Zip').text = zip
        SubElement(order_type_node, 'Quantity').text = quantity

        payload = tostring(order_node)
        # TODO - print payload on debug

        # return the OrderResponse
        return Order._create(payload)


    @classmethod
    def create_lata_search_and_order(cls, lata, quantity, **kwargs):
        """
        <LATASearchAndOrderType>
            <Lata>224</Lata>
            <Quantity>1</Quantity>
        </LATASearchAndOrderType>
        Args:
            lata:
            quantity:
            **kwargs:

        Returns:

        """
        # get the main 'Order' xml
        order_node = Order.to_xml(**kwargs)

        # add the specifics for this order type
        order_type_node = SubElement(order_node, 'LATASearchAndOrderType')
        SubElement(order_type_node, 'Lata').text = lata
        SubElement(order_type_node, 'Quantity').text = quantity

        payload = tostring(order_node)
        # TODO - print payload on debug

        # return the OrderResponse
        return Order._create(payload)


    @classmethod
    def create_combined_search_and_order(cls,
                                         area_code,
                                         rate_center,
                                         state,
                                         npanxx,
                                         lata,
                                         city,
                                         zip,
                                         enable_lca,
                                         quantity,
                                         local_vantity=None,
                                         ends_in='false',
                                         **kwargs):
        """
       <CombinedSearchAndOrderType>
            <AreaCode>617</AreaCode>
            <RateCenter>RALEIGH</RateCenter>
            <State>NC</State>
            <NpaNxx>919439</NpaNxx>
            <Lata>224</Lata>
            <City>RALEIGH</City>
            <Zip>27606</Zip>
            <EnableLCA>false</EnableLCA>
            <Quantity>1</Quantity>
        </CombinedSearchAndOrderType>

        or the following:

        <CombinedSearchAndOrderType>
            <Quantity>1</Quantity>
            <AreaCode>617</AreaCode>
            <LocalVanity>newcars</LocalVanity>
            <EndsIn>false</EndsIn>
        </CombinedSearchAndOrderType>
        Args:
            area_code:
            rate_center:
            state:
            npanxx:
            lata:
            city:
            zip:
            enable_lca:
            quantity:
            local_vantity:
            ends_in:
            **kwargs:

        Returns:

        """
        # get the main 'Order' xml
        order_node = Order.to_xml(**kwargs)

        # add the specifics for this order type
        order_type_node = SubElement(order_node, 'CombinedSearchAndOrderType')
        SubElement(order_type_node, 'AreaCode').text = area_code
        SubElement(order_type_node, 'RateCenter').text = rate_center
        SubElement(order_type_node, 'State').text = state
        SubElement(order_type_node, 'NpaNxx').text = npanxx
        SubElement(order_type_node, 'Lata').text = lata
        SubElement(order_type_node, 'City').text = city
        SubElement(order_type_node, 'Zip').text = zip
        SubElement(order_type_node, 'EnableLCA').text = enable_lca
        SubElement(order_type_node, 'Quantity').text = quantity
        if local_vantity is not None:
            SubElement(order_type_node, 'LocalVanity').text = local_vantity
            SubElement(order_type_node, 'EndsIn').text = ends_in


        payload = tostring(order_node)
        # TODO - print payload on debug

        # return the OrderResponse
        return Order._create(payload)

    @classmethod
    def to_xml(cls, **kwargs):
        """
        This generates the 'Order' part of the order. The order types are generated by their respective subclasses
        <Order>
            <CustomerOrderId>123456789</CustomerOrderId>
            <Name>Existing Number Order</Name>
            <ExistingTelephoneNumberOrderType>
                <TelephoneNumberList>
                    <TelephoneNumber>9193752369</TelephoneNumber>
                    <TelephoneNumber>9193752720</TelephoneNumber>
                    <TelephoneNumber>9193752648</TelephoneNumber>
                </TelephoneNumberList>
                <ReservationIdList>
                    <ReservationId>[GUID]</ReservationId>
                    <ReservationId>[GUID]</ReservationId>
                </ReservationIdList>
            </ExistingTelephoneNumberOrderType>
            <SiteId>743</SiteId>
        </Order>
        Args:
            **kwargs: contains the Order name/value pairs

        Returns: A dictionary with an Order node

        """
        if not kwargs:
            return {}
        assert isinstance(kwargs, dict), 'Wrong type'
        data = drop_empty(kwargs)

        root = Element(cls.__name__)

        for k, v in six.iteritems(kwargs):
            SubElement(root, camelize(k)).text = v

        return root