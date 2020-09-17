# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     notifications
   Description :
   Author :       ybw
   date：          2020/9/16
-------------------------------------------------
   Change Activity:
                   2020/9/16:
-------------------------------------------------
"""

from flask import url_for

from albumy.models.model import Notification
from  albumy.extensions import db

def push_follow_notification(follower, receiver):
    """
    推送关注提醒
    :param follower:
    :param receiver:
    :return:
    """
    message = 'User <a href="%s">%s</a> followed you.' % \
              (url_for('user.index', username=follower.username), follower.username)
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_comment_notification(photo_id, receiver, page=1):
    """
    推送评论提醒
    :param photo_id:
    :param receiver:
    :param page:
    :return:
    """
    message = '<a href="%s#comments">This photo</a> has new comment/reply.' % \
              (url_for('main.show_photo', photo_id=photo_id, page=page))
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_collect_notification(collector, photo_id, receiver):
    """
    推送收藏提醒
    :param collector:
    :param photo_id:
    :param receiver:
    :return:
    """
    message = 'User <a href="%s">%s</a> collected your <a href="%s">photo</a>' % \
              (url_for('user.index', username=collector.username),
               collector.username,
               url_for('main.show_photo', photo_id=photo_id))
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()