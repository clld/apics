from fabric.api import task, hosts
from fabric.contrib.console import confirm

from clld.deploy import config, util


APP = config.APPS['apics']


@hosts('forkel@cldbstest.eva.mpg.de')
@task
def deploy_test():
    util.deploy(APP, 'test')


@hosts('robert@vmext24-203.gwdg.de')
@task
def deploy():
    util.deploy(APP, 'production')


@hosts('robert@vmext24-203.gwdg.de')
@task
def create_downloads():
    util.create_downloads(APP)
