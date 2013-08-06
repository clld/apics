from clld.web.assets import environment
from path import path

import apics


environment.append_path(
    path(apics.__file__).dirname().joinpath('static'), url='/apics:static/')
environment.load_path = list(reversed(environment.load_path))
