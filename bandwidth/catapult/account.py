class AccountMixin:
    def get_account():
        data, _, _ = self._make_request('get', '/users/%s/account' % self.user_id)
        return data

    def get_account_transactions(query = None):
        data, _, _ = self._make_request('get', '/users/%s/transactions' % self.user_id, params=query)
        return data
