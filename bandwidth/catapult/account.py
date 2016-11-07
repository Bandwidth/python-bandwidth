class AccountMixin:
    def get_account(self):
        return self._make_request('get', '/users/%s/account' % self.user_id)[0]

    def get_account_transactions(self, query=None):
        return self._make_request('get', '/users/%s/account/transactions' % self.user_id, params=query)[0]
