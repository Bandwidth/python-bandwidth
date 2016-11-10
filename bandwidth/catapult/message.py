from .lazy_enumerable import get_lazy_enumerator


class MessageMixin:
    def get_messages(self, query=None):
        path = '/users/%s/messages' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def send_message(self, data):
        return self._make_request('post', '/users/%s/messages' % self.user_id, json=data)[2]

    def send_messages(self, messages_data):
        results = self._make_request('post', '/users/%s/messages' % self.user_id, json=messages_data)[0]
        for i in range(0, len(messages_data)):
            item = results[i]
            item['id'] = item.get('location', '').split('/')[-1]
            item['message'] = messages_data[i]
        return results

    def get_message(self, id):
        return self._make_request('get', '/users/%s/messages/%s' % (self.user_id, id))[0]
