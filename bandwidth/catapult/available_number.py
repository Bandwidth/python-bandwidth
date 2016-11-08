class AvailableNumberMixin:
    def search_available_numbers(self, number_type='local', query=None):
        return self._make_request('get', '/availableNumbers/%s' % number_type, params=query)[0]

    def search_and_order_available_numbers(self, number_type='local', query=None):
        list = self._make_request('post', '/availableNumbers/%s' % number_type, params=query)[0]
        for item in list:
            item['id'] = item.get('location', '').split('/')[-1]
        return list
