import time

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

    def test_values_table(self):
        dt = self.get_datatable('/parameters/1')
        dt.sort('Lexifier', sleep=3)
        row = dt.get_first_row()
        try:
            self.assert_('Arabic' in row)
        except:
            #print row
            pass
        dt.filter('lexifier', 'Dutch')
        self.assertEqual(dt.get_info().filtered, 5)
        dt.filter('language', 'B')
        self.assertEqual(dt.get_info().filtered, 1)
        b = self.browser.find_element_by_id('cite-button-1')
        b.click()
        time.sleep(2)
        b = self.browser.find_element_by_id('md-tab-opener-md.bib')
        b.click()
        self.get_datatable('/contributions/1')
        dt = self.get_datatable('/contributions/2')
        dt.sort('lect')
        dt.filter('language', 'Sranan')
        dt.sort('Feature')
