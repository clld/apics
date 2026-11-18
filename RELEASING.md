# Releasing APiCS Online

Clone and install the app from source:
```shell
git clone https://github.com/clld/apics
git clone --branch v2013.1 --depth 1 https://github.com/cldf-datasets/apics apics-cldf
git clone --branch v2.3.1 --depth 1 https://github.com/cldf-clts/clts
cd apics
pip install -e .[test]
```
check out the latest release of cldf-datasets/apics
run
```shell
clld initdb --cldf ../apics-cldf/cldf/StructureDataset-metadata.json development.ini
```
run the tests
```shell
pytest
```
Store the tested requirements:
```shell
pip freeze > requirements.txt
```
Store a db dump:
```shell
pg_dump -xO --compress gzip:9 apics > apics.sql.gz
```

