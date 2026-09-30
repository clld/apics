# Releasing APiCS Online

- Clone and install the app from source:
  ```shell
  git clone https://github.com/clld/apics
  cd apics
  pip install -e .[test]
  ```
- check out the latest release of cldf-datasets/apics
- run
  ```shell
  clld initdb --cldf ../apics-cldf/cldf/StructureDataset-metadata.json development.ini
  ```
- run the tests
  ```shell
  pytest
  ```
- release the app software
- deploy
- Store the tested requirements:
  ```shell
  pip freeze > requirements.txt
  ```
- Store a db dump:
  ```shell
  pg_dump -xO apics > apics.sql
  zip apics.sql.zip apics.sql
  rm apics.sql
  ```

