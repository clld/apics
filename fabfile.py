from fabric.api import task, hosts
from fabric.contrib.console import confirm

from clld.deploy import config, util


APP = config.APPS['apics']


#@hosts('forkel@cldbstest.eva.mpg.de')
@hosts('robert@vmext24-203.gwdg.de')
@task
def deploy_test():
    util.deploy(APP, 'test')


@task
def deploy():
    util.deploy(APP, 'production')
