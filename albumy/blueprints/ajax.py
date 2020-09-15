# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ajax
   Description :
   Author :       ybw
   date：          2020/9/14
-------------------------------------------------
   Change Activity:
                   2020/9/14:
-------------------------------------------------
"""
from flask import Blueprint, render_template, abort

from albumy.models.model import User

ajax_bp = Blueprint("ajax", __name__)


@ajax_bp.route('/profile/<int:user_id>')
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('main/profile_popup.html', user=user)
