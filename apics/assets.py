import pathlib

from clld.web.assets import environment

import apics


environment.append_path(
    str(pathlib.Path(apics.__file__).parent.joinpath('static')), url='/apics:static/')
environment.load_path = list(reversed(environment.load_path))
