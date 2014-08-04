APiCS Online
============

Cite
----

APiCS Online is licensed under a Creative Commons Attribution 3.0 Unported License. Cite as

  Michaelis, Susanne Maria & Maurer, Philippe & Haspelmath, Martin & Huber, Magnus (eds.) 2013.
  Atlas of Pidgin and Creole Language Structures Online.
  Leipzig: Max Planck Institute for Evolutionary Anthropology.
  (Available online at http://apics-online.info) 
  [![DOI](https://zenodo.org/badge/5142/clld/apics.png)](http://dx.doi.org/10.5281/zenodo.11135)


Install
-------

To get APiCS Online running locally, you need python 2.7 and have to run your system's equivalent to the following bash commands:

```bash
virtualenv --no-site-packages apics
cd apics/
. bin/activate
curl -O http://zenodo.org/record/11135/files/apics-v2013.zip
unzip apics-v2013.zip
python clld-apics-1a306df/fromdump.py
cd apics/
pip install -r requirements.txt
python setup.py develop
python apics/scripts/unfreeze.py sqlite.ini
pserve sqlite.ini
```

Then you should be able to access the application by visiting http://localhost:6543 in your browser. Note that you still need an internet connection for the application to download external resources like the map tiles or javascript libraries.
