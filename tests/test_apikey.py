# -*- coding: utf-8 -*-

import abuseip

def test_get_apikey():
    apikey = abuseip.get_apikey()
    assert apikey == 'pytest_123'
    apikey = abuseip.get_apikey('../src')
    assert apikey != 'pytest_123'
