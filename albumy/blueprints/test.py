# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test
   Description :
   Author :       ybw
   date：          2020/9/18
-------------------------------------------------
   Change Activity:
                   2020/9/18:
-------------------------------------------------
"""
import time

from flask import Blueprint, render_template

from albumy.extensions import cache

test_bp = Blueprint('test', __name__)


# 缓存时间设置为10分钟
@test_bp.route('/foo', methods=['GET'])
def foo():
    time.sleep(1)
    return render_template('test/foo.html')


@test_bp.route('/foo2', methods=['GET'])
@cache.cached(timeout=10 * 60)
def foo2():
    time.sleep(1)
    return render_template('test/foo.html')