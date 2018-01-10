import time


def test_map(selenium):
    map_ = selenium.get_map('/contributions')
    map_.test_show_marker()
    map_.test_show_legend()
    map_.test_show_legend('lexifier')


def test_datatable(selenium):
    dt = selenium.get_datatable('/contributions')
    dt.filter('name', 'Afr')
    assert dt.get_info().filtered == 2
    dt.filter('lexifier', 'English')
    assert dt.get_info().filtered == 1


def test_region_col(selenium):
    dt = selenium.get_datatable('/contributions')
    dt.sort('Region')
    assert 'Australia' in dt.get_first_row()
    dt.filter('region', 'Australia')
    assert dt.get_info().filtered == 2


def test_values_table(selenium):
    dt = selenium.get_datatable('/parameters/1')
    dt.sort('Lexifier', sleep=3)
    row = dt.get_first_row()
    assert 'Arabic' in row
    dt.filter('lexifier', 'Dutch')
    assert dt.get_info().filtered == 5
    dt.filter('language', 'B')
    assert dt.get_info().filtered == 1
    b = selenium.browser.find_element_by_id('cite-button-1')
    b.click()
    time.sleep(2)
    b = selenium.browser.find_element_by_id('md-tab-opener-md.bib')
    b.click()
    selenium.get_datatable('/contributions/1')
    dt = selenium.get_datatable('/contributions/2')
    dt.sort('lect')
    dt.filter('language', 'Sranan')
    dt.sort('Feature')
