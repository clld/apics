from clldutils.jsonlib import load
from clldutils.path import Path


for d in ['Atlas', 'Surveys']:
    for f in Path('apics/static').joinpath(d).glob('*.json'):
        try:
            load(f)
        except:
            print(f)
            raise

