from clld.web.assets import environment
from clldutils.path import Path

import apics


environment.append_path(
    Path(apics.__file__).parent.joinpath('static').as_posix(), url='/apics:static/')
environment.load_path = list(reversed(environment.load_path))
