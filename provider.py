#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import requests


class SpellCheckerProvider(object):

    def __init__(self, server_addr):
        self.server_addr = server_addr

    def spell_check(self, word):
        payload = {'word': word}
        r = requests.post(self.server_addr, json=payload)
        if r.status_code != 200:
            raise ValueError('unrecognized format')
        result = r.json()
        if 'result' in result:
            return result['result']
        else:
            raise ValueError('unrecognized format')


if __name__ == '__main__':
    a = SpellCheckerProvider('http://54.88.99.94:20002/spell-check')
    print(a.spell_check('Helllo woorld'))
