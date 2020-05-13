from clld.db.meta import DBSession
from clld.db.models.common import Config


def about(ctx, req):
    return {'html': DBSession.query(Config).filter(Config.key=='intro').one().value}
