# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask_avatars import Avatars
from flask_bootstrap import Bootstrap
from flask_dropzone import Dropzone
from flask_login import LoginManager, AnonymousUserMixin
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_whooshee import Whooshee

whooshee = Whooshee()
bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
moment = Moment()
login_manager = LoginManager()
dropzone = Dropzone()
avatars = Avatars()
csrf = CSRFProtect()


@login_manager.user_loader
def load_user(user_id):
    from albumy.models.model import User
    user = User.query.get(int(user_id))
    return user


class Guest(AnonymousUserMixin):
    confirmed = False

    @property
    def is_admin(self):
        return False

    @property
    def is_guest(self):
        return True

    def can(self, permission_name):
        return False


login_manager.anonymous_user = Guest

login_manager.login_view = 'auth.login'
# login_manager.login_message = 'Your custom message'
login_manager.login_message_category = 'warning'
