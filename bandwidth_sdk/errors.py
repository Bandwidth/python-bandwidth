class AppPlatformError(Exception):
    """
    Raised by :meth:`Client.request()` for requests that:

      - Return a non-200 HTTP response, or
      - Connection refused/timeout or
      - Response timeout or
      - Malformed request
      - Have a malformed/missing header in the response.

    """
