from path import path

from clld.tests.util import TestWithApp

import apics


class Tests(TestWithApp):
    __cfg__ = path(apics.__file__).dirname().joinpath('..', 'development.ini').abspath()
    __setup_db__ = False

    def test_home(self):
        self.app.get('/', status=200)

    def test_resources(self):
        for rsc, id_, index in [
            ('language', '1', True),
            ('contributor', 'abohenocho', True),
            ('contribution', '1', True),
            ('parameter', '1', True),
            ('valueset', '1-1', True),
            ('source', '483', True),
        ]:
            if id_:
                self.app.get('/%ss/%s' % (rsc, id_),
                             headers={'accept': 'text/html'}, status=200)
            if index:
                self.app.get('/%ss' % rsc, headers={'accept': 'text/html'}, status=200)

                headers = {'x-requested-with': 'XMLHttpRequest'}
                _path = '/%ss?sEcho=1&iSortingCols=1&iSortCol_0=1&sSortDir_0=desc' % rsc
                self.app.get(_path, headers=headers, status=200)

        headers = {'x-requested-with': 'XMLHttpRequest'}
        _path = '/values?sEcho=1&iSortingCols=1&iSortCol_0=1&sSortDir_0=desc'
        self.app.get(_path, headers=headers, status=200)

    def test_datatables(self):
        headers = {'x-requested-with': 'XMLHttpRequest'}

        for path, query in [
            ('contributions', 'iSortingCols=1&iSortCol_0=0&sSortDir_0=desc&sSearch_0=a'),
            ('values', 'parameter=2&iSortingCols=1&iSortCol_0=2'),
            ('values', 'parameter=1'),
        ]:
            self.app.get('/%s?sEcho=1&%s' % (path, query), headers=headers, status=200)

    def test_non_default_parameter(self):
        self.app.get('/parameters/2', headers={'accept': 'text/html'}, status=200)
        self.app.get('/valuesets/7-2', headers={'accept': 'text/html'}, status=200)
