from __future__ import print_function, unicode_literals

import pytest


@pytest.mark.parametrize(
    "method,path",
    [
        ('get_html', '/'),
        ('get_html', '/credits'),
        ('get_html', '/help'),
        ('get_html', '/wals'),
        ('get_dt', '/wals'),
        ('get_html', '/wals/1'),
        ('get_html', '/languages/2'),
        ('get_html', '/contributors/abohenocho'),
        ('get_html', '/contributions/2'),
        ('get_html', '/parameters/1'),
        ('get_html', '/parameters/102'),
        ('get_json', '/parameters/1.geojson'),
        ('get_json', '/parameters/102.geojson'),
        ('get_html', '/valuesets/73-102'),
        ('get_html', '/valuesets/1-1'),
        ('get_html', '/sources/483'),
        ('get_html', '/languages'),
        ('get_html', '/contributors'),
        ('get_html', '/contributions'),
        ('get_html', '/parameters'),
        ('get_html', '/valuesets'),
        ('get_html', '/sources'),
        ('get_dt', '/languages?iSortingCols=1&iSortCol_0=1&sSortDir_0=desc'),
        ('get_dt', '/contributors?iSortingCols=1&iSortCol_0=1&sSortDir_0=desc'),
        ('get_dt', '/contributions?iSortingCols=1&iSortCol_0=1&sSortDir_0=desc'),
        ('get_dt', '/parameters?iSortingCols=1&iSortCol_0=1&sSortDir_0=desc'),
        ('get_dt', '/valuesets?iSortingCols=1&iSortCol_0=1&sSortDir_0=desc'),
        ('get_dt', '/sources?iSortingCols=1&iSortCol_0=1&sSortDir_0=desc'),
        ('get_dt', '/values?ftype=primary&iSortingCols=1&iSortCol_0=1'),
        ('get_dt', '/values?parameter=1&iSortingCols=1&iSortCol_0=0&sSearch_0=sra'),
        ('get_dt', '/values?language=2&iSortingCols=1&iSortCol_0=4&sSearch_4=sra'),
        ('get_dt', '/values?language=1'),
        (
            'get_dt',
            '/contributions?iSortingCols=1&iSortCol_0=0&sSortDir_0=desc&sSearch_0=a'),
        ('get_dt', '/values?parameter=2&iSortingCols=1&iSortCol_0=2'),
        ('get_dt', '/values?parameter=1'),
        ('get_html', '/parameters/2'),
        ('get_html', '/valuesets/7-2'),
        ('get', '/parameters/132.md.ris'),
        ('get', '/parameters/132.md.txt'),
        ('get_html', '/valuesets/2-132'),
        ('get_html', '/valuesets/2-309'),
        ('get_html', '/languages/74.snippet.html?parameter=xxxx'),
        ('get_html', '/languages/1.snippet.html?parameter=1'),
        ('get_xml', '/parameters/192.rdf'),
    ])
def test_pages(app, method, path):
    getattr(app, method)(path)


def test_wals(app):
    app.get('/wals/9', status=404)
