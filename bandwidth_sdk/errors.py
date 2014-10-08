class AppPlatformError(Exception):
    """
    Raised by :meth:`Client.request()` for requests that:

      - Return a non-200 HTTP response, or
      - Connection refused/timeout or
      - Response timeout or
      - Malformed request
      - Have a malformed/missing header in the response.

    """


class MessageCreationError(AppPlatformError):

    def __init__(self, error_message):
        self.error_message = error_message

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.error_message)
