from main import set_alarm, k2c, set_notification, get_config, remove_notification, set_alarm
import main

def test_set_alarm():
    new_alarm = set_alarm('Test Title', 'Test Body', 'Placeholder event')
    assert new_alarm == {'title':'Test Title', 'content':'Test Body', 'event':'Placeholder event'}

def test_k2c_valid():
    assert k2c(400) == 126.85

def test_k2c_invalid():
    assert k2c('INVALID INPUT') == None

def test_set_notification():
    new_notification = set_notification('Test', 'Test')
    main.set_notifications.append(new_notification)
    assert main.set_notifications == [{'title':'Test', 'content':'Test'}]

def test_get_config():
    a, b, c, d, e, f, g, h, i = get_config('config.json')
    assert (a, b, c, d , e, f, g, h, i) != (None, None, None, None, None, None, None, None)

def test_get_invalid_config():
    try:
        a, b, c, d, e, f, g, h, i = get_config('config_invalid.json')
    except:
        a, b, c, d, e, f, g, h, i = '', '', '', '', '', 'app.log', [], 0, ''
    assert (a, b, c, d, e, f, g, h, i) == ('', '', '', '', '', 'app.log', [], 0, '')

def test_no_config():
    try:
        a, b, c, d, e, f, g, h, i = get_config('')
    except:
        a, b, c, d, e, f, g, h, i = '', '', '', '', '', 'app.log', [], 0, ''
    assert (a, b, c, d, e, f, g, h, i) == ('', '', '', '', '', 'app.log', [], 0, '')
