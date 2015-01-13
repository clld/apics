# coding: utf8
from clld.scripts.util import parsed_args
from clld.util import jsondump
from clld.lib.fmpxml import Client


def main(args):
    client = Client(args.host, 'apics_data', args.user, args.password)

    for layout, table in [
        ('lect_description_references', 'Lect_description_references'),
        ('lect_descriptions', 'Lect_descriptions'),
        ('colours', 'Colours'),
        ('contributors', 'Contributors'),
        ("data (editors' layout)", 'Data'),
        ("data (apics-wals)", 'wals'),
        ("data references", "Data_references"),
        ("editors", "Editors"),
        ("examples", "ExamplesB"),
        ("examples (editors' layout)", "Examples"),
        ("feature references", "Feature_references"),
        ("features (publication)", "Featuresp"),
        ("features (value names)", "Featuresv"),
        ("features", "Features"),
        ("language references", "Language_references"),
        ("languages (editors' layout)", "Languages"),
        ("people", "People"),
        ("references", "References"),
        ("segment data (editors' layout)", "Segment_data"),
        ("segment data", "Segment_dataB"),
        ('segment features', 'Segment_features'),
        ("sociolinguistic data", "Sociolinguistic_data"),
        ("sociolinguistic data references", "Sociolinguistic_data_references"),
        ("sociolinguistic features", "Sociolinguistic_features"),
        ("value examples", "Value_examples"),
    ]:
        jsondump(client.get(layout), args.data_file('fm', '%s.json' % table))


if __name__ == '__main__':
    main(parsed_args((("host",), {}), (("user",), {}), (("password",), {})))
