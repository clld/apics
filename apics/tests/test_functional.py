from path import path

from clld.tests.util import TestWithApp

import apics


class Tests(TestWithApp):
    __cfg__ = path(apics.__file__).dirname().joinpath('..', 'development.ini').abspath()
    __setup_db__ = False

    def test_home(self):
        self.app.get('/', status=200)
        self.app.get('/', accept='text/html', status=200)

    def test_wals_index(self):
        self.app.get('/wals', status=200)
        self.app.get('/wals?sEcho=1', xhr=True, status=200)

    def test_wals(self):
        self.app.get('/wals/1', status=200)

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
                self.app.get('/%ss/%s' % (rsc, id_), accept='text/html', status=200)
                if rsc == 'parameter':
                    self.app.get('/%ss/%s.geojson' % (rsc, id_), status=200)
            if index:
                self.app.get('/%ss' % rsc, accept='text/html', status=200)

                _path = '/%ss?sEcho=1&iSortingCols=1&iSortCol_0=1&sSortDir_0=desc' % rsc
                self.app.get(_path, xhr=True, status=200)

        _path = '/values?sEcho=1&iSortingCols=1&iSortCol_0=1&sSortDir_0=desc'
        self.app.get(_path, xhr=True, status=200)

    def test_datatables(self):
        for path, query in [
            ('contributions', 'iSortingCols=1&iSortCol_0=0&sSortDir_0=desc&sSearch_0=a'),
            ('values', 'parameter=2&iSortingCols=1&iSortCol_0=2'),
            ('values', 'parameter=1'),
        ]:
            self.app.get('/%s?sEcho=1&%s' % (path, query), xhr=True, status=200)

    def test_non_default_parameter(self):
        self.app.get('/parameters/2', accept='text/html', status=200)
        self.app.get('/valuesets/7-2', accept='text/html', status=200)

    def test_misc(self):
        self.app.get('/parameters/132.md.ris', status=200)
        self.app.get('/valuesets/2-132', accept='text/html', status=200)
