from path import path

from clld.tests.util import TestWithApp

import apics


class Tests(TestWithApp):
    __cfg__ = path(apics.__file__).dirname().joinpath('..', 'development.ini').abspath()
    __setup_db__ = False

    def test_home(self):
        res = self.app.get('/', status=200)

    def test_resources(self):
        for rsc, id_, index in [
            ('language', '1', True),
            ('contributor', 'abohenocho', True),
            ('contribution', '1', True),
            ('parameter', 'compt', True),
            ('valueset', '1-compt', True),
        ]:
            if id_:
                res = self.app.get('/%ss/%s' % (rsc, id_), headers={'accept': 'text/html'}, status=200)
            if index:
                res = self.app.get('/%ss' % rsc, headers={'accept': 'text/html'}, status=200)

                headers = {'x-requested-with': 'XMLHttpRequest'}
                _path = '/%ss?sEcho=1&iSortingCols=1&iSortCol_0=1&sSortDir_0=desc' % rsc
                res = self.app.get(_path, headers=headers, status=200)

        headers = {'x-requested-with': 'XMLHttpRequest'}
        _path = '/values?sEcho=1&iSortingCols=1&iSortCol_0=1&sSortDir_0=desc'
        res = self.app.get(_path, headers=headers, status=200)
