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
        'clld>=9.2.2',
        'clldmpg>=4.2',
        'clldutils',
        'pyclts>=2.1.1',
        'csvw>=1.0',
        'sqlalchemy',
        'BeautifulSoup4',
        'waitress',
    ],
    extras_require={
        'dev': [
            'flake8',
            'tox',
            'bs4',
        ],
        'test': [
            'mock',
            'psycopg2',
            'pytest>=3.1',
            'pytest-clld>=0.4',
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
