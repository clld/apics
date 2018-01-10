from setuptools import setup, find_packages


setup(
    name='apics',
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
    install_requires=[
        "clld~=4.0",
        "clldmpg~=3.1",
        "clldutils~=2.0",
        "csvw~=1.0",
        "BeautifulSoup4",
        "waitress",
    ],
    extras_require={
        'dev': ['flake8', 'waitress', 'psycopg2'],
        'test': [
            'tox',
            'mock',
            'pytest>=3.1',
            'pytest-clld',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
            'selenium',
            'zope.component>=3.11.0',
        ],
    },
    test_suite="apics",
    entry_points="""\
    [paste.app_factory]
    main = apics:main
""")
