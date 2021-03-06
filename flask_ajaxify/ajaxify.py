#!/usr/bin/env python
"""
Ajaxify an object

Request format:
    {
        "func" : function (string)
        "args" : args (json encoded list)
        "kwargs": kwargs (json encoded object/dict)
        "attr" : attribute (string)
    }

if a request has an attr, check that it does NOT have a func
if a request has a func, check that it does NOT have an attr

Return format:
    {
        "status" : 0 (no error, 1 python error, 2 js error)
        "error" : error message (string)
        "result" : variable (json encoded something)
    }
"""


import json
import os

import flask


def process_request(data, obj):
    if ('func' in data) and ('attr' in data):
        raise ValueError("Request must not contain func[%s] and attr[%s]" % \
                (data['func'], data['attr']))

    if 'attr' in data:
        attr = data.get('attr', '')
        if not hasattr(obj, attr):
            raise AttributeError("Object %s does not have attr %s" % \
                    (obj, attr))
        return getattr(obj, attr)

    if 'func' not in data:
        raise ValueError("Request must contain either a func or attr")
    # else 'func' in data
    func = data.get('func', '')
    if not hasattr(obj, func):
        raise AttributeError("Object %s does not have func %s" % \
                (obj, func))
    f = getattr(obj, func)

    args_str = data.get('args', '[]')
    try:
        args = json.loads(args_str)
        if not isinstance(args, list):
            raise ValueError("not a list")
    except Exception as E:
        raise ValueError("Failed to decode args [%s]: %s" % (args_str, E))

    kwargs_str = data.get('kwargs', '{}')
    try:
        kwargs = json.loads(kwargs_str)
        if not isinstance(kwargs, dict):
            raise ValueError("not a dict")
    except Exception as E:
        raise ValueError("Failed to decode kwargs [%s]: %s" % (kwargs_str, E))

    return f(*args, **kwargs)


def make_blueprint(obj, register=True, app=None, json_dumps_kwargs=None):
    name = 'ajaxify'  # only works for 1 name now
    main_dir = os.path.dirname(os.path.abspath(__file__))
    template_folder = os.path.join(main_dir, 'templates')
    static_folder = os.path.join(main_dir, 'static')

    ajax = flask.Blueprint(name, name, \
            template_folder=template_folder, static_folder=static_folder)
    json_dumps_kwargs = {} if json_dumps_kwargs is None else json_dumps_kwargs

    @ajax.route('/')
    def request():
        try:
            r = process_request(flask.request.args, obj)
            e = ''
            s = 0
        except Exception as E:
            s = 1
            e = 'PY: %s' % E
            r = ''
        return flask.jsonify(status=s, \
                result=json.dumps(r, **json_dumps_kwargs), error=e)

    @ajax.route('/test')
    def main():
        return flask.render_template('ajaxify_test.html')

    if register:
        if app is None:
            app = flask.Flask(name)
        app.register_blueprint(ajax, url_prefix='/%s' % name)
        return ajax, app
    else:
        return ajax


class Dummy(object):
    def __init__(self):
        self.name = 'dummy'

    def foo(self, *args, **kwargs):
        return args, kwargs


def test(**kwargs):
    d = Dummy()
    _, app = make_blueprint(d, register=True)
    app.run(**kwargs)


if __name__ == '__main__':
    test(debug=True)
