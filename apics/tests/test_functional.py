from __future__ import print_function, unicode_literals

from clldutils.path import Path
from clld.tests.util import TestWithApp

import apics


class Tests(TestWithApp):
    __cfg__ = Path(apics.__file__).parent.joinpath('..', 'development.ini').resolve()

    def test_home(self):
        self.app.get_html('/')
        self.app.get_html('/credits')
        self.app.get_html('/help')
        self.app.get('/void.cldf.csv')

    def test_wals_index(self):
        self.app.get_html('/wals')
        self.app.get_dt('/wals')

    def test_wals(self):
        self.app.get_html('/wals/1')
        self.app.get('/wals/9', status=404)

    def test_resources(self):
        for rsc, id_, index in [
            ('language', '2', True),
            ('contributor', 'abohenocho', True),
            ('contribution', '2', True),
            ('parameter', '1', True),
            ('parameter', '102', True),
            ('valueset', '73-102', True),
            ('valueset', '1-1', True),
            ('source', '483', True),
        ]:
            if id_:
                self.app.get_html('/%ss/%s' % (rsc, id_))
                if rsc == 'parameter':
                    self.app.get_json('/%ss/%s.geojson' % (rsc, id_))
            if index:
                self.app.get_html('/%ss' % rsc)

                _path = '/%ss?iSortingCols=1&iSortCol_0=1&sSortDir_0=desc' % rsc
                self.app.get_dt(_path)

    def test_values(self):
        self.app.get_dt('/values?ftype=primary&iSortingCols=1&iSortCol_0=1')
        self.app.get_dt('/values?parameter=1&iSortingCols=1&iSortCol_0=0&sSearch_0=sra')
        self.app.get_dt('/values?language=2&iSortingCols=1&iSortCol_0=4&sSearch_4=sra')
        self.app.get_dt('/values?language=1')

    def test_datatables(self):
        for _path, query in [
            ('contributions', 'iSortingCols=1&iSortCol_0=0&sSortDir_0=desc&sSearch_0=a'),
            ('values', 'parameter=2&iSortingCols=1&iSortCol_0=2'),
            ('values', 'parameter=1'),
        ]:
            self.app.get_dt('/%s?%s' % (_path, query))

    def test_non_default_parameter(self):
        self.app.get_html('/parameters/2')
        self.app.get_html('/valuesets/7-2')

    def test_misc(self):
        self.app.get_xml('/parameters/192.rdf')
        self.app.get('/parameters/132.md.ris')
        self.app.get('/parameters/132.md.txt')
        self.app.get_html('/valuesets/2-132')
        self.app.get_html('/valuesets/2-309')
        self.app.get_html('/languages/74.snippet.html?parameter=xxxx')
        self.app.get_html('/languages/1.snippet.html?parameter=1')
