from .lazy_enumerable import get_lazy_enumerator


class AccountMixin:
    def get_account(self):
        return self._make_request('get', '/users/%s/account' % self.user_id)[0]

    def get_account_transactions(self, query=None):
        path = '/users/%s/account/transactions' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))
