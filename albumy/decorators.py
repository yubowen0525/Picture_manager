# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     decorators
   Description :
   Author :       ybw
   date：          2020/9/7
-------------------------------------------------
   Change Activity:
                   2020/9/7:
-------------------------------------------------
"""
from functools import wraps

from flask_login import current_user
from flask import Markup, url_for, flash, redirect, abort


def confirm_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.confirmed:
            message = Markup(
                'Please confirm your account first.'
                'Not receive the email?'
                '<a class="alert-link" href="%s">Resend Confirm Email</a>' %
                url_for('auth.resend_confirm_email'))
            flash(message, 'warning')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)

    return decorated_function


def permission_required(permission_name):
    def decorator(func):
        @wraps(func)
        def decoreated_function(*args, **kwargs):
            if not current_user.can(permission_name):
                abort(403)
            return func(*args, **kwargs)

        return decoreated_function

    return decorator


def logged(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        print(func.__name__ + " was called")
        return func(*args, **kwargs)

    return with_logging


def test1():
    print("hello world2")


@logged
def test(a, b, c, d):
    print("test", __name__)


# a_function_requiring_decoration = logged(test)
# print(a_function_requiring_decoration.__name__)
# a_function_requiring_decoration(1, 2, 3, 4)
# test(1,2,3,4)
