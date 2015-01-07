from setuptools import setup, find_packages

requires = [
    'clld>=0.15.5',
    'clldmpg',
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'zope.sqlalchemy',
    'waitress',
    'requests',
    ]

setup(name='apics',
      version='0.0',
      description='apics',
      long_description='',
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="apics",
      entry_points="""\
      [paste.app_factory]
      main = apics:main
      """,
      )
