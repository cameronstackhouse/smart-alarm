from news_filter import get_news

def test_invalid_key():
    stories = get_news('aa', 'gb')
    assert stories == {}

def test_invalid_area():
    stories = get_news('c1cbe821f0d24fb49be55f5c86172737', 'aaab')
    assert stories == {}

def test_none():
    stories = get_news('', '')
    assert stories == {}

def test_valid():
    stories = get_news('c1cbe821f0d24fb49be55f5c86172737', 'gb')
    assert stories != {}

def test_connection():
    pass
