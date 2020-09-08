# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     wsgi
   Description :
   Author :       ybw
   date：          2020/9/4
-------------------------------------------------
   Change Activity:
                   2020/9/4:
-------------------------------------------------
"""

from albumy import create_app

app = create_app()

if __name__ == '__main__':
    app.run()