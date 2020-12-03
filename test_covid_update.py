from covid_update import get_covid

def test_invalid_city():
    cases, deaths, date = get_covid('invalid', '2020-11-21')
    assert (cases, deaths, date) == (None, None, None)

def test_invalid_date():
    cases, deaths, date = get_covid('Exeter', 'asa-131-as')
    assert (cases, deaths, date) == (None, None, None)

def test_none():
    cases, deaths, date = get_covid('', '')
    assert (cases, deaths, date) == (None, None, None)

def test_missing_one():
    cases, deaths, date = get_covid('Exeter', '')
    assert (cases, deaths, date) == (None, None, None)

def test_valid():
    cases, deaths, date = get_covid('Exeter', '2020-11-21')
    assert (cases, deaths, date) != (None, None, None)

def test_valid_date():
    cases, deaths, date = get_covid('Exeter', '2020-11-21')
    assert date == '2020-11-21'

def test_cases():
    cases, deaths, date = get_covid('Exeter', '2020-11-21')
    assert cases != None and isinstance(cases, int)

def test_types():
    cases, deaths, date = get_covid('Exeter', '2020-11-21')
    assert isinstance(cases, int) and isinstance(deaths, int) or deaths == None and isinstance(date, str)
