# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     model
   Description :
   Author :       ybw
   date：          2020/9/4
-------------------------------------------------
   Change Activity:
                   2020/9/4:
-------------------------------------------------
"""
from datetime import datetime

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from albumy.extensions import db

roles_permissions = db.Table(
    'roles_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id')),
)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    permissions = db.relationship('Permission', secondary=roles_permissions, back_populates='roles')
    # back_populates是在另一侧显示定义关系属性role
    users = db.relationship('User', back_populates='role')

    @staticmethod
    def init_role():
        """
        init role <-> permission
        :return:
        """
        roles_permissions_map = {
            'Locked': ['FOLLOW', 'COLLECT'],
            'User': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD'],
            'Moderator': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD', 'MODERATE'],
            'Administrator': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD', 'MODERATE', 'ADMINISTER']
        }

        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name)
                db.session.add(role)
            role.permissions = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if not permission:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)
        db.session.commit()


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    roles = db.relationship('Role', secondary=roles_permissions, back_populates='permissions')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # 资料
    username = db.Column(db.String(20), unique=True, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(30))
    website = db.Column(db.String(255))
    bio = db.Column(db.String(120))
    location = db.Column(db.String(50))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    # 用户状态,是否认证
    confirmed = db.Column(db.Boolean, default=False)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', back_populates='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.set_role()

    def set_role(self):
        if not self.role:
            if self.email == current_app.config["ALBUMY_ADMIN_EMAIL"]:
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(name='User').first()
            db.session.commit()

    # 对于Flask_Login的普通用户，访客并没有is_admin,can的方法，所以需要手动自定义Guest类
    @property
    def is_admin(self):
        """
        验证是否是管理员
        :return:
        """
        return self.role.name == "Administrator"

    def can(self, permission_name):
        """
        验证该用户是否拥有该权限
        :param permission_name: 权限名称
        :return:
        """
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission and self.role and permission in self.role.permissions


    @staticmethod
    def init_role():
        """
        初始化没有权限的用户
        :return:
        """
        for user in User.query.all():
            if not user.role:
                if user.email == current_app.config["ALBUMY_ADMIN_EMAIL"]:
                    user.role = Role.query.filter_by(name='Administrator').first()
                else:
                    user.role = Role.query.filter_by(name='User').first()
            db.session.add(user)
        db.session.commit()
