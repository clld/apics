from setuptools import setup, find_packages

requires = [
    'clld>=0.28',
    'clldmpg',
    'requests',
]

tests_require = [
    'WebTest >= 1.3.1', # py3 compat
    'mock',
    'selenium',
    'psycopg2',
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
      tests_require=tests_require,
      test_suite="apics",
      entry_points="""\
      [paste.app_factory]
      main = apics:main
      """,
      )
