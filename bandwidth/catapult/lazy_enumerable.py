
def get_lazy_enumerator(client, get_first_page):
    """
    Returns api results as "lazy" collection.
    Makes api requests for new parts of data on demand only.
    :type client: bandwidth.catapult.Client
    :param client: catapult client
    :type get_first_page: types.FunctionType
    :param get_first_page: function which returns contane of first part (page) of data

    :rtype: types.GeneratorType
    :returns: lazy collection
    """
    get_data = get_first_page
    while True:
        items, response, _ = get_data()
        next_page_url = ''
        for item in items:
            yield item
        links = response.headers.get('link', '').split(',')
        for link in links:
            values = link.split(';')
            if len(values) == 2 and values[1].strip() == 'rel="next"':
                next_page_url = values[0].replace('<', ' ').replace('>', ' ').strip()
                break
        if len(next_page_url) == 0:
            break

        def get_data():
            return client._make_request('get', next_page_url)
