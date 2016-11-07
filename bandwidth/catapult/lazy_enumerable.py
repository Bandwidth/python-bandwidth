def get_lazy_enumerator(client, get_first_page):
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
        get_data = lambda : client._make_request('get', next_page_url)
