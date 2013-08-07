import time

from path import path

from clld.tests.util import TestWithSelenium

import apics


class Tests(TestWithSelenium):
    app = apics.main({}, **{'sqlalchemy.url': 'postgres://robert@/apics'})

    def test_map(self):
        map_ = self.get_map('/contributions')
        map_.test_show_marker()
        map_.test_show_legend()
        map_.test_show_legend('lexifier')

    def test_datatable(self):
        dt = self.get_datatable('/contributions')
        dt.filter('name', 'Afr')
        self.assertEqual(dt.get_info().filtered, 2)
        dt.filter('lexifier', 'English')
        self.assertEqual(dt.get_info().filtered, 1)

    def test_region_col(self):
        dt = self.get_datatable('/contributions')
        dt.sort('Region')
        self.assert_('Australia' in dt.get_first_row())
        dt.filter('region', 'Australia')
        self.assertEqual(dt.get_info().filtered, 2)

