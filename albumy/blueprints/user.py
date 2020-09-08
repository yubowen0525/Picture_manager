# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     user
   Description :
   Author :       ybw
   date：          2020/9/8
-------------------------------------------------
   Change Activity:
                   2020/9/8:
-------------------------------------------------
"""
from flask import render_template, Blueprint

from albumy.models.model import User

user_bp = Blueprint('user', __name__)


@user_bp.route('/<username>')
def index(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user/index.html', user=user)
