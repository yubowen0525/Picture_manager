# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_base
   Description :
   Author :       ybw
   date：          2020/9/18
-------------------------------------------------
   Change Activity:
                   2020/9/18:
-------------------------------------------------
"""

from flask import current_app

from tests.base import BaseTestCase


class BasicTestCase(BaseTestCase):

    def test_app_exist(self):
        self.assertTrue(current_app)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_404_error(self):
        response = self.client.get('/foo')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn('404 Error', data)
