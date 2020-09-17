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
import os
from datetime import datetime

from flask import current_app
from flask_avatars import Identicon
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


# relationship object
class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # 关注者
    follower = db.relationship('User', foreign_keys=[follower_id], back_populates='following', lazy='joined')
    # 被关注者
    followed = db.relationship('User', foreign_keys=[followed_id], back_populates='followers', lazy='joined')


# relationship object
class Collect(db.Model):
    collector_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                             primary_key=True)
    collected_id = db.Column(db.Integer, db.ForeignKey('photo.id'),
                             primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # photo.collectors.collector | photo.collectors获取包含收藏对象的Collect的列表，.collector/collected才会加载对应的用户和图片
    # 这样就需要两次select，增加了一次查询，那么通过联结join这样只需要一次查询
    # 收藏者
    collector = db.relationship('User', back_populates='collections', lazy='joined')
    # 被收藏图片
    collected = db.relationship('Photo', back_populates='collectors', lazy='joined')


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
    # 若用户删除，则图片也所有删除
    photos = db.relationship('Photo', back_populates='author', cascade='all')
    # 评论
    comments = db.relationship('Comment', back_populates='author', cascade='all')
    # 收藏
    collections = db.relationship('Collect', back_populates='collector', cascade='all')
    # 正在关注
    following = db.relationship('Follow', foreign_keys=[Follow.follower_id], back_populates='follower', lazy='dynamic',
                                cascade='all')
    # 关注者
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], back_populates='followed', lazy='dynamic',
                                cascade='all')

    notifications = db.relationship('Notification', back_populates='receiver', cascade='all')

    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.set_role()
        self.generate_avatar()
        self.follow(self)

    def set_role(self):
        if not self.role:
            if self.email == current_app.config["ALBUMY_ADMIN_EMAIL"]:
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(name='User').first()
            db.session.commit()

    def generate_avatar(self):
        """

        :return:
        """
        avatar = Identicon()
        filenames = avatar.generate(text=self.username)
        self.avatar_s = filenames[0]
        self.avatar_m = filenames[1]
        self.avatar_l = filenames[2]
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

    def collect(self, photo):
        """
        收藏图片
        :param photo:
        :return:
        """
        if not self.is_collecting(photo):
            collect = Collect(collector=self, collected=photo)
            db.session.add(collect)
            db.session.commit()

    def uncollect(self, photo):
        """
        取消收藏
        :param photo:
        :return:
        """
        collect = Collect.query.with_parent(self).filter_by(collected_id=photo.id).first()
        if collect:
            db.session.delete(collect)
            db.session.commit()

    def follow(self, user):
        """
        关注用户
        :param user:
        :return:
        """
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        """
        取消关注用户
        :param user:
        :return:
        """
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    def is_following(self, user):
        if user.id is None:  # when follow self, user.id will be None
            return False
        return self.following.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(followed_id=user.id).first() is not None

    def is_collecting(self, photo):
        return Collect.query.with_parent(self).filter_by(collected_id=photo.id).first() is not None

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


tagging = db.Table('tagging',
                   db.Column('photo_id', db.Integer, db.ForeignKey('photo.id')),
                   db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                   )


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500))
    filename = db.Column(db.String(64))
    filename_s = db.Column(db.String(64))
    filename_m = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    can_comment = db.Column(db.Boolean, default=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    author = db.relationship('User', back_populates='photos')

    comments = db.relationship('Comment', back_populates='photo', cascade='all')

    tags = db.relationship('Tag', secondary=tagging, back_populates='photos')

    collectors = db.relationship('Collect', back_populates='collected', cascade='all')


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    photos = db.relationship('Photo', secondary=tagging, back_populates='tags')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    flag = db.Column(db.Integer, default=0)

    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    author = db.relationship('User', back_populates='comments')
    photo = db.relationship('Photo', back_populates='comments')
    replies = db.relationship('Comment', back_populates='replied', cascade='all')
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    received_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver = db.relationship('User', back_populates='notifications')

###########################################################################################


@db.event.listens_for(Photo, 'after_delete')
def delete_photos(mapper, connection, target):
    for filename in [target.filename, target.filename_s, target.filename_m]:
        path = os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'], filename)
        if os.path.exists(path):
            os.remove(path)
