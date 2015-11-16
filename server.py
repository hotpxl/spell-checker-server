#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import os.path
import flask
import spell_checker

app = flask.Flask(__name__)

app.config.update(
    JSONIFY_PRETTYPRINT_REGULAR=False
)

checker = spell_checker.GoogleSpellChecker(os.path.abspath('./bin/phantomjs'))

@app.route('/spell-check', methods=['POST'])
def spell_check():
    if not flask.request.json or 'word' not in flask.request.json:
        return (flask.jsonify({'error': 'unrecognized format'}), 400)
    else:
        res = checker.correct_spelling(flask.request.json['word'])
        if res:
            return flask.jsonify({'result': res})
        else:
            return (flask.jsonify({'error': 'request error'}), 400)

if __name__ == '__main__':
    app.run()

